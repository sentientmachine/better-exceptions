"""Beautiful and helpful exceptions

Just set your `BETTER_EXCEPTIONS` environment variable. It handles the rest.


   Name: better_exceptions
 Author: Josh Junon
  Email: josh@junon.me
    URL: github.com/qix-/better-exceptions
License: Copyright (c) 2017 Josh Junon, licensed under the MIT license
"""

from __future__ import absolute_import
from __future__ import print_function

import logging
import sys

from .formatter import THEME, MAX_LENGTH, PIPE_CHAR, CAP_CHAR, ExceptionFormatter
from .encoding import to_byte
from .context import PY3
from .color import SUPPORTS_COLOR, SHOULD_ENCODE, STREAM
from .log import BetExcLogger, patch as patch_logging
from .repl import interact, get_repl


__version__ = '0.2.2'


THEME = THEME.copy()  # Users customizing the theme should not impact core


def write_stream(data, stream=STREAM):
    if SHOULD_ENCODE:
        data = to_byte(data)

        if PY3:
            stream.buffer.write(data)
        else:
            stream.write(data)
    else:
        stream.write(data)


def format_exception(exc, value, tb):
    # Rebuild each time to take into account any changes made by the user to the global parameters
    formatter = ExceptionFormatter(colored=SUPPORTS_COLOR, theme=THEME, max_length=MAX_LENGTH,
                                   pipe_char=PIPE_CHAR, cap_char=CAP_CHAR)
    return formatter.format_exception(exc, value, tb)


def excepthook(exc, value, tb):
    formatted = format_exception(exc, value, tb)

    try:
        import sys
        from pygments.style import Style
        from pygments.token import Keyword, Name, Comment, String, Error, \
             Number, Operator, Generic
    
        """
        A colorful style, inspired by the manni terminal highlighting style.
        """
    
        class MyStyle(Style):
            background_color = '#f0f3f3'
    
            styles = {
                #Whitespace:         '#bbbbbb',
                Comment:            'italic #0099FF',
                Comment.Preproc:    'noitalic #009999',
                Comment.Special:    'bold',
    
                Keyword:            'bold #006699',
                Keyword.Pseudo:     'nobold',
                Keyword.Type:       '#007788',
    
                Operator:           '#FF0000',
                Operator.Word:      'bold #000000',
                Name.Builtin:       '#FF44FF',      #this one defines the Error's FileName
                Name.Function:      '#CC00FF',
                Name.Class:         'bold #00AA88',
                Name.Namespace:     'bold #00CCFF',
                Name.Exception:     'bold #CC0000',
                Name.Variable:      '#003333',
                Name.Constant:      '#336600',
                Name.Label:         '#9999FF',
                Name.Entity:        'bold #999999',
                Name.Attribute:     '#330099',
                Name.Tag:           'bold #330099',
                Name.Decorator:     '#9999FF',
    
                String:             '#CC3300',
                String.Doc:         'italic',
                String.Interpol:    '#AA0000',
                String.Escape:      'bold #CC3300',
                String.Regex:       '#33AAAA',
                String.Symbol:      '#FFCC33',
                String.Other:       '#CC3300',
    
                #Number:             'bg:#FFFFFF #FF6600',         #this one defines the error's line number
                Number:             'bg:#555555 bold #FFFFFF',
                Generic.Heading:    'bold #003300',
                Generic.Subheading: 'bold #003300',
                Generic.Deleted:    'border:#CC0000 bg:#FFCCCC',
                Generic.Inserted:   'border:#00CC00 bg:#CCFFCC',
                Generic.Error:      'bg:#FF0000 bold #000000',
                Generic.Emph:       'italic',
                Generic.Strong:     'bold',
                Generic.Prompt:     'bold #000099',
                Generic.Output:     '#AAAAAA',
                Generic.Traceback:  'bg:#FF0000 bold #00FF00',
    
                Error:              'bg:#FFAAAA #AA0000'
                #Error:              'bg:#FF0000 bold #AA0000'
                #Error:              'bg:#00FF00 bold #00FF00'
            }
    
    


        import traceback
        from pygments import highlight
        from pygments.lexers import get_lexer_by_name
        from pygments.formatters import Terminal256Formatter

        tbtext = ''.join(traceback.format_exception(type, value, tb))
        lexer = get_lexer_by_name("pytb", stripall=True)
