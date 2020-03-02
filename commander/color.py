# encoding: utf-8

"""
File: color.py
Author: Rock Johnson
"""
import os
import sys
import functools

color_names = ('black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white')
foreground = {color_names[x]: '3%s' % x for x in range(8)}
background = {color_names[x]: '4%s' % x for x in range(8)}

RESET = '0'
opt_dict = {'bold': '1', 'underscore': '4', 'blink': '5', 'reverse': '7', 'conceal': '8'}

NOCOLOR_PALETTE = 'nocolor'
DARK_PALETTE = 'dark'
LIGHT_PALETTE = 'light'

PALETTES = {
    NOCOLOR_PALETTE: {
        'ERROR': {},
        'SUCCESS': {},
        'WARNING': {},
        'NOTICE': {},
        'SQL_FIELD': {},
        'SQL_COLTYPE': {},
        'SQL_KEYWORD': {},
        'SQL_TABLE': {},
        'HTTP_INFO': {},
        'HTTP_SUCCESS': {},
        'HTTP_REDIRECT': {},
        'HTTP_NOT_MODIFIED': {},
        'HTTP_BAD_REQUEST': {},
        'HTTP_NOT_FOUND': {},
        'HTTP_SERVER_ERROR': {},
        'MIGRATE_HEADING': {},
        'MIGRATE_LABEL': {},
    },
    DARK_PALETTE: {
        'ERROR': {'fg': 'red', 'opts': ('bold',)},
        'SUCCESS': {'fg': 'green', 'opts': ('bold',)},
        'WARNING': {'fg': 'yellow', 'opts': ('bold',)},
        'NOTICE': {'fg': 'red'},
        'SQL_FIELD': {'fg': 'green', 'opts': ('bold',)},
        'SQL_COLTYPE': {'fg': 'green'},
        'SQL_KEYWORD': {'fg': 'yellow'},
        'SQL_TABLE': {'opts': ('bold',)},
        'HTTP_INFO': {'opts': ('bold',)},
        'HTTP_SUCCESS': {},
        'HTTP_REDIRECT': {'fg': 'green'},
        'HTTP_NOT_MODIFIED': {'fg': 'cyan'},
        'HTTP_BAD_REQUEST': {'fg': 'red', 'opts': ('bold',)},
        'HTTP_NOT_FOUND': {'fg': 'yellow'},
        'HTTP_SERVER_ERROR': {'fg': 'magenta', 'opts': ('bold',)},
        'MIGRATE_HEADING': {'fg': 'cyan', 'opts': ('bold',)},
        'MIGRATE_LABEL': {'opts': ('bold',)},
    },
    LIGHT_PALETTE: {
        'ERROR': {'fg': 'red', 'opts': ('bold',)},
        'SUCCESS': {'fg': 'green', 'opts': ('bold',)},
        'WARNING': {'fg': 'yellow', 'opts': ('bold',)},
        'NOTICE': {'fg': 'red'},
        'SQL_FIELD': {'fg': 'green', 'opts': ('bold',)},
        'SQL_COLTYPE': {'fg': 'green'},
        'SQL_KEYWORD': {'fg': 'blue'},
        'SQL_TABLE': {'opts': ('bold',)},
        'HTTP_INFO': {'opts': ('bold',)},
        'HTTP_SUCCESS': {},
        'HTTP_REDIRECT': {'fg': 'green', 'opts': ('bold',)},
        'HTTP_NOT_MODIFIED': {'fg': 'green'},
        'HTTP_BAD_REQUEST': {'fg': 'red', 'opts': ('bold',)},
        'HTTP_NOT_FOUND': {'fg': 'red'},
        'HTTP_SERVER_ERROR': {'fg': 'magenta', 'opts': ('bold',)},
        'MIGRATE_HEADING': {'fg': 'cyan', 'opts': ('bold',)},
        'MIGRATE_LABEL': {'opts': ('bold',)},
    }
}
DEFAULT_PALETTE = DARK_PALETTE


def colorize(text='', opts=(), **kwargs):
    code_list = []
    if text == '' and len(opts) == 1 and opts[0] == 'reset':
        return '\x1b[%sm' % RESET
    for k, v in kwargs.items():
        if k == 'fg':
            code_list.append(foreground[v])
        elif k == 'bg':
            code_list.append(background[v])
    for o in opts:
        if o in opt_dict:
            code_list.append(opt_dict[o])
    if 'noreset' not in opts:
        text = '%s\x1b[%sm' % (text or '', RESET)
    return '%s%s' % (('\x1b[%sm' % ';'.join(code_list)), text or '')


def make_style_term(opts=(), **kwargs):
    return lambda text: colorize(text, opts, **kwargs)


def parse_color_setting(config_string):
    if not config_string:
        return PALETTES[DEFAULT_PALETTE]

    parts = config_string.lower().split(';')
    palette = PALETTES[NOCOLOR_PALETTE].copy()
    for part in parts:
        if part in PALETTES:
            palette.update(PALETTES[part])
        elif '=' in part:
            definition = {}

            role, instructions = part.split('=')
            role = role.upper()

            styles = instructions.split(',')
            styles.reverse()

            colors = styles.pop().split('/')
            colors.reverse()
            fg = colors.pop()
            if fg in color_names:
                definition['fg'] = fg
            if colors and colors[-1] in color_names:
                definition['bg'] = colors[-1]

            opts = tuple(s for s in styles if s in opt_dict)
            if opts:
                definition['opts'] = opts

            if role in PALETTES[NOCOLOR_PALETTE] and definition:
                palette[role] = definition

    if palette == PALETTES[NOCOLOR_PALETTE]:
        return None
    return palette


def supports_color():
    """
    如果正在运行的系统支持颜色,则返回True,否则返回False.
    """
    plat = sys.platform
    supported_platform = plat != 'Pocket PC' and (plat != 'win32' or 'ANSICON' in os.environ)
    is_a_tty = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
    return supported_platform and is_a_tty


class Style:
    pass


def make_style(config_str=''):
    """
    用给定的config_str创建一个Style对象.
    """
    style = Style()

    color_settings = parse_color_setting(config_str)

    for role in PALETTES[NOCOLOR_PALETTE]:
        if color_settings:
            format = color_settings.get(role, {})
            style_func = make_style_term(**format)
        else:
            def style_func(x):
                return x
        setattr(style, role, style_func)

    return style


@functools.lru_cache(maxsize=None)
def no_style():
    """
    返回一个没有颜色方案的Style对象.
    """
    return make_style('nocolor')


def color_style(force_color=False):
    """
    从Commander的颜色方案中返回一个Style对象.
    """
    if not force_color and not supports_color():
        return no_style()
    return make_style(os.environ.get('COMMANDER_COLORS', ''))
