import glob

import scipy.optimize as sopt
import pandas as pd
import scipy.constants as sconst

from rootcommand import CommonOption, RootCommand
from uroboros import Command
from uroboros.constants import ExitStatus

from setting import *


def fitfunc_satmag(x, M_s, K_s):
    return M_s + K_s*x/(sconst.mu_0*M_s)


class MagnetizationFitting(Command):
    """Sub command of stfmr"""
    name = 'satmag'
    options = [CommonOption()]

    short_description = 'Saturation Magnetization fitting for multiple samples'
    long_description = 'Calculate and output saturation magnetization.'

    def run(self, args):
        file_list = glob.glob(str(args.dir) + '/**/' + thickness_dep_file)
        df_list = []
        for files in file_list:
            df_list.append(pd.read_csv(files))
        df = pd.concat(df_list, sort=False)
        print(df)
        df = df.set_index(["range_type"], drop=True)
        df_result = pd.DataFrame(index=[],
                                 columns=['range_type', 'M_s', 'K_s'])
        for range_type in ["negative", "positive"]:
           # load csv
            df_val = df.loc[(range_type)]
            M_eff = df_val["M_eff"].values.tolist()
            d_f = df_val["df"].values.tolist()

            # Kittel fitting
            para_ini_satmag = [0.500, 3*10**(-10)]
            [para_opt_satmag, cov] = sopt.curve_fit(
                fitfunc_satmag, d_f, M_eff, para_ini_satmag)

            df_result = df_result.append(
                {"range_type": range_type, "M_s": para_opt_satmag[0], 'K_s': para_opt_satmag[1]*10**9}, ignore_index=True)

            # xi_FMR
            file_list = glob.glob('temp/*.txt')

        df_result.to_csv(str(args.dir) + "/" +
                         satmag_result_file, index=False)

        return ExitStatus.SUCCESS
