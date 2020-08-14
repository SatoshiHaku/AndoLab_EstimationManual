from rootcommand import CommonOption, RootCommand
from uroboros import Command
from uroboros.constants import ExitStatus
from .core import CurveFittingCore


class CurveFitting(Command):
    """Sub command of root"""
    name = 'curve'
    options = [CommonOption()]

    short_description = 'ST-FMR fitting for a single sample'
    long_description = 'Analyze experimental data using ST-FMR method for a single sample'
    curve_fitting = CurveFittingCore()

    def run(self, args):
        self.curve_fitting.fitting(args.dir)
        return ExitStatus.SUCCESS


class CurvePlotting(Command):
    """Sub command of stfmr"""
    name = 'curveplot'
    options = [CommonOption()]

    short_description = 'ST-FMR Plotting for a single sample'
    long_description = 'Generate plottings of experimental data and fitting ones.'

    curve_fitting = CurveFittingCore()

    def run(self, args):
        self.curve_fitting.plot(args.dir)
        return ExitStatus.SUCCESS
