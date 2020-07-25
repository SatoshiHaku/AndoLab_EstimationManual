import glob
import os
import sys

import pandas as pd
import scipy.constants as sconst
import scipy.optimize as sopt
import numpy as np
import matplotlib.pyplot as plt


class XiFLDLFittingCore():
    curve_fitting_file = ""
    thickness_dep_file = ""
    satmag_result_file = ""
    Fontsize = 12
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

    def __init__(self):
        base = os.path.dirname(os.path.abspath(__file__))
        name = os.path.normpath(os.path.join(
            base, '../setting/settings.json'))
        self.curve_fitting_file = pd.read_json(
            name).at["curve_fitting_file", "file_name"]
        self.thickness_dep_file = pd.read_json(
            name).at["thickness_dep_file", "file_name"]
        self.satmag_result_file = pd.read_json(
            name).at["satmag_result_file", "file_name"]

    def fitting(self, dir):
        df_satmag = pd.read_csv(str(dir) + "/" +
                                self.satmag_result_file)
        df_satmag = df_satmag.set_index(["range_type"], drop=True)
        folder_list = glob.glob(str(dir) + '/**/')
        for folders in folder_list:
            thick_result = folders + self.thickness_dep_file
            curve_result = folders + self.curve_fitting_file
            if os.path.isfile(thick_result) and os.path.isfile(curve_result):
                print(folders)
                df_thick = pd.read_csv(thick_result)
                df_thick = df_thick.set_index(["range_type"], drop=True)
                df_curve = pd.read_csv(curve_result)
                df_curve = df_curve.set_index(["range_type"], drop=True)
                for range_type in ['negative', "positive"]:
                    self.d_f[range_type].append(
                        float(df_thick.loc[range_type]['df']) * 1e-9)
                    self.d_n[range_type].append(
                        float(df_thick.loc[range_type]['dn']) * 1e-9)
                    self.xi_FMR_inv[range_type].append(
                        1 / float(df_thick.loc[range_type]['xi_FMR_ave']))
        for range_type in ['negative', "positive"]:
            M_s = df_satmag.loc[range_type]['M_s']

            d_arr = (1/(np.array(self.d_f[range_type]) *
                        np.array(self.d_n[range_type]))).tolist()
            para_ini = [0.01, 0.01]
            print(self.xi_FMR_inv[range_type])
            print(M_s)
            print(d_arr)

            Fontsize = 12

            def fitfunc_xifmr(d_inv, xi_DL, xi_FL):
                return (1 + sconst.hbar * xi_FL / (sconst.elementary_charge * M_s) * d_inv) / xi_DL

            para, _ = sopt.curve_fit(
                fitfunc_xifmr, d_arr, self.xi_FMR_inv[range_type], para_ini)
            df_satmag.at[range_type, 'xi_DL'] = para[0]
            df_satmag.at[range_type, 'xi_FL'] = para[1]
        df_satmag.to_csv(str(dir) + "/" +
                         self.satmag_result_file)

    def plot(self, dir):
        for range_type in ['negative', "positive"]:
            d_arr = (1/(np.array(self.d_f[range_type]) *
                        np.array(self.d_n[range_type]))).tolist()
            plt.plot(d_arr, self.xi_FMR_inv[range_type],
                     marker='.', linewidth=0, label=range_type)

        plt.legend(bbox_to_anchor=(0, 1), loc='upper left',
                   borderaxespad=0, fontsize=self.Fontsize)
        plt.xticks(fontsize=self.Fontsize)
        plt.yticks(fontsize=self.Fontsize)
        plt.grid(True)
        plt.title("xi_FMR vs thickness")
        plt.xlabel('1/df*dn (m^-2)', fontsize=self.Fontsize)
        plt.ylabel('xi FMR^-1', fontsize=self.Fontsize)
        plt.savefig(dir +
                    "/xi_FMR_result.png")


if __name__ == "__main__":
    xiflfl_fitting = XiFLDLFittingCore()
    xiflfl_fitting.fitting(sys.argv[1])
    xiflfl_fitting.plot(sys.argv[1])
    pass
