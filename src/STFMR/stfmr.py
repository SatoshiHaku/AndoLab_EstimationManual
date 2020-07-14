from uroboros import Command
from uroboros.constants import ExitStatus

from rootcommand import CommonOption, RootCommand
from curvefitting import CurveFitting, CurvePlotting
from kittellinefitting import KittelLineFitting
from magnetization import MagnetizationFitting
from xifmr import XiFMRFitting
from xifldl import XiFLDLFitting


# Create command tree
root_cmd = RootCommand()
root_cmd.add_command(CurveFitting())
root_cmd.add_command(CurvePlotting())
root_cmd.add_command(KittelLineFitting())
root_cmd.add_command(MagnetizationFitting())
root_cmd.add_command(XiFMRFitting())
root_cmd.add_command(XiFLDLFitting())

if __name__ == '__main__':
    exit(root_cmd.execute())
