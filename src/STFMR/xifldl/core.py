import glob
import os

import pandas as pd
import scipy.constants as sconst
import scipy.optimize as sopt
import numpy as np
import matplotlib.pyplot as plt


from rootcommand import CommonOption, RootCommand
from uroboros import Command
from uroboros.constants import ExitStatus

from setting import *


class XiFLDLFitting(Command):
    """Sub command of stfmr"""
    name = 'xifldl'
    options = [CommonOption()]

    short_description = 'Calculate xi_FL and xi_DL for multiple samples'
    long_description = 'Calculate and output xi_DL and xi_FL.'

    def run(self, args):
        d_f = {
            'negative': [],
            'positive': []
        }
        d_n = {
            'negative': [],
            'positive': []
        }
        xi_FMR_inv = {
            'negative': [],
            'positive': []
        }
        df_satmag = pd.read_csv(str(args.dir) + "/" +
                                satmag_result_file)
        df_satmag = df_satmag.set_index(["range_type"], drop=True)
        folder_list = glob.glob(str(args.dir) + '/**/')
        for folders in folder_list:
            thick_result = folders + thickness_dep_file
            curve_result = folders + curve_fitting_file
            if os.path.isfile(thick_result) and os.path.isfile(curve_result):
                print(folders)
                df_thick = pd.read_csv(thick_result)
                df_thick = df_thick.set_index(["range_type"], drop=True)
                df_curve = pd.read_csv(curve_result)
                df_curve = df_curve.set_index(["range_type"], drop=True)
                for range_type in ['negative', "positive"]:
                    d_f[range_type].append(
                        df_thick.loc[range_type]['df'] * 1e-9)
                    d_n[range_type].append(
                        df_thick.loc[range_type]['dn'] * 1e-9)
                    xi_FMR_inv[range_type].append(
                        1 / df_thick.loc[range_type]['xi_FMR_ave'])
        for range_type in ['negative', "positive"]:
            M_s = df_satmag.loc[range_type]['M_s']

            d_arr = (1/(np.array(d_f[range_type]) *
                        np.array(d_n[range_type]))).tolist()
            para_ini = [0.01, 0.01]
            print(xi_FMR_inv[range_type])
            print(M_s)
            print(d_arr)

            Fontsize = 12
            plt.plot(d_arr, xi_FMR_inv[range_type],
                     marker='.', linewidth=0, label=range_type)

            def fitfunc_xifmr(d_inv, xi_DL, xi_FL):
                return (1 + sconst.hbar * xi_FL / (sconst.elementary_charge * M_s)) * d_inv / xi_DL

            para, _ = sopt.curve_fit(
                fitfunc_xifmr, d_arr, xi_FMR_inv[range_type], para_ini)
            df_satmag.at[range_type, 'xi_DL'] = para[0]
            df_satmag.at[range_type, 'xi_FL'] = para[1]
        df_satmag.to_csv(str(args.dir) + "/" +
                         satmag_result_file)
        plt.legend(bbox_to_anchor=(0, 1), loc='upper left',
                   borderaxespad=0, fontsize=Fontsize)
        plt.xticks(fontsize=Fontsize)
        plt.yticks(fontsize=Fontsize)
        plt.grid(True)
        plt.title("xi_FMR vs thickness")
        plt.xlabel('1/df*dn (m^-2)', fontsize=Fontsize)
        plt.ylabel('xi FMR^-1', fontsize=Fontsize)
        plt.savefig(str(args.dir) +
                    "/xi_FMR_result.png")

        return ExitStatus.SUCCESS
