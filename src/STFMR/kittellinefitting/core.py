import pandas as pd
import numpy as np
import scipy.optimize as sopt
import scipy.constants as sconst
import os
from pathlib import Path

from setting import *
from rootcommand import CommonOption, RootCommand
from uroboros import Command
from uroboros.constants import ExitStatus

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


class KittelLineFitting(Command):
    """Sub command of stfmr"""
    name = 'kittelline'
    options = [CommonOption()]

    short_description = 'Kittel & linewidth fitting for a single sample'
    long_description = 'Calculate Kittel & linewidth fitting and outputs effective magnetization, damping coefficient, and W0.'

    def build_option(self, parser):
        """
        引数の追加．
        """
#        parser.add_argument('output', type=Path,
#                            help="Directory to save the result data")
        parser.add_argument('theta', type=float,
                            help="Angle (deg) of the applied magnetic field (in-plane)")
        parser.add_argument('df', type=float,
                            help="Thickness (nm) of the ferromagnet")
        parser.add_argument('dn', type=float,
                            help="Thickness (nm) of the nonmagnet")
        # 追加した後にparserを返す
        return parser

    def run(self, args):
        df = pd.read_csv(str(args.dir) + "/" +
                         curve_fitting_file)
        df = df.set_index(["range_type"], drop=True)
        df_result = pd.DataFrame(index=[],
                                 columns=['range_type', 'M_eff', 'damping', 'W0', 'theta', 'df', 'dn'])

        for range_type, init_M in [["negative", -0.500], ["positive", 0.500]]:
           # load csv
            df_val = df.loc[(range_type)]
            h_res = df_val["h_res"].values.tolist()
            freq = df_val["frequency"].values.tolist()
            lw = df_val["linewidth"].values.tolist()

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
                {"range_type": range_type, "M_eff": para_opt_kittel[0], 'damping': alpha, 'W0': para_opt_line[1], 'theta': args.theta, 'df': args.df, 'dn': args.dn}, ignore_index=True)
        df_result.to_csv(str(args.dir) + "/" +
                         thickness_dep_file, index=False)
        print(df_result)
        return ExitStatus.SUCCESS
