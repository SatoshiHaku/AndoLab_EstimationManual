import glob
import os
import sys

import numpy as np
import scipy.optimize as sopt
import scipy.constants as sconst
import pandas as pd


def fitfunc_satmag(x, M_s, K_s):
    return M_s + K_s*x/(sconst.mu_0*M_s)


class MagnetizationFittingCore():
    thickness_dep_file = ''

    def __init__(self):
        base = os.path.dirname(os.path.abspath(__file__))
        name = os.path.normpath(os.path.join(
            base, '../setting/settings.json'))
        self.thickness_dep_file = pd.read_json(
            name).at['thickness_dep_file', 'file_name']
        self.satmag_result_file = pd.read_json(
            name).at['satmag_result_file', 'file_name']
        pass

    def fitting(self, dir):
        print("Running saturation magnetization fitting...")
        file_list = glob.glob(str(dir) + '/**/' + self.thickness_dep_file)
        df_list = []
        for files in file_list:
            df_list.append(pd.read_csv(files))
        df = pd.concat(df_list, sort=False)
        df = df.set_index(['range_type', 'val_type'], drop=True)
        df_result = pd.DataFrame(index=[],
                                 columns=['range_type', 'val_type', 'M_s', 'K_s'])
        for range_type in ['negative', 'positive']:
           # load csv
            df_val = df.loc[range_type, 'val']
            df_std = df.loc[range_type, 'std']

            M_eff = df_val['M_eff']
            d_f = df_val['df']

            # Saturation magnetization fitting
            para_ini_satmag = [0.500, 3*10**(-10)]
            para_satmag_ndarr, cov_satmag_ndarr = sopt.curve_fit(
                fitfunc_satmag, d_f, M_eff, para_ini_satmag)
            err_satmag_ndarr = np.sqrt(np.diag(cov_satmag_ndarr))
            df_result = df_result.append(
                {'range_type': range_type, 'val_type': 'val', 'M_s': para_satmag_ndarr[0], 'K_s': para_satmag_ndarr[1]*10**9}, ignore_index=True)
            df_result = df_result.append(
                {'range_type': range_type, 'val_type': 'std', 'M_s': err_satmag_ndarr[0], 'K_s': err_satmag_ndarr[1]*10**9}, ignore_index=True)

        df_result.to_csv(str(dir) + '/' +
                         self.satmag_result_file, index=False)

        return 0


if __name__ == '__main__':
    magnetization_fitting = MagnetizationFittingCore()
    magnetization_fitting.fitting(sys.argv[1])
