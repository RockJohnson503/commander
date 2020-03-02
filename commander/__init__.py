# encoding: utf-8

"""
File: __init__.py.py
Author: Rock Johnson
"""
import os
import sys
import shlex
import functools
from pkgutil import iter_modules
from argparse import ArgumentParser
from importlib import import_module
from difflib import get_close_matches

from commander.base import BaseCommand

PATH = None

__version__ = '1.0.0'


def find_commands(app_dir):
    """
    给定应用程序的目录路径,返回所有可用命令名称的列表.
    """
    commands_dir = os.path.join(app_dir, 'commands')

    if app_dir not in sys.path:
        sys.path.append(app_dir)
    return [name for _, name, is_pkg in iter_modules([commands_dir])
            if not is_pkg and not name.startswith('_')]


def load_command_class(name):
    """
    给定命令名称和应用程序名称,返回Command类实例.
    """
    module = import_module(f'commands.{name}')
    return module.Command()


@functools.lru_cache(maxsize=None)
def get_commands():
    """
    返回一个列表.

    在应用程序中查找commands软件包,如果存在命令软件包,
    则在该软件包中注册所有的命令.

    始终包含本应用程序的命令.如果指定了用户应用程序,则还包括用户定义的命令.

    该列表在第一次调用中缓存,并在后续调用中重用.
    """
    commands = find_commands(__path__[0])

    if PATH:
        commands.extend(find_commands(PATH))
    return commands


class CommanderUtility:
    """
    仿照django命令行解析应用程序开发的命令行解析框架
    """

    def __init__(self, argv=None, version=None):
        self.argv = argv or sys.argv
        self.version = version or __version__
        self.prog_name = os.path.basename(self.argv[0])

    def main_help_text(self, commands_only=False):
        """返回脚本的主要帮助信息,字符串格式"""
        usage = []
        if not commands_only:
            usage.extend([
                f'输入"{self.prog_name} help <subcommand>"以获取子命令的帮助信息.',
                '',
                '可用子命令:',
                ''
            ])
        usage.extend(sorted(get_commands()))
        return '\n'.join(usage)

    def fetch_command(self, subcommand):
        """
        尝试获取给定子命令,如果获取不到,则从命令行调用的相应命令打印一条信息.
        """
        commands = get_commands()
        if subcommand not in commands:
            possible_matches = get_close_matches(subcommand, commands)
            sys.stderr.write(f'未知命令: "{subcommand}"')
            if possible_matches:
                sys.stderr.write(f'. 你是要使用"{possible_matches[0]}"吗?')
            sys.stderr.write(f'\n输入"{self.prog_name} help"以获取用法.\n')
            sys.exit(1)

        if isinstance(subcommand, BaseCommand):
            klass = subcommand
        else:
            klass = load_command_class(subcommand)
        return klass

    def execute(self):
        """
        运行已创建的子命令
        """
        try:
            subcommand = self.argv[1]
        except:
            subcommand = 'help'

        parser = ArgumentParser(add_help=False, allow_abbrev=False)
        parser.add_argument('args', nargs='*')
        options, args = parser.parse_known_args(self.argv[2:])

        if subcommand == 'help':
            if options.args:
                self.fetch_command(options.args[0]).print_help(self.prog_name, options.args[0])
            else:
                sys.stdout.write(f'{self.main_help_text(commands_only="--commands" in args)}\n')
        elif subcommand == 'version' or self.argv[1:] in (['-v'], ['--version']):
            sys.stdout.write(f'{self.version}\n')
        elif self.argv[1:] in (['-h'], ['--help']):
            sys.stdout.write(f'{self.main_help_text()}\n')
        else:
            self.fetch_command(subcommand).run_from_argv(self.argv)


def execute_from_command_line(path, argv=None, version=None):
    """运行CommanderUtility"""
    if not isinstance(path, str):
        raise TypeError('path必须是字符串')

    # 将字符串处理成命令行参数
    if isinstance(argv, str):
        argv = shlex.split(argv)

    global PATH
    PATH = path
    utility = CommanderUtility(argv, version)
    utility.execute()
