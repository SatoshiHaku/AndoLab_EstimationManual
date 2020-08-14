from rootcommand import CommonOption, RootCommand
from uroboros import Command
from uroboros.constants import ExitStatus

from .core import XiFMRFittingCore


class XiFMRFitting(Command):
    """Sub command of stfmr"""
    name = 'xifmr'
    options = [CommonOption()]

    short_description = 'Calculate xi_FMR for multiple samples'
    long_description = 'Calculate and output xi_FMR.'

    xi_fmr_fitting = XiFMRFittingCore()

    def run(self, args):
        self.xi_fmr_fitting.fitting(args.dir)
        return ExitStatus.SUCCESS
