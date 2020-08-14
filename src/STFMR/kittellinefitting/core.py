import pandas as pd
import numpy as np
import scipy.optimize as sopt
import scipy.constants as sconst
import matplotlib.pyplot as plt

import os
import sys

from pathlib import Path

gamma = sconst.physical_constants['electron gyromag. ratio'][0]
gamma_GHZ = float(
    sconst.physical_constants['electron gyromag. ratio in MHz/T'][0])/1000
Fontsize = 10


def fitfunc_kittel(h, Meff):
    '''
    面内に磁場をかけた時のKittelの式．

     Parameters
    ----------
    h : 印加磁場 (mT)
    gamma : 磁気回転比
    Meff : 有効磁化
     Output
    ---------
    frequency (GHz)
    '''
    return gamma_GHZ * np.sqrt(h / 1000 * (h / 1000 + Meff))


def fitfunc_line(x, a, b):
    return a * x + b


class KittelLineFittingCore():
    thickness_dep_file = ''
    curve_fitting_file = ''

    def __init__(self):
        base = os.path.dirname(os.path.abspath(__file__))
        name = os.path.normpath(os.path.join(
            base, '../setting/settings.json'))
        self.curve_fitting_file = pd.read_json(
            name).at['curve_fitting_file', 'file_name']
        self.thickness_dep_file = pd.read_json(
            name).at['thickness_dep_file', 'file_name']

    def fitting(self, dir, theta, d_f, d_n):
        print("Running Kittel & line fitting...")
        df = pd.read_csv(str(dir) + '/' +
                         self.curve_fitting_file)
        df = df.set_index(['range_type', 'val_type'], drop=True)
        df_result = pd.DataFrame(index=[],
                                 columns=['range_type', 'val_type', 'M_eff', 'damping', 'W0', 'theta', 'df', 'dn'])

        for range_type, init_M in [['negative', -0.500], ['positive', 0.500]]:
           # load csv
            df_val = df.loc[range_type, 'val']
            df_std = df.loc[range_type, 'std']
            h_res_val = df_val['h_res'].tolist()
            h_res_std = df_std['h_res'].tolist()
            freq = df_val['frequency'].tolist()
            lw = df_val['linewidth'].tolist()
            lw_std = df_std['linewidth'].tolist()

            # Kittel fitting
            para_ini_kittel = [init_M]
            [para_kittel_ndarr, cov_kittel_ndarr] = sopt.curve_fit(
                fitfunc_kittel, h_res_val, freq, para_ini_kittel)
            err_kittel_ndarr = np.sqrt(np.diag(cov_kittel_ndarr))

            plt.figure()
            plt.errorbar(
                h_res_val, freq, yerr=h_res_std, capsize=3, linewidth=2.0, ls='None', label='error bar ('+range_type+')')
            h_res_reprod = np.arange(min(h_res_val), max(h_res_val), 1)
            freq_reprod = list(
                map(lambda x: fitfunc_kittel(x, *para_kittel_ndarr), h_res_reprod))
            plt.plot(h_res_reprod, freq_reprod,
                     linewidth=2.0, label='fitted curve (' + range_type + ')')
            plt.plot([], [], linewidth=0, label='M_eff={0:.4e}±{1:.1e}'.format(
                para_kittel_ndarr[0], err_kittel_ndarr[0]))
            plt.rcParams['legend.loc'] = 'best'
            plt.rcParams['legend.frameon'] = True
            plt.xticks(fontsize=Fontsize)
            plt.yticks(fontsize=Fontsize)
            plt.grid(True)
            plt.title('Kittel Fitting ('+range_type+')')
            plt.xlabel('H_res (T)', fontsize=Fontsize)
            plt.ylabel('frequency (GHz)', fontsize=Fontsize)
            plt.legend()
            plt.savefig(str(dir)+'/kittel_fitting_'+range_type+'.png')

            # linewidth fitting
            para_ini_line = [2, 0.1]
            [para_line_ndarr, cov_line_ndarr] = sopt.curve_fit(
                fitfunc_line, freq, lw, para_ini_line)
            err_line_ndarr = np.sqrt(np.diag(cov_line_ndarr))
            # 線幅の単位はmT
            alpha = (para_line_ndarr[0] * gamma_GHZ) / 1000
            alpha_std = (err_line_ndarr[0] * gamma_GHZ) / 1000

            plt.figure()
            plt.errorbar(
                freq, lw, yerr=lw_std, capsize=3, linewidth=2.0, ls='None', label='error bar (' + range_type + ')')
            freq_reprod = np.arange(min(freq)-1, max(freq)+1, 0.2)
            lw_reprod = list(
                map(lambda x: fitfunc_line(x, *para_line_ndarr), freq_reprod))
            plt.plot(freq_reprod, lw_reprod,
                     linewidth=2.0, label='fitted curve (' + range_type + ')')
            plt.plot([], [], linewidth=0, label='alpha={0:.4e}±{1:.1e}'.format(
                alpha, alpha_std))
            plt.rcParams['legend.loc'] = 'best'
            plt.rcParams['legend.frameon'] = True
            plt.xticks(fontsize=Fontsize)
            plt.yticks(fontsize=Fontsize)
            plt.grid(True)
            plt.title('Line Fitting ('+range_type+')')
            plt.xlabel('frequency (GHz)', fontsize=Fontsize)
            plt.ylabel('linewidth (mT)', fontsize=Fontsize)
            plt.legend()
            plt.savefig(str(dir)+'/line_fitting_'+range_type+'.png')

            df_result = df_result.append(
                {'range_type': range_type, 'val_type': 'val', 'M_eff': para_kittel_ndarr[0], 'damping': alpha, 'W0': para_line_ndarr[1], 'theta': theta, 'df': d_f, 'dn': d_n}, ignore_index=True)
            df_result = df_result.append(
                {'range_type': range_type, 'val_type': 'std', 'M_eff': err_kittel_ndarr[0], 'damping': alpha_std, 'W0': err_line_ndarr[1], 'theta': 0, 'df': 0, 'dn': 0}, ignore_index=True)
        df_result.to_csv(str(dir) + '/' +
                         self.thickness_dep_file)
        return 0


if __name__ == '__main__':
    kittelline_fitting = KittelLineFittingCore()
    kittelline_fitting.fitting(
        sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
