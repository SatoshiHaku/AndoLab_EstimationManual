from rootcommand import CommonOption, RootCommand
from uroboros import Command
from uroboros.constants import ExitStatus
from .core import XiFLDLFittingCore


class XiFLDLFitting(Command):
    """Sub command of stfmr"""
    name = 'xifldl'
    options = [CommonOption()]

    short_description = 'Calculate xi_FL and xi_DL for multiple samples'
    long_description = 'Calculate and output xi_DL and xi_FL.'

    XiFLDL_fitting = XiFLDLFittingCore()

    def run(self, args):
        self.XiFLDL_fitting.fitting(args.dir)
        self.XiFLDL_fitting.plot(args.dir)
        return ExitStatus.SUCCESS