#    formatter = TerminalFormatter(bg='dark')
#    #formatter = TerminalFormatter(colorscheme=COLOR_SCHEME)
#    formatter = Terminal256Formatter(style='friendly')
#    formatter = Terminal256Formatter(style='default')
#    formatter = Terminal256Formatter(style='colorful')
        #formatter = Terminal256Formatter(style='vim')
        #formatter = Terminal256Formatter(style='fruity')
        #formatter = Terminal256Formatter(style='manni')      #good, except for FileName
        #formatter = Terminal256Formatter(style=MyStyle)
        #formatter = Terminal256Formatter(YourStyle)
        formatter = Terminal256Formatter(style=MyStyle)


        #formatter = Terminal256Formatter(style='igor')      #terrible
        #formatter = Terminal256Formatter(style='xcode')      #terrible
        #formatter = Terminal256Formatter(style='autumn')      #ok
        #formatter = Terminal256Formatter(style='vs')          #terrible
        #formatter = Terminal256Formatter(style='rrt')
        #formatter = Terminal256Formatter(style='native')
        #formatter = Terminal256Formatter(style='perldoc')
        #formatter = Terminal256Formatter(style='borland')    #bad
        #formatter = Terminal256Formatter(style='tango')      #bad
        #formatter = Terminal256Formatter(style='emacs')
        #formatter = Terminal256Formatter(style='monokai')     #best one yet
        #formatter = Terminal256Formatter(style='monokaiyo')
        #formatter = Terminal256Formatter(style='paraiso-dark')
        #formatter = Terminal256Formatter(style='murphy')
        #formatter = Terminal256Formatter(style='bw')
        #formatter = Terminal256Formatter(style='pastie')
        #formatter = Terminal256Formatter(style='paraiso-light')
        #formatter = Terminal256Formatter(style='trac')            #ok




        class bcolors(object):
            HEADER = '\033[95m'
            WARNING = '\033[93m'
            FAIL = '\033[91m'
            ENDC = '\033[0m'
            BOLD = '\033[1m'
            UNDERLINE = '\033[4m'
            PURPLE = '\033[0;35m'
            WHITE = '\033[0;37m'
            WHITEBOLD = WHITE + BOLD
            CYAN = '\033[0;36m'
            CYANBOLD = CYAN + BOLD
            PINK = '\033[01;38;5;213m'
            PINKBOLD = PINK + BOLD
            RED = '\033[0;31m'
            REDBOLD = RED + BOLD
            GREEN = '\033[92m'
            GREENBOLD = GREEN + BOLD
            PURPLEBOLD = '\033[0;35m' + BOLD
            FAILBOLD = FAIL + BOLD
            BLUE = '\033[94m'
            BLUEBOLD = BLUE + BOLD
            BLACK = '\033[0;30m'
            BLACKBOLD = BLACK + BOLD
            BG_GREEN = '\033[48;5;046m'
            BG_WHITE = '\033[48;5;255m'
            BG_GREEN_FG_BLACKBOLD = BLACKBOLD + BG_GREEN
            BG_WHITE_FG_BLACKBOLD = BLACKBOLD + BG_WHITE

        colorized = highlight(tbtext, lexer, formatter)

        sys.stderr.write(bcolors.BLUEBOLD +
                "==============BETTER_EXCEPTIONS STACKTRACE ==========================\n" +
                bcolors.ENDC) 

        write_stream(formatted, STREAM)

        sys.stderr.write(bcolors.GREENBOLD +
                "=================== PYGMENTS STACKTRACE ==========================\n" +
                bcolors.ENDC)

        sys.stderr.write(colorized)
    
    except ImportError:
        print("can't load your things, remedial actions?")
        exit()


def hook():
    sys.excepthook = excepthook

    logging.setLoggerClass(BetExcLogger)
    patch_logging()

    if hasattr(sys, 'ps1'):
        print('WARNING: better_exceptions will only inspect code from the command line\n'
              '         when using: `python -m better_exceptions\'. Otherwise, only code\n'
              '         loaded from files will be inspected!', file=sys.stderr)
