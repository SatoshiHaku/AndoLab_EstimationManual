import glob
import os
import sys

import pandas as pd
import scipy.constants as sconst
import numpy as np


class XiFMRFittingCore():

    curve_fitting_file = ""
    thickness_dep_file = ""
    satmag_result_file = ""

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
        pass

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
                xi_FMR_list = {
                    'negative': [],
                    'positive': []
                }
                for range_type, M_s in [["negative", df_satmag.at['negative', 'M_s']], ["positive", df_satmag.at['positive', 'M_s']]]:
                    d_f = float(df_thick.at[range_type, 'df'])*1e-9
                    d_n = float(df_thick.at[range_type, 'dn'])*1e-9
                    M_eff = df_thick.at[range_type, 'M_eff']
                    df_curve_value = df_curve.loc[range_type]
                    for index, row in df_curve_value.iterrows():
                        h_res = row['h_res']
                        sa_ratio = row['sym'] / row['asym']
                        xi_FMR = sa_ratio*sconst.elementary_charge*M_s*d_f * \
                            d_n * np.sqrt(1 + M_eff * 1000 /
                                          h_res) / sconst.hbar
                        df_curve.at[index, 'xi_FMR'] = xi_FMR
                        xi_FMR_list[range_type].append(xi_FMR)
                    # average and std of xi_FMR
                    df_thick.at[range_type, 'xi_FMR_ave'] = np.mean(
                        xi_FMR_list[range_type])
                    df_thick.at[range_type, 'xi_FMR_std'] = np.std(
                        xi_FMR_list[range_type])
                df_curve.to_csv(curve_result)
                df_thick.to_csv(thick_result)
        return 0


if __name__ == "__main__":
    xi_fmr_fitting = XiFMRFittingCore()
    xi_fmr_fitting.fitting(sys.argv[1])
