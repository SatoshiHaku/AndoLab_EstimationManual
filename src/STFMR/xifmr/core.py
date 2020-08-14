import glob
import os
import sys

import pandas as pd
import scipy.constants as sconst
import numpy as np
import matplotlib.pyplot as plt
from uncertainties import ufloat
import uncertainties.umath as umath
Fontsize = 12


class XiFMRFittingCore():

    curve_fitting_file = ''
    thickness_dep_file = ''
    satmag_result_file = ''

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
        pass

    def fitting(self, dir):
        print("Running XiFMR fitting...")
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
                serial_num = pd.RangeIndex(
                    start=1, stop=len(curve_df.index) + 1, step=1)
                curve_df['index'] = serial_num
                curve_df = curve_df.set_index(
                    ['range_type', 'val_type', 'index'])
                xi_FMR_list = {
                    'negative': [],
                    'positive': []
                }
                M_s_val = {
                    'negative': df_satmag.at[('negative', 'val'), 'M_s'],
                    'positive': df_satmag.at[('positive', 'val'), 'M_s']
                }
                M_s_std = {
                    'negative': df_satmag.at[('negative', 'std'), 'M_s'],
                    'positive': df_satmag.at[('positive', 'std'), 'M_s']
                }
                for range_type in ['negative', 'positive']:
                    d_f = df_thick.at[(range_type, 'val'), 'df']*1e-9
                    d_n = df_thick.at[(range_type, 'val'), 'dn']*1e-9
                    M_eff_val = df_thick.loc[range_type, 'val']['M_eff']
                    M_eff_std = df_thick.loc[range_type, 'std']['M_eff']
                    curve_val_df = curve_df.loc[(
                        range_type, 'val')]
                    curve_std_df = curve_df.loc[(
                        range_type, 'std')]
                    for [val_index, val_row], [std_index, std_row] in zip(curve_val_df.iterrows(), curve_std_df.iterrows()):
                        # average and std of xi_FMR
                        h_res_val = val_row['h_res']
                        h_res_std = std_row['h_res']
                        sa_ratio_val = val_row['S/A']
                        sa_ratio_std = std_row['S/A']

                        h_res = ufloat(abs(val_row['h_res']), std_row['h_res'])
                        sa_ratio = ufloat(val_row['S/A'], std_row['S/A'])
                        M_s = ufloat(
                            abs(M_s_val[range_type]), M_s_std[range_type])
                        M_eff = ufloat(abs(M_eff_val), M_eff_std)

                        xi_FMR = (sconst.elementary_charge / sconst.hbar) * sa_ratio * \
                            M_s*d_f * d_n * \
                            umath.sqrt(1 + M_eff * 1000 / h_res)

                        curve_df.at[(range_type, 'val', val_index),
                                    'xi_FMR'] = xi_FMR.nominal_value
                        curve_df.at[(range_type, 'std', std_index),
                                    'xi_FMR'] = xi_FMR.std_dev

                curve_df = curve_df.reset_index()
                curve_df = curve_df.drop('index', axis=1)
                curve_df.to_csv(curve_result, index=False)
                df_thick.to_csv(thick_result)
                self.plot_xifmr(folders)
        return 0

    def plot_xifmr(self, dir):
        df = pd.read_csv(str(dir) + '/' +
                         self.curve_fitting_file)
        df = df.set_index(['range_type', 'val_type'], drop=True)
        xi_fmr_val = {
            'positive': [],
            'negative': []
        }
        xi_fmr_std = {
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
                xi_fmr_val[range_type].append(val_row['xi_FMR'])
                xi_fmr_std[range_type].append(std_row['xi_FMR'])
            plt.errorbar(
                frequency, xi_fmr_val[range_type], yerr=xi_fmr_std[range_type], linewidth=2.0, capsize=3, label=range_type)

        plt.rcParams['legend.loc'] = 'best'
        plt.rcParams['legend.frameon'] = True
        plt.xticks(fontsize=Fontsize)
        plt.yticks(fontsize=Fontsize)
        plt.grid(True)
        plt.title('Xi_FMR for each frequency')
        plt.xlabel('Frequency (GHz)', fontsize=Fontsize)
        plt.ylabel('Xi_FMR', fontsize=Fontsize)
        plt.legend()
        plt.savefig(str(dir) +
                    '/XiFMR.png')


if __name__ == '__main__':
    xi_fmr_fitting = XiFMRFittingCore()
    xi_fmr_fitting.fitting(sys.argv[1])
