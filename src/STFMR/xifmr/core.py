import glob
import os

import pandas as pd
import scipy.constants as sconst
import numpy as np

from rootcommand import CommonOption, RootCommand
from uroboros import Command
from uroboros.constants import ExitStatus

from setting import *


class XiFMRFitting(Command):
    """Sub command of stfmr"""
    name = 'xifmr'
    options = [CommonOption()]

    short_description = 'Calculate xi_FMR for multiple samples'
    long_description = 'Calculate and output xi_FMR.'

    def run(self, args):
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
                xi_FMR_list = {
                    'negative': [],
                    'positive': []
                }
                for range_type, M_s in [["negative", df_satmag.at['negative', 'M_s']], ["positive", df_satmag.at['positive', 'M_s']]]:
                    d_f = df_thick.at[range_type, 'df']*1e-9
                    d_n = df_thick.at[range_type, 'dn']*1e-9
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
        return ExitStatus.SUCCESS
