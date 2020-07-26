import pandas as pd
import numpy as np
import scipy.optimize as sopt
import scipy.constants as sconst

import os
import sys

from pathlib import Path

gamma = sconst.physical_constants["electron gyromag. ratio"][0]
gamma_GHZ = float(
    sconst.physical_constants["electron gyromag. ratio in MHz/T"][0])/1000


def fitfunc_kittel(h, Meff):
    """
    面内に磁場をかけた時のKittelの式．

     Parameters
    ----------
    h : 印加磁場 (mT)
    gamma : 磁気回転比
    Meff : 有効磁化
     Output
    ---------
    frequency (GHz)
    """
    return gamma_GHZ * np.sqrt(h / 1000 * (h / 1000 + Meff))


def fitfunc_line(x, a, b):
    return a * x + b


class KittelLineFittingCore():
    thickness_dep_file = ""
    curve_fitting_file = ""

    def __init__(self):
        base = os.path.dirname(os.path.abspath(__file__))
        name = os.path.normpath(os.path.join(
            base, '../setting/settings.json'))
        self.curve_fitting_file = pd.read_json(
            name).at["curve_fitting_file", "file_name"]
        self.thickness_dep_file = pd.read_json(
            name).at["thickness_dep_file", "file_name"]

    def fitting(self, dir, theta, d_f, d_n):
        df = pd.read_csv(str(dir) + "/" +
                         self.curve_fitting_file)
        df = df.set_index(["range_type"], drop=True)
        df_result = pd.DataFrame(index=[],
                                 columns=['range_type', 'M_eff', 'damping', 'W0', 'theta', 'df', 'dn'])

        for range_type, init_M in [["negative", -0.500], ["positive", 0.500]]:
           # load csv
            df_val = df.loc[(range_type)]
            h_res = df_val["h_res"].tolist()
            freq = df_val["frequency"].tolist()
            lw = df_val["linewidth"].tolist()

            print(h_res)
            print(freq)
            print(lw)

            # Kittel fitting
            para_ini_kittel = [init_M]
            [para_opt_kittel, cov] = sopt.curve_fit(
                fitfunc_kittel, h_res, freq, para_ini_kittel)

            # linewidth fitting
            para_ini_line = [2, 0.1]
            [para_opt_line, cov] = sopt.curve_fit(
                fitfunc_line, freq, lw, para_ini_line)

            # 線幅の単位はmT
            alpha = (para_opt_line[0] * gamma_GHZ)/1000

            df_result = df_result.append(
                {"range_type": range_type, "M_eff": para_opt_kittel[0], 'damping': alpha, 'W0': para_opt_line[1], 'theta': theta, 'df': d_f, 'dn': d_n}, ignore_index=True)
        print(df_result)
        df_result.to_csv(str(dir) + "/" +
                         self.thickness_dep_file)
        return 0


if __name__ == "__main__":
    kittelline_fitting = KittelLineFittingCore()
    kittelline_fitting.fitting(
        sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
