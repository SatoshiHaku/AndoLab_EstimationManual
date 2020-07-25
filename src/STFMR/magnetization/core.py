import glob
import os
import sys

import scipy.optimize as sopt
import pandas as pd
import scipy.constants as sconst


def fitfunc_satmag(x, M_s, K_s):
    return M_s + K_s*x/(sconst.mu_0*M_s)


class MagnetizationFittingCore():
    thickness_dep_file = ""

    def __init__(self):
        base = os.path.dirname(os.path.abspath(__file__))
        name = os.path.normpath(os.path.join(
            base, '../setting/settings.json'))
        self.thickness_dep_file = pd.read_json(
            name).at["thickness_dep_file", "file_name"]
        self.satmag_result_file = pd.read_json(
            name).at["satmag_result_file", "file_name"]
        pass

    def fitting(self, dir):
        file_list = glob.glob(str(dir) + '/**/' + self.thickness_dep_file)
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

        df_result.to_csv(str(dir) + "/" +
                         self.satmag_result_file, index=False)

        return 0


if __name__ == "__main__":
    magnetization_fitting = MagnetizationFittingCore()
    magnetization_fitting.fitting(sys.argv[1])
