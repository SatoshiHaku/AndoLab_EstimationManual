
import scipy.optimize as sopt
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

import sys
import glob
import re
import json
import os

# 正側と負側のフィッティング範囲
fitting_range = {
    "positive": list(range(610, 1190)),
    "negative": list(range(10, 590))
}
Fontsize = 12


def fitfunc_curve(h, hr, s, a, w, c, d):
    """
        DC電圧の波形の関数．

         Parameters
        ----------
        h : float
            印加磁場
        hr : float
            共鳴磁場
        s : float
            symmetry成分の振幅
        a : float
            antisymmetry成分の振幅
        w : float
            線幅
        c : float
            線型部分の傾き
        d : float
            線型部分の切片
        """
    return s * w * w / ((h - hr) * (h - hr) + w * w) + a * w * (h - hr) / ((h - hr)*(h - hr) + w*w) + c*h + d


class CurveFittingCore():
    file_list = []
    range_type = []
    frequency = []
    h_res = []
    sym = []
    asym = []
    linewidth = []
    slope = []
    bias = []
    columns = ["range_type", "frequency", "h_res", "sym",
               "asym", "linewidth", "slope", "bias"]
    curve_fitting_file = ""

    def __init__(self):
        base = os.path.dirname(os.path.abspath(__file__))
        name = os.path.normpath(os.path.join(
            base, '../setting/settings.json'))
        self.curve_fitting_file = pd.read_json(
            name).at["curve_fitting_file", "file_name"]

    def file_parser(self, foldername):
        filename = glob.glob(foldername + '/*lvm')  # lvmファイルがあるフォルダー内のファイル名を取得

        for i, filename in enumerate(filename):
            # ファイル名から周波数部分だけ抽出
            pat = r'[0-9]+\.[0-9]+'  # 抽出するパターン：数字
            num_list = re.findall(pat, filename)  # 数字を抽出してリスト化
            fre = float(num_list[0])
            self.file_list.append([fre, filename])
        self.file_list.sort(key=lambda x: x[0])

    def curve_fitting(self, fre, filename):
        df = pd.read_table(filename, names=['MF', 'Vol'])
        x = df['MF']
        y = df['Vol']
        for [range_type, fre_slope, fre_bias] in [["positive", 17, -17], ["negative", -17, 17]]:
            para_ini = [fre_slope * fre + fre_bias, 1.0, 1.0, 5.0, 1.0, 1.0]
            x_ = x[fitting_range.get(range_type)]
            y_ = y[fitting_range.get(range_type)]
            # フィッティングパラメータの最適化
            para, _ = sopt.curve_fit(
                fitfunc_curve, x_, y_, para_ini)
            self.range_type += [range_type]
            self.frequency += [fre]
            self.h_res += [para[0]]
            self.sym += [para[1]]
            self.asym += [para[2]]
            self.linewidth += [para[3]]
            self.slope += [para[4]]
            self.bias += [para[5]]
        return 0

    def fitting(self, dir):
        foldername = str(dir)
        self.file_parser(foldername)
        print('Target files:')
        for fre, filename in self.file_list:
            print(filename)
            self.curve_fitting(fre, filename)
        df = pd.DataFrame(
            data={"range_type": self.range_type,
                  "frequency": self.frequency,
                  "h_res": self.h_res,
                  "sym": self.sym,
                  "asym": self.asym,
                  "linewidth": self.linewidth,
                  "slope": self.slope,
                  "bias": self.bias,
                  },
            columns=self.columns
        )
        print(df)
        df.to_csv(foldername + "/" + self.curve_fitting_file, index=False)
        return 0

    def plot(self, dir):
        df = pd.read_csv(str(dir) + "/" +
                         self.curve_fitting_file)
        df = df.set_index(["range_type"], drop=True)
        reprod_range = {
            "positive": np.arange(0, 250, 0.5),
            "negative": np.arange(-250, 0, 0.5)
        }
        for range_type in ["negative", "positive"]:
            df_val = df.loc[(range_type)]
            for index, row in df_val.iterrows():
                h = reprod_range[range_type]
                fre = row.to_list()[0]
                para = row.to_list()[1:7]
                v = list(map(lambda x: fitfunc_curve(x, *para), h))
                plt.plot(h, v, linewidth=2.0)
        plt.xticks(fontsize=Fontsize)
        plt.yticks(fontsize=Fontsize)
        plt.grid(True)
        plt.title("Curve fitting" + " (" + range_type + ") ")
        plt.xlabel('magnetic field (mT)', fontsize=Fontsize)
        plt.ylabel('voltage (V)', fontsize=Fontsize)
        plt.savefig(str(dir) +
                    "/fitting_result.png")


if __name__ == "__main__":
    curve_fitting = CurveFittingCore()
    curve_fitting.fitting(sys.argv[1])
