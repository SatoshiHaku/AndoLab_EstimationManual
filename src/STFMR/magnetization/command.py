import glob

import scipy.optimize as sopt
import pandas as pd
import scipy.constants as sconst

from rootcommand import CommonOption, RootCommand
from uroboros import Command
from uroboros.constants import ExitStatus

from .core import MagnetizationFittingCore


def fitfunc_satmag(x, M_s, K_s):
    return M_s + K_s*x/(sconst.mu_0*M_s)


class MagnetizationFitting(Command):
    """Sub command of stfmr"""
    name = 'satmag'
    options = [CommonOption()]

    short_description = 'Saturation Magnetization fitting for multiple samples'
    long_description = 'Calculate and output saturation magnetization.'

    magnetization_fitting = MagnetizationFittingCore()

    def run(self, args):
        self.magnetization_fitting.fitting(args.dir)
        return ExitStatus.SUCCESS
