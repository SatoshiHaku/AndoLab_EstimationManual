from setting import *
from uroboros import Option, Command
from uroboros.constants import ExitStatus
from pathlib import Path


class CommonOption(Option):

    def build_option(self, parser):
        # 共通するオプションを追加する
        parser.add_argument(
            'dir', type=Path, help="Target directory for ST-FMR analysis")
        return parser

        # 実行時にCommandの`run`より先に呼ばれる
    def validate(self, args):
        errors = []
        # 指定したパスが存在しない場合エラーにする
        if not args.dir.exists():
            errors.append(Exception(
                "Error! The specified directory '{}' does not exists.".format(args.dir)))
        return errors


class RootCommand(Command):
    """Root command of your application"""
    name = 'root'
    long_description = 'This is a command for ST-FMR analysis'

    def build_option(self, parser):
        """Add optional arguments"""
        parser.add_argument('--version', action='store_true',
                            default=False, help='Print version')
        return parser

    def run(self, args):
        """Your own script to run"""
        if args.version:
            print("{name} v{version}".format(
                name=self.name, version='1.0.0'))
        else:
            self.print_help()
        return ExitStatus.SUCCESS
