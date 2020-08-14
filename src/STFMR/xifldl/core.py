import glob
import os
import sys

import pandas as pd
import scipy.constants as sconst
import scipy.optimize as sopt
import numpy as np
import matplotlib.pyplot as plt


class XiFLDLFittingCore():
    curve_fitting_file = ''
    thickness_dep_file = ''
    satmag_result_file = ''
    Fontsize = 12
    d_f = {
        'negative': [],
        'positive': []
    }
    d_n = {
        'negative': [],
        'positive': []
    }
    xi_FMR_inv_val = {
        'negative': [],
        'positive': []
    }
    xi_FMR_inv_std = {
        'negative': [],
        'positive': []
    }
    xi_FL_val = {
        'negative': [],
        'positive': []
    }

    xi_FL_std = {
        'negative': [],
        'positive': []
    }
    xi_DL_val = {
        'negative': [],
        'positive': []
    }

    xi_DL_std = {
        'negative': [],
        'positive': []
    }

    def __init__(self):
        base = os.path.dirname(os.path.abspath(__file__))
        name = os.path.normpath(os.path.join(
            base, '../setting/settings.json'))
        self.curve_fitting_file = pd.read_json(
            name).at['curve_fitting_file', 'file_name']
        self.thickness_dep_file = pd.read_json(
            name).at['thickness_dep_file', 'file_name']
        self.satmag_result_file = pd.read_json(
            name).at['satmag_result_file', 'file_name']

    def fitting(self, dir):
        print("Running XiFLDL fitting...")
        df_satmag = pd.read_csv(str(dir) + '/' +
                                self.satmag_result_file)
        df_satmag = df_satmag.set_index(['range_type', 'val_type'], drop=True)
        folder_list = glob.glob(str(dir) + '/**/')
        for folders in folder_list:
            thick_result = folders + self.thickness_dep_file
            curve_result = folders + self.curve_fitting_file
            if os.path.isfile(thick_result) and os.path.isfile(curve_result):
                print(folders)
                df_thick = pd.read_csv(thick_result)
                df_thick = df_thick.set_index(
                    ['range_type', 'val_type'], drop=True)
                curve_df = pd.read_csv(curve_result)
                curve_df = curve_df.set_index(
                    ['range_type', 'val_type'], drop=True)
                for range_type in ['negative', 'positive']:
                    curve_val_df = curve_df.loc[(range_type, 'val')]
                    curve_std_df = curve_df.loc[(range_type, 'std')]
                    # ここの処理はちょっと怪しい
                    xi_FMR_ave = np.average(curve_val_df['xi_FMR'])
                    xi_FMR_std = np.sqrt(np.average(curve_std_df['xi_FMR']**2))
                    self.d_f[range_type].append(
                        float(df_thick.loc[range_type, 'val']['df']) * 1e-9)
                    self.d_n[range_type].append(
                        float(df_thick.loc[range_type, 'val']['dn']) * 1e-9)
                    self.xi_FMR_inv_val[range_type].append(
                        1 / float(xi_FMR_ave))
                    self.xi_FMR_inv_std[range_type].append(
                        float(xi_FMR_std) / (float(xi_FMR_ave) ** 2))

        for range_type in ['negative', 'positive']:
            M_s = df_satmag.loc[(range_type, 'val')]['M_s']

            d_arr = (1/(np.array(self.d_f[range_type]) *
                        np.array(self.d_n[range_type]))).tolist()
            para_ini = [0.01, 0.01]
            Fontsize = 12

            def fitfunc_xifmr(d_inv, xi_DL, xi_FL):
                return (1 + sconst.hbar * xi_FL * d_inv / (sconst.elementary_charge * M_s)) / xi_DL

            para_xifldl_ndarr, cov_xifldl_ndarr = sopt.curve_fit(
                fitfunc_xifmr, d_arr, self.xi_FMR_inv_val[range_type], para_ini)
            err_xifldl_ndarr = np.sqrt(np.diag(cov_xifldl_ndarr))
            self.xi_DL_val[range_type] = df_satmag.at[(
                range_type, 'val'), 'xi_DL'] = para_xifldl_ndarr[0]
            self.xi_FL_val[range_type] = df_satmag.at[(
                range_type, 'val'), 'xi_FL'] = para_xifldl_ndarr[1]
            self.xi_DL_std[range_type] = df_satmag.at[(
                range_type, 'std'), 'xi_DL'] = err_xifldl_ndarr[0]
            self.xi_FL_std[range_type] = df_satmag.at[(
                range_type, 'std'), 'xi_FL'] = err_xifldl_ndarr[1]
        df_satmag.to_csv(str(dir) + '/' +
                         self.satmag_result_file)

    def plot(self, dir):
        for range_type in ['negative', 'positive']:
            d_arr = (1/(np.array(self.d_f[range_type]) *
                        np.array(self.d_n[range_type]))).tolist()
            plt.errorbar(
                d_arr, self.xi_FMR_inv_val[range_type], yerr=self.xi_FMR_inv_std[range_type], linestyle='None', linewidth=2.0, capsize=3, label=range_type)
            plt.plot([], [], linewidth=0, label='xi_FL={0:.4e}±{1:.1e} ({2})'.format(
                self.xi_FL_val[range_type], self.xi_FL_std[range_type], range_type))
            plt.plot([], [], linewidth=0, label='xi_DL={0:.4e}±{1:.1e} ({2})'.format(
                self.xi_DL_val[range_type], self.xi_DL_std[range_type], range_type))
        plt.rcParams['legend.loc'] = 'best'
        plt.rcParams['legend.frameon'] = True
        plt.legend()
        plt.xticks(fontsize=self.Fontsize)
        plt.yticks(fontsize=self.Fontsize)
        plt.grid(True)
        plt.title('xi_FMR vs thickness')
        plt.xlabel('1/df*dn (m^-2)', fontsize=self.Fontsize)
        plt.ylabel('xi FMR^-1', fontsize=self.Fontsize)
        plt.savefig(str(dir) +
                    '/xi_FMR_result.png')


if __name__ == '__main__':
    xiflfl_fitting = XiFLDLFittingCore()
    xiflfl_fitting.fitting(sys.argv[1])
    xiflfl_fitting.plot(sys.argv[1])
    pass
