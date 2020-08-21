
import scipy.optimize as sopt
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd

import sys
import glob
import re
import json
import os
import math

# 正側と負側のフィッティング範囲
fitting_range = {
    'positive': list(range(610, 1190)),
    'negative': list(range(10, 590))
}
Fontsize = 10


def fitfunc_curve(h, hr, s, a, w, c, d):
    '''
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
        '''
    return s * w * w / ((h - hr) * (h - hr) + w * w) + a * w * (h - hr) / ((h - hr)*(h - hr) + w*w) + c*h + d


class CurveFittingCore():
    file_list = []
    columns = ['range_type', 'val_type', 'frequency', 'h_res', 'sym',
               'asym', 'linewidth', 'slope', 'bias', 'S/A']
    curve_fitting_file = ''

    def __init__(self):
        base = os.path.dirname(os.path.abspath(__file__))
        name = os.path.normpath(os.path.join(
            base, '../setting/settings.json'))
        self.curve_fitting_file = pd.read_json(
            name).at['curve_fitting_file', 'file_name']

    def file_parser(self, foldername):
        filename = glob.glob(foldername + '/*lvm')  # lvmファイルがあるフォルダー内のファイル名を取得

        for i, filename in enumerate(filename):
            # ファイル名から周波数部分だけ抽出
            pat = r'[0-9]+\.[0-9]+'  # 抽出するパターン：数字
            num_list = re.findall(pat, filename)  # 数字を抽出してリスト化
            fre = float(num_list[0])
            self.file_list.append([fre, filename])
        self.file_list.sort(key=lambda x: x[0])

    def fitting(self, dir):
        print("Running curve fitting...")
        foldername = str(dir)
        self.file_parser(foldername)
        plt.figure()
        result_df = pd.DataFrame([], columns=self.columns)
        print('Target files:')
        for fre, filename in self.file_list:
            print(filename)
            raw_df = pd.read_table(filename, names=['MF', 'Vol'])
            x = raw_df['MF']
            y = raw_df['Vol']
            plt.plot(x, y, linewidth=2.0, label=str(fre) + ' GHz')
            for [range_type, fre_slope, fre_bias] in [['positive', 17, -17], ['negative', -17, 17]]:
                para_ini = [fre_slope * fre +
                            fre_bias, 1.0, 1.0, 5.0, 1.0, 1.0]
                x_ = x[fitting_range.get(range_type)]
                y_ = y[fitting_range.get(range_type)]
                # フィッティングパラメータの最適化
                para_ndarr, cov_ndarr = sopt.curve_fit(
                    fitfunc_curve, x_, y_, para_ini)
                err_ndarr = np.sqrt(np.diag(cov_ndarr))
                # ratio of sym to asym
                sym_val = para_ndarr[1]
                sym_std = err_ndarr[1]
                asym_val = para_ndarr[2]
                asym_std = err_ndarr[2]
                # fitting results
                ratio_val = sym_val/asym_val
                ratio_std = math.sqrt(
                    (sym_std/asym_val)**2+(sym_val*asym_std/(asym_val**2))**2)
                val_series = pd.Series(
                    [range_type, 'val', fre] + para_ndarr.tolist()+[ratio_val], index=result_df.columns)
                result_df = result_df.append(val_series, ignore_index=True)
                val_series = pd.Series(
                    [range_type, 'std', 0] + err_ndarr.tolist()+[ratio_std], index=result_df.columns)
                result_df = result_df.append(val_series, ignore_index=True)

        plt.rcParams['legend.loc'] = 'best'
        plt.rcParams['legend.frameon'] = True
        plt.xticks(fontsize=Fontsize)
        plt.yticks(fontsize=Fontsize)
        plt.grid(True)
        plt.title('Raw Data Plot')
        plt.xlabel('magnetic field (mT)', fontsize=Fontsize)
        plt.ylabel('voltage (V)', fontsize=Fontsize)
        plt.legend()
        plt.savefig(str(dir)+'/raw_data_plot.png', bbox_inches="tight")
        result_df.to_csv(foldername + '/' +
                         self.curve_fitting_file, index=False)
        return 0

    def plot(self, dir):
        self.plot_fitted(dir)
        self.plot_ratio_sym_to_asym(dir)

    def plot_fitted(self, dir):
        df = pd.read_csv(str(dir) + '/' +
                         self.curve_fitting_file, index_col=['range_type', 'val_type'])
        reprod_range = {
            'positive': np.arange(0, 250, 0.5),
            'negative': np.arange(-250, 0, 0.5)
        }
        for range_type in ['negative', 'positive']:
            df_val = df.loc[range_type, 'val']
            plt.figure()
            for index, row in df_val.iterrows():
                h = reprod_range[range_type]
                fre = row.loc['frequency']
                para = row.loc['h_res':'bias'].to_list()
                print(fre)
                v = list(map(lambda x: fitfunc_curve(x, *para), h))
                plt.plot(h, v, linewidth=2.0, label=str(fre) + ' GHz')

            plt.rcParams['legend.loc'] = 'best'
            plt.rcParams['legend.frameon'] = True
            plt.xticks(fontsize=Fontsize)
            plt.yticks(fontsize=Fontsize)
            plt.grid(True)
            plt.title('Curve fitting' + ' (' + range_type + ') ')
            plt.xlabel('magnetic field (mT)', fontsize=Fontsize)
            plt.ylabel('voltage (V)', fontsize=Fontsize)
            plt.legend()
            plt.savefig(str(dir) +
                        '/fitting_result_' + range_type + '.png', bbox_inches="tight")

    def plot_ratio_sym_to_asym(self, dir):
        df = pd.read_csv(str(dir) + '/' +
                         self.curve_fitting_file)
        df = df.set_index(['range_type', 'val_type'], drop=True)
        ratio = {
            'positive': [],
            'negative': []
        }
        std = {
            'positive': [],
            'negative': []
        }
        plt.figure()
        for range_type in ['negative', 'positive']:
            val_df = df.loc[(range_type, 'val')]
            std_df = df.loc[(range_type, 'std')]
            frequency = []
            for [_, val_row], [_, std_row] in zip(val_df.iterrows(), std_df.iterrows()):
                frequency.append(val_row['frequency'])
                ratio[range_type].append(val_row['S/A'])
                std[range_type].append(std_row['S/A'])
            plt.errorbar(
                frequency, ratio[range_type], yerr=std[range_type], linewidth=2.0, capsize=3, label=range_type)

        plt.rcParams['legend.loc'] = 'best'
        plt.rcParams['legend.frameon'] = True
        plt.xticks(fontsize=Fontsize)
        plt.yticks(fontsize=Fontsize)
        plt.grid(True)
        plt.title('Ratio of S to A')
        plt.xlabel('Frequency (GHz)', fontsize=Fontsize)
        plt.ylabel('Ratio', fontsize=Fontsize)
        plt.legend()
        plt.savefig(str(dir) +
                    '/ratio_of_S_to_A.png', bbox_inches="tight")


if __name__ == '__main__':
    curve_fitting = CurveFittingCore()
    curve_fitting.fitting(sys.argv[1])
