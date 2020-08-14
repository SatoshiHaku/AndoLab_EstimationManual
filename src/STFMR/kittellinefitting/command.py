from rootcommand import CommonOption, RootCommand
from uroboros import Command
from uroboros.constants import ExitStatus
from .core import KittelLineFittingCore


class KittelLineFitting(Command):
    """Sub command of stfmr"""
    name = 'kittelline'
    options = [CommonOption()]

    short_description = 'Kittel & linewidth fitting for a single sample'
    long_description = 'Calculate Kittel & linewidth fitting and outputs effective magnetization, damping coefficient, and W0.'

    kittelline_fitting = KittelLineFittingCore()

    def build_option(self, parser):
        """
        引数の追加．
        """
#        parser.add_argument('output', type=Path,
#                            help="Directory to save the result data")
        parser.add_argument('theta', type=float,
                            help="Angle (deg) of the applied magnetic field (in-plane)")
        parser.add_argument('df', type=float,
                            help="Thickness (nm) of the ferromagnet")
        parser.add_argument('dn', type=float,
                            help="Thickness (nm) of the nonmagnet")
        # 追加した後にparserを返す
        return parser

    def run(self, args):
        self.kittelline_fitting.fitting(args.dir, args.theta, args.df, args.dn)
        return ExitStatus.SUCCESS
