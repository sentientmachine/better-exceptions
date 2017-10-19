"""Beautiful and helpful exceptions                                                                                            
                                                                                                                               
Just `import better_exceptions` somewhere. It handles the rest.                                                                
                                                                                                                               
                                                                                                                               
   Name: better_exceptions                                                                                                     
 Author: Josh Junon                                                                                                            
  Email: josh@junon.me                                                                                                         
    URL: github.com/qix-/better-exceptions                                                                                     
License: Copyright (c) 2017 Josh Junon, licensed under the MIT license                                                         
"""                                                                                                                            
                                                                                                                               
from __future__ import absolute_import                                                                                         
from __future__ import print_function                                                                                          
                                                                                                                               
import ast                                                                                                                     
import inspect                                                                                                                 
import keyword                                                                                                                 
import linecache                                                                                                               
import locale                                                                                                                  
import logging                                                                                                                 
import os                                                                                                                      
import re                                                                                                                      
import sys                                                                                                                     
import traceback                                                                                                               
import codecs                                                                                                                  
                                                                                                                               
from .color import STREAM, SUPPORTS_COLOR                                                                                      
from .log import BetExcLogger, patch as patch_logging                                                                          
from .repl import interact, get_repl                                                                                           
                                                                                                                               
                                                                                                                               
def isast(v):                                                                                                                  
    return inspect.isclass(v) and issubclass(v, ast.AST)                                                                       
                                                                                                                               
                                                                                                                               
ENCODING = locale.getpreferredencoding()                                                                                       
                                                                                                                               
PIPE_CHAR = u'\u2502'                                                                                                          
CAP_CHAR = u'\u2514'                                                                                                           
                                                                                                                               
try:                                                                                                                           
    PIPE_CHAR.encode(ENCODING)
except UnicodeEncodeError:
    PIPE_CHAR = '|'
    CAP_CHAR = '->'

COMMENT_REGXP = re.compile(r'((?:(?:"(?:[^\\"]|(\\\\)*\\")*")|(?:\'(?:[^\\"]|(\\\\)*\\\')*\')|[^#])*)(#.*)$')
CMDLINE_REGXP = re.compile(r'(?:[^\t ]*([\'"])(?:\\.|.)*(?:\1))[^\t ]*|([^\t ]+)')

AST_ELEMENTS = {
    'builtins': __builtins__.keys() if type(__builtins__) is dict else dir(__builtins__),
    'keywords': [getattr(ast, cls) for cls in dir(ast) if keyword.iskeyword(cls.lower()) and isast(getattr(ast, cls))],
}

THEME = {
    'comment': lambda s: '\x1b[2;37m{}\x1b[m'.format(s),
    'keyword': lambda s: '\x1b[33;1m{}\x1b[m'.format(s),
    'builtin': lambda s: '\x1b[35;1m{}\x1b[m'.format(s),
    'literal': lambda s: '\x1b[31m{}\x1b[m'.format(s),
    'inspect': lambda s: s if not SUPPORTS_COLOR else u'\x1b[36m{}\x1b[m'.format(s),
}

MAX_LENGTH = 128

PY3 = sys.version_info[0] >= 3


def _byte(val):
    unicode_type = str if PY3 else unicode
    if isinstance(val, unicode_type):
        try:
            return val.encode(ENCODING)
        except UnicodeEncodeError:
            if PY3:
                return codecs.escape_decode(val)[0]
            else:
                return val.encode("unicode-escape").decode("string-escape")

    return val


def _unicode(val):
    if isinstance(val, bytes):
        try:
            return val.decode(ENCODING)
        except UnicodeDecodeError:
            return val.decode("unicode-escape")

    return val


def colorize_comment(source):
    match = COMMENT_REGXP.match(source)
    if match:
        source = '{}{}'.format(match.group(1), THEME['comment'](match.group(4)))
    return source


def colorize_tree(tree, source):
    if not SUPPORTS_COLOR:
        # quick fail
        return source

    chunks = []

    offset = 0
    nodes = [n for n in ast.walk(tree)]
    nnodes = len(nodes)

    def append(offset, node, s, theme):
        begin_col = node.col_offset
        src_chunk = source[offset:begin_col]
        chunks.append(src_chunk)
        chunks.append(THEME[theme](s))
        return begin_col + len(s)

    displayed_nodes = []

    for i in range(nnodes):
        node = nodes[i]
        nodecls = node.__class__
        nodename = nodecls.__name__

        if 'col_offset' not in dir(node):
            continue

        if nodecls in AST_ELEMENTS['keywords']:
            displayed_nodes.append((node, nodename.lower(), 'keyword'))

        if nodecls == ast.Name and node.id in AST_ELEMENTS['builtins']:
            displayed_nodes.append((node, node.id, 'builtin'))

        if nodecls == ast.Str:
            displayed_nodes.append((node, "'{}'".format(node.s), 'literal'))

        if nodecls == ast.Num:
            displayed_nodes.append((node, str(node.n), 'literal'))

    displayed_nodes.sort(key=lambda elem: elem[0].col_offset)

    for dn in displayed_nodes:
        offset = append(offset, *dn)

    chunks.append(source[offset:])
    return colorize_comment(''.join(chunks))


def get_relevant_names(source, tree):
    return [node for node in ast.walk(tree) if isinstance(node, ast.Name)]


def format_value(v):
    v = repr(v)
    if MAX_LENGTH is not None and len(v) > MAX_LENGTH:
        v = v[:MAX_LENGTH] + '...'
    return v


