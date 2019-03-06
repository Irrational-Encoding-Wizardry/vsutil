"""
VSUtil. A collection of general-purpose Vapoursynth functions to be reused in modules and scripts.
"""
import ast
from functools import reduce
import re
from typing import Any, List

import vapoursynth as vs

core = vs.core


def get_subsampling(clip: vs.VideoNode) -> str:
    """
    Returns the subsampling of a clip in human-readable format.
    """
    if clip.format.subsampling_w == 1 and clip.format.subsampling_h == 1:
        css = '420'
    elif clip.format.subsampling_w == 1 and clip.format.subsampling_h == 0:
        css = '422'
    elif clip.format.subsampling_w == 0 and clip.format.subsampling_h == 0:
        css = '444'
    elif clip.format.subsampling_w == 2 and clip.format.subsampling_h == 2:
        css = '410'
    elif clip.format.subsampling_w == 2 and clip.format.subsampling_h == 0:
        css = '411'
    elif clip.format.subsampling_w == 0 and clip.format.subsampling_h == 1:
        css = '440'
    else:
        raise ValueError('Unknown subsampling')
    return css


def get_depth(clip: vs.VideoNode) -> int:
    """
    Returns the bitdepth of a clip as an integer.
    """
    return clip.format.bits_per_sample


def iterate(base, function, count):
    """
    Utility function that executes a given function for a given number of times.
    """
    return reduce(lambda v,_: function(v), range(count), base)


def insert_clip(clip: vs.VideoNode, insert: vs.VideoNode, start_frame: int) -> vs.VideoNode:
    """
    Convenience method to insert a shorter clip into a longer one.
    The inserted clip cannot go beyond the last frame of the source clip or an exception is raised.
    """
    if start_frame == 0:
        return insert + clip[insert.num_frames:]
    pre = clip[:start_frame]
    frame_after_insert = start_frame + insert.num_frames
    if frame_after_insert > clip.num_frames:
        raise ValueError('Inserted clip is too long')
    if frame_after_insert == clip.num_frames:
        return pre + insert
    post = clip[start_frame + insert.num_frames:]
    return pre + insert + post


def fallback(value, fallback_value):
    """
    Utility function that returns a value or a fallback if the value is None.
    """
    return fallback_value if value is None else value


def get_y(clip: vs.VideoNode) -> vs.VideoNode:
    """
    Helper to get the luma of a VideoNode.
    """
    return core.std.ShufflePlanes(clip, 0, vs.GRAY)


def split(clip: vs.VideoNode) -> list:
    """
    Returns a list of planes for the given input clip.
    """
    return [core.std.ShufflePlanes(clip, x, colorfamily=vs.GRAY) for x in range(clip.format.num_planes)]


def join(planes: list, family=vs.YUV) -> vs.VideoNode:
    """
    Joins the supplied list of planes into a YUV video node.
    """
    return core.std.ShufflePlanes(clips=planes, planes=[0], colorfamily=family)


class ExprStr(ast.NodeVisitor):
    """
    Drop-in wrapper for Expr() string in infix form.

    Usage:

    ``core.std.Expr([clip1, clip2], ExprStr('x * 0.5 + y * 0.5'))``

    All operators and functions of Expr are supported, but input string must contain a valid Python expression, therefore syntax slightly differs:
    1. Parentheses ``()`` are supported
    2. Equality operator is ``==``
    3. Python conditional expression ``b if a else c`` is used for conditional operator
    
    It should be noted that though chaining of comparison operators is syntactically correct, it's semantics completely differs for Python and Expr interpreter.

    More examples:

    ``>>> print(ExprStr('swap(sqrt(a) * (0 if b < 100 else c), e)'))``

    ``a sqrt b 100 < 0 c ? * e swap``

    ``>>> print(ExprStr('a > b < c >= d'))``

    ``a b > c < d >=``
    """

    variables = 'abcdefghijklmnopqrstuvwxyz'

    # Available operators and their Expr respresentation.
    # Conditional operator handled separately in visit_IfExp()
    operators = {
        ast.Add:  '+',
        ast.Sub:  '-',
        ast.Mult: '*',
        ast.Div:  '/',

        ast.Eq:   '=',
        ast.Gt:   '>',
        ast.Lt:   '<',
        ast.GtE: '>=',
        ast.LtE: '<=',
    }

    # Avaialable fixed-name functions and number of their arguments
    functions = {
        'abs' : 1,
        'exp' : 1,
        'log' : 1,
        'not' : 1,
        'sqrt': 1,

        'and' : 2,
        'max' : 2,
        'min' : 2,
        'or'  : 2,
        'pow' : 2,
        'xor' : 2,
    }

    # Available functions with names defined as regexp and number of their arguments
    functions_re = {
        re.compile(r'dup\d*') : 1,
        re.compile(r'swap\d*'): 2,
    }

    def __init__(self, input_string: str):
        self.stack: List[str] = []
        # 'eval' mode takes care of assignment operator
        self.visit(ast.parse(input_string, mode='eval'))

    def visit_Num(self, node: ast.Num) -> None:
        self.stack.append(str(node.n))

    def visit_Name(self, node: ast.Name) -> None:
        if (len(node.id) > 1
                or node.id not in self.variables):
            raise SyntaxError(
                f'ExprStr: clip name \'{node.id}\' is not valid.')

        self.stack.append(node.id)

    def visit_Compare(self, node: ast.Compare) -> Any:
        for i in range(len(node.ops) - 1, -1, -1):
            if type(node.ops[i]) not in self.operators:
                raise SyntaxError(
                    f'ExprStr: operator \'{type(node.ops[i])}\' is not supported.')

            self.stack.append(self.operators[type(node.ops[i])])

            self.visit(node.comparators[i])
            
        self.visit(node.left)

    def visit_UnaryOp(self, node: ast.UnaryOp) -> Any:
        raise SyntaxError(
            'ExprStr: arithmetical operators taking one argument are not allowed.')

    def visit_BinOp(self, node: ast.BinOp) -> Any:
        if type(node.op) not in self.operators:
            raise SyntaxError(
                f'ExprStr: operator \'{type(node.op)}\' is not supported.')

        self.stack.append(self.operators[type(node.op)])

        self.visit(node.right)
        self.visit(node.left)

    def visit_Call(self, node: ast.Call) -> Any:
        is_re_function = False
        args_required  = 0
        if node.func.id not in self.functions:
            for pattern, args_count in self.functions_re.items():
                if pattern.fullmatch(node.func.id):
                    is_re_function = True
                    args_required = args_count
                    break
            
            if not is_re_function:
                raise SyntaxError(
                    f'ExprStr: function \'{node.func.id}\' is not supported.')

        if not is_re_function:
            args_required = self.functions[node.func.id]

        if len(node.args) != args_required:
            raise SyntaxError('ExprStr: function \'{}\' takes exactly {} arguments, but {} provided.'
                              .format(node.func.id, args_required, len(node.args)))

        self.stack.append(node.func.id)

        for arg in node.args[::-1]:
            self.visit(arg)

    def visit_IfExp(self, node: ast.IfExp) -> Any:
        self.stack.append('?')

        self.visit(node.orelse)
        self.visit(node.body)
        self.visit(node.test)

    def __str__(self) -> str:
        return ' '.join(self.stack[::-1])
