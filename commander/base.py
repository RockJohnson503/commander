# encoding: utf-8

"""
File: base.py
Author: Rock Johnson
"""
import os
import sys
from io import TextIOBase
from argparse import ArgumentParser, HelpFormatter

from commander.color import no_style, color_style


class CommandError(Exception):
    """
    自定义抛错类型.
    """
    pass


class CommanderParser(ArgumentParser):
    """
    自定义ArgumentParser类.
    """
    def __init__(self, *, positionals='位置参数', optionals='可选参数', **kwargs):
        super().__init__(**kwargs)
        add_group = self.add_argument_group
        self._positionals = add_group(positionals)
        self._optionals = add_group(optionals)


class CommanderHelpFormatter(HelpFormatter):
    """
    自定义Formatter.
    """
    show_last = {
        '--traceback', '--no-color', '--force-color', '--help'
    }

    def _reordered_actions(self, actions):
        return sorted(
            actions,
            key=lambda a: set(a.option_strings) & self.show_last != set()
        )

    def add_usage(self, usage, actions, *args, **kwargs):
        super().add_usage(usage, self._reordered_actions(actions), prefix='用法: ', *args, **kwargs)

    def add_arguments(self, actions):
        super().add_arguments(self._reordered_actions(actions))


class OutputWrapper(TextIOBase):
    """
    包装stdout/stderr周围
    """
    @property
    def style_func(self):
        return self._style_func

    @style_func.setter
    def style_func(self, style_func):
        if style_func and self.isatty():
            self._style_func = style_func
        else:
            self._style_func = lambda x: x

    def __init__(self, out, ending='\n'):
        self._out = out
        self.style_func = None
        self.ending = ending

    def __getattr__(self, item):
        return getattr(self._out, item)

    def isatty(self):
        return hasattr(self._out, 'isatty') and self._out.isatty()

    def write(self, msg, style_func=None, ending=None):
        ending = self.ending if ending is None else ending
        if ending and not msg.endswith(ending):
            msg += ending
        style_func = style_func or self.style_func
        self._out.write(style_func(msg))


class BaseCommand:
    """
    所有自定义命令的基类.
    """
    help = ''

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        self.stdout = OutputWrapper(stdout or sys.stdout)
        self.stderr = OutputWrapper(stderr or sys.stderr)
        if no_color and force_color:
            raise CommandError('"no_color"和"force_color"不能同时使用.')
        if no_color:
            self.style = no_style()
        else:
            self.style = color_style(force_color)
            self.stderr.style_func = self.style.ERROR

    def create_parser(self, prog_name, subcommand, **kwargs):
        """
        创建并返回ArgumentParser,它将用于解析此命令行的参数.
        """
        parser = CommanderParser(
            add_help=False,
            description=self.help or None,
            formatter_class=CommanderHelpFormatter,
            prog=f'{os.path.basename(prog_name)} {subcommand}',
            **kwargs
        )
        color = parser.add_mutually_exclusive_group()
        color.add_argument('--no-color', action='store_true', help='不使用彩色文字输出.')
        color.add_argument('--force-color', action='store_true', help='强制彩色文字输出.')
        parser.add_argument('--traceback', action='store_true', help='引发并追溯异常.')
        parser.add_argument('-h', '--help', action='help', help='打印帮助信息并退出')
        self.add_arguments(parser)
        return parser

    def add_arguments(self, parser: CommanderParser):
        """
        用于添加自定义参数的子类命令入口点.
        """
        pass

    def print_help(self, prog_name, subcommand):
        """
        打印该命令的帮助信息.
        """
        parser = self.create_parser(prog_name, subcommand)
        parser.print_help()

    def run_from_argv(self, argv):
        """
        运行命令,如果命令引发CommandError错误,
        则将其拦截并将其明智地打印到stderr.
        如果存在--traceback选项或引发的Exception不是CommandError,则引发它。
        """
        parser = self.create_parser(argv[0], argv[1])
        options = parser.parse_args(argv[2:])
        cmd_options = vars(options)
        # 将位置参数移出选项以模仿旧版optparse.
        args = cmd_options.pop('args', ())
        try:
            self.execute(*args, **cmd_options)
        except Exception as e:
            if options.traceback:
                raise

            self.stderr.write(f'{e.__class__.__name__}: {e}')
            sys.exit(1)

    def execute(self, *args, **options):
        """
        尝试执行此命令.
        """
        if options['force_color'] and options['no_color']:
            raise CommandError('"no_color"和"force_color"不能同时使用.')
        if options['force_color']:
            self.style = color_style(force_color=True)
        elif options['no_color']:
            self.style = no_style()
            self.stderr.style_func = None
        if options.get('stdout'):
            self.stdout = OutputWrapper(options['stdout'])
        if options.get('stderr'):
            self.stderr = OutputWrapper(options['stderr'])
        output = self.handle(*args, **options)
        if output:
            self.stdout.write(str(output))
        return output

    def handle(self, *args, **options):
        """
        命令的实际逻辑.
        子类必须实现此方法.
        """
        raise NotImplementedError('BaseCommand的子类必须提供handle()方法.')