def get_relevant_values(source, frame, tree):
    names = get_relevant_names(source, tree)
    values = []

    for name in names:
        text = name.id
        col = name.col_offset
        if text in frame.f_locals:
            val = frame.f_locals.get(text, None)
            values.append((text, col, format_value(val)))
        elif text in frame.f_globals:
            val = frame.f_globals.get(text, None)
            values.append((text, col, format_value(val)))

    values.sort(key=lambda e: e[1])

    return values


def split_cmdline(cmdline):
    return [m.group(0) for m in CMDLINE_REGXP.finditer(cmdline)]


def get_string_source():
    import os
    import platform

    # import pdb; pdb.set_trace()

    cmdline = None
    if platform.system() == 'Windows':
        # TODO use winapi to obtain the command line
        return ''
    elif platform.system() == 'Linux':
        # TODO try to use proc
        pass

    if cmdline is None and os.name == 'posix':
        from subprocess import CalledProcessError, check_output as spawn

        try:
            cmdline = spawn(['ps', '-ww', '-p', str(os.getpid()), '-o', 'command='])
        except CalledProcessError:
            return ''
    else:
        # current system doesn't have a way to get the command line
        return ''

    cmdline = cmdline.decode('utf-8').strip()
    cmdline = split_cmdline(cmdline)

    extra_args = sys.argv[1:]
    if len(extra_args) > 0:
        if cmdline[-len(extra_args):] != extra_args:
            # we can't rely on the output to be correct; fail!
            return ''

        cmdline = cmdline[1:-len(extra_args)]

    skip = 0
    for i in range(len(cmdline)):
        a = cmdline[i].strip()
        if not a.startswith('-c'):
            skip += 1
        else:
            a = a[2:].strip()
            if len(a) > 0:
                cmdline[i] = a
            else:
                skip += 1
            break

    cmdline = cmdline[skip:]
    source = ' '.join(cmdline)

    return source


def get_traceback_information(tb):
    frame_info = inspect.getframeinfo(tb)
    filename = frame_info.filename
    lineno = frame_info.lineno
    function = frame_info.function

    repl = get_repl()
    if repl is not None and filename in repl.entries:
        _, filename, source = repl.entries[filename]
        source = source.replace('\r\n', '\n').split('\n')[lineno - 1]
    elif filename == '<string>':
        source = get_string_source()
    else:
        source = linecache.getline(filename, lineno)

    source = source.strip()

    try:
        tree = ast.parse(source, mode='exec')
    except SyntaxError:
        return filename, lineno, function, source, source, []

    relevant_values = get_relevant_values(source, tb.tb_frame, tree)
    color_source = colorize_tree(tree, source)

    return filename, lineno, function, source, color_source, relevant_values


def format_traceback_frame(tb):
    filename, lineno, function, source, color_source, relevant_values = get_traceback_information(tb)

    lines = [color_source]
    for i in reversed(range(len(relevant_values))):
        _, col, val = relevant_values[i]
        pipe_cols = [pcol for _, pcol, _ in relevant_values[:i]]
        line = ''
        index = 0
        for pc in pipe_cols:
            line += (' ' * (pc - index)) + PIPE_CHAR
            index = pc + 1

        if not PY3 and isinstance(val, str):
            # In Python2 the Non-ASCII value will be the escaped string,
            # use string-escape to decode the string to show the text in human way.
            val = _unicode(val.decode("string-escape"))

        line += u'{}{} {}'.format((' ' * (col - index)), CAP_CHAR, val)
        lines.append(THEME['inspect'](line))
    formatted = u'\n    '.join([_unicode(x) for x in lines])

    return (filename, lineno, function, formatted), color_source


def format_traceback(tb=None):
    omit_last = False
    if not tb:
        try:
            raise Exception()
        except:
            omit_last = True
            _, _, tb = sys.exc_info()
            assert tb is not None

    frames = []
    final_source = ''
    while tb:
        if omit_last and not tb.tb_next:
            break

        formatted, colored = format_traceback_frame(tb)

        # special case to ignore runcode() here.
        if not (os.path.basename(formatted[0]) == 'code.py' and formatted[2] == 'runcode'):
            final_source = colored
            frames.append(formatted)

        tb = tb.tb_next

    lines = traceback.format_list(frames)

    return ''.join(lines), final_source


def write_stream(data):
    data = _byte(data)

    if PY3:
        STREAM.buffer.write(data)
    else:
        STREAM.write(data)


def format_exception(exc, value, tb):
    formatted, colored_source = format_traceback(tb)

    if not str(value) and exc is AssertionError:
        value.args = (colored_source,)
    title = traceback.format_exception_only(exc, value)

    #full_trace = u'Traceback (most recent call last):\n{}{}\n'.format(formatted, title[0].strip())



    full_trace = u'Traceback (most recent call last):\n{}{}\n'.format(formatted, ''.join(title))


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
    

    
        def myexcepthook(type, value, tb):
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
            write_stream(full_trace)

            sys.stderr.write(bcolors.GREENBOLD +
                    "=================== PYGMENTS STACKTRACE ==========================\n" +
                    bcolors.ENDC) 

            sys.stderr.write(colorized)
            return full_trace

        myexcepthook(exc, value, tb)

    except ImportError:
        print("Can't load your things")
        print("Either exit here, or perform remedial actions")
        exit()

    return full_trace

def excepthook(exc, value, tb):
    formatted = format_exception(exc, value, tb)
    #write_stream(formatted)

sys.excepthook = excepthook




logging.setLoggerClass(BetExcLogger)
patch_logging()


if hasattr(sys, 'ps1'):
    print('WARNING: better_exceptions will only inspect code from the command line\n'
          '         when using: `python -m better_exceptions\'. Otherwise, only code\n'
          '         loaded from files will be inspected!', file=sys.stderr)
