# Based on utils.py by Jeremy Siek
# Adapted by permission from https://github.com/IUCompilerCourse/python-student-support-code
# See EOC-LICENSE for details
import os
import sys
import ast
from ast import ( 
    Module, Expr, Pass, Assign, AnnAssign, Return, Name, Constant, Add, Sub, Mult, And, Or,
    USub, Not, UnaryOp, Call, If, IfExp, While, Compare, Eq, NotEq, Lt, LtE, Gt, GtE, Is, Tuple, Subscript, List, BinOp, BoolOp
)

from dataclasses import dataclass

indent_amount = 2

def indent_stmt() -> str:
    return " " * indent_amount


def indent() -> None:
    global indent_amount
    indent_amount += 2


def dedent() -> None:
    global indent_amount
    indent_amount -= 2

def label_name(n: str) -> str:
    if sys.platform == "darwin":
        return '_' + n
    else:
        return n

def strip_module(node:ast.AST) -> list[ast.stmt]:
   match node:
       case Module(body=body):
           return body
       case ast.stmt():
           return [node]
       case _:
           raise ValueError(f"Expected Module or stmt, got {type(node)}")

def get_first_expr(node: ast.AST) -> ast.expr:
    match node:
        case Module(body=[Expr(value=e),*rest]):
            return e
        case Expr(value=e):
            return e
        case _:
            raise ValueError(f"Expected Module or Expr, got {type(node)}")

def parse_stmts(source: str) -> list[ast.stmt]:
    """parse a string into a list of statements"""
    return strip_module(ast.parse(source))

def parse_expr(source: str) -> ast.expr:
    """parse a string into an expression"""
    return get_first_expr(ast.parse(source))

################################################################################
# Generating unique names
################################################################################

name_id = 0


def generate_name(name: str) -> str:
    global name_id
    ls = name.split('.')
    new_id = name_id
    name_id += 1
    return ls[0] + '.' + str(new_id)


def str_Module(self: Module) -> str:
    indent()
    body = ''.join([str(s) for s in self.body])
    dedent()
    return body


Module.__str__ = str_Module  # type: ignore[method-assign, assignment]


def repr_Module(self: Module) -> str:
    return 'Module(' + repr(self.body) + ')'


Module.__repr__ = repr_Module  # type: ignore[method-assign, assignment]


def str_Expr(self: Expr) -> str:
    return indent_stmt() + str(self.value) + '\n'


Expr.__str__ = str_Expr  # type: ignore[method-assign, assignment]


def repr_Expr(self: Expr) -> str:
    return indent_stmt() + 'Expr(' + repr(self.value) + ')'


Expr.__repr__ = repr_Expr  # type: ignore[method-assign, assignment]


def str_Pass(self: Pass) -> str:
    return indent_stmt() + 'pass' + '\n'


Pass.__str__ = str_Pass  # type: ignore[method-assign, assignment]


def repr_Pass(self: Pass) -> str:
    return indent_stmt() + 'Pass()'


Pass.__repr__ = repr_Pass  # type: ignore[method-assign, assignment]


def str_Assign(self: Assign) -> str:
    return indent_stmt() + str(self.targets[0]) + ' = ' + str(self.value) + '\n'


Assign.__str__ = str_Assign  # type: ignore[method-assign, assignment]


def repr_Assign(self: Assign) -> str:
    return indent_stmt() + 'Assign(' + repr(self.targets) + ', ' + repr(self.value) + ')'


Assign.__repr__ = repr_Assign  # type: ignore[method-assign, assignment]


def str_AnnAssign(self: AnnAssign) -> str:
    return indent_stmt() + str(self.target) + ' : ' + str(self.annotation) + ' = ' + str(self.value) + '\n'


AnnAssign.__str__ = str_AnnAssign  # type: ignore[method-assign, assignment]


def repr_AnnAssign(self: AnnAssign) -> str:
    return indent_stmt() + 'AnnAssign(' + repr(self.target) + ', ' \
           + repr(self.annotation) + ', ' + repr(self.value) + repr(self.simple) + ')'


AnnAssign.__repr__ = repr_AnnAssign  # type: ignore[method-assign, assignment]


def str_Return(self: Return) -> str:
    return indent_stmt() + 'return ' + str(self.value) + '\n'


Return.__str__ = str_Return  # type: ignore[method-assign, assignment]


def repr_Return(self: Return) -> str:
    return indent_stmt() + 'Return(' + repr(self.value) + ')'


Return.__repr__ = repr_Return  # type: ignore[method-assign, assignment]


def str_Name(self: Name) -> str:
    if hasattr(self, 'has_type'):
        return self.id + ':' + str(self.has_type)
    else:
        return self.id


Name.__str__ = str_Name  # type: ignore[method-assign, assignment]


def repr_Name(self: Name) -> str:
    return 'Name(' + repr(self.id) + ')'


Name.__repr__ = repr_Name  # type: ignore[method-assign, assignment]


def str_Constant(self: Constant) -> str:
    return str(self.value)


Constant.__str__ = str_Constant  # type: ignore[method-assign, assignment]


def repr_Constant(self: Constant) -> str:
    return 'Constant(' + repr(self.value) + ')'


Constant.__repr__ = repr_Constant  # type: ignore[method-assign, assignment]


def str_Add(self: Add) -> str:
    return '+'


Add.__str__ = str_Add  # type: ignore[method-assign, assignment]


def repr_Add(self: Add) -> str:
    return 'Add()'


Add.__repr__ = repr_Add  # type: ignore[method-assign, assignment]


def str_Sub(self: Sub) -> str:
    return '-'


Sub.__str__ = str_Sub  # type: ignore[method-assign, assignment]


def repr_Sub(self: Sub) -> str:
    return 'Sub()'


Sub.__repr__ = repr_Sub  # type: ignore[method-assign, assignment]


def str_Mult(self: Mult) -> str:
    return '*'


Mult.__str__ = str_Mult  # type: ignore[method-assign, assignment]


def repr_Mult(self: Mult) -> str:
    return 'Mult()'


Mult.__repr__ = repr_Mult  # type: ignore[method-assign, assignment]


def str_And(self: And) -> str:
    return 'and'


And.__str__ = str_And  # type: ignore[method-assign, assignment]


def repr_And(self: And) -> str:
    return 'And()'


And.__repr__ = repr_And  # type: ignore[method-assign, assignment]


def str_Or(self: Or) -> str:
    return 'or'


Or.__str__ = str_Or  # type: ignore[method-assign, assignment]


def repr_Or(self: Or) -> str:
    return 'Or()'


Or.__repr__ = repr_Or  # type: ignore[method-assign, assignment]


def str_BinOp(self: BinOp) -> str:
    return '(' + str(self.left) + ' ' + str(self.op) + ' ' + str(self.right) + ')'


BinOp.__str__ = str_BinOp  # type: ignore[method-assign, assignment]


def repr_BinOp(self: BinOp) -> str:
    return 'BinOp(' + repr(self.left) + ', ' + repr(self.op) + ', ' + repr(self.right) + ')'


BinOp.__repr__ = repr_BinOp  # type: ignore[method-assign, assignment]


def str_BoolOp(self: BoolOp) -> str:
    return '(' + str(self.values[0]) + ' ' + str(self.op) + ' ' + str(self.values[1]) + ')'


BoolOp.__str__ = str_BoolOp  # type: ignore[method-assign, assignment]


def repr_BoolOp(self: BoolOp) -> str:
    return repr(self.values[0]) + ' ' + repr(self.op) + ' ' + repr(self.values[1])


BoolOp.__repr__ = repr_BoolOp  # type: ignore[method-assign, assignment]


def str_USub(self: USub) -> str:
    return '-'


USub.__str__ = str_USub  # type: ignore[method-assign, assignment]


def repr_USub(self: USub) -> str:
    return 'USub()'


USub.__repr__ = repr_USub  # type: ignore[method-assign, assignment]


def str_Not(self: Not) -> str:
    return 'not'


Not.__str__ = str_Not  # type: ignore[method-assign, assignment]


def repr_Not(self: Not) -> str:
    return 'Not()'


Not.__repr__ = repr_Not  # type: ignore[method-assign, assignment]


def str_UnaryOp(self: UnaryOp) -> str:
    return str(self.op) + '(' + str(self.operand) + ')'


UnaryOp.__str__ = str_UnaryOp  # type: ignore[method-assign, assignment]


def repr_UnaryOp(self: UnaryOp) -> str:
    return 'UnaryOp(' + repr(self.op) + ', ' + repr(self.operand) + ')'


UnaryOp.__repr__ = repr_UnaryOp  # type: ignore[method-assign, assignment]


def str_Call(self: Call) -> str:
    return str(self.func) \
           + '(' + ', '.join([str(arg) for arg in self.args]) + ')'


Call.__str__ = str_Call  # type: ignore[method-assign, assignment]


def repr_Call(self: Call) -> str:
    return 'Call(' + repr(self.func) + ', ' + repr(self.args) + ')'


Call.__repr__ = repr_Call  # type: ignore[method-assign, assignment]


def str_If(self: If) -> str:
    header = indent_stmt() + 'if ' + str(self.test) + ':\n'
    indent()
    thn = ''.join([str(s) for s in self.body])
    els = ''.join([str(s) for s in self.orelse])
    dedent()
    return header + thn + indent_stmt() + 'else:\n' + els


If.__str__ = str_If  # type: ignore[method-assign, assignment]


def repr_If(self: If) -> str:
    return 'If(' + repr(self.test) + ', ' + repr(self.body) + ', ' + repr(self.orelse) + ')'


If.__repr__ = repr_If  # type: ignore[method-assign, assignment]


def str_IfExp(self: IfExp) -> str:
    return '(' + str(self.body) + ' if ' + str(self.test) + \
           ' else ' + str(self.orelse) + ')'


IfExp.__str__ = str_IfExp  # type: ignore[method-assign, assignment]


def repr_IfExp(self: IfExp) -> str:
    return 'IfExp(' + repr(self.test) + ', ' + repr(self.body) + \
        ', ' + repr(self.orelse) + ')'


IfExp.__repr__ = repr_IfExp  # type: ignore[method-assign, assignment]


def str_While(self: While) -> str:
    header = indent_stmt() + 'while ' + str(self.test) + ':\n'
    indent()
    body = ''.join([str(s) for s in self.body])
    dedent()
    return header + body


While.__str__ = str_While  # type: ignore[method-assign, assignment]


def repr_While(self: While) -> str:
    return 'While(' + repr(self.test) + ', ' + repr(self.body) + ', ' + repr(self.orelse) + ')'


While.__repr__ = repr_While  # type: ignore[method-assign, assignment]


def str_Compare(self: Compare) -> str:
    return str(self.left) + ' ' + str(self.ops[0]) + ' ' + str(self.comparators[0])


Compare.__str__ = str_Compare  # type: ignore[method-assign, assignment]


def repr_Compare(self: Compare) -> str:
    return 'Compare(' + repr(self.left) + ', ' + repr(self.ops) + ', ' \
           + repr(self.comparators) + ')'


Compare.__repr__ = repr_Compare  # type: ignore[method-assign, assignment]


def str_Eq(self: Eq) -> str:
    return '=='


Eq.__str__ = str_Eq  # type: ignore[method-assign, assignment]


def repr_Eq(self: Eq) -> str:
    return 'Eq()'


Eq.__repr__ = repr_Eq  # type: ignore[method-assign, assignment]


def str_NotEq(self: NotEq) -> str:
    return '!='


NotEq.__str__ = str_NotEq  # type: ignore[method-assign, assignment]


def repr_NotEq(self: NotEq) -> str:
    return 'NotEq()'


NotEq.__repr__ = repr_NotEq  # type: ignore[method-assign, assignment]


def str_Lt(self: Lt) -> str:
    return '<'


Lt.__str__ = str_Lt  # type: ignore[method-assign, assignment]


def repr_Lt(self: Lt) -> str:
    return 'Lt()'


Lt.__repr__ = repr_Lt  # type: ignore[method-assign, assignment]


def str_LtE(self: LtE) -> str:
    return '<='


LtE.__str__ = str_LtE  # type: ignore[method-assign, assignment]


def repr_LtE(self: LtE) -> str:
    return 'LtE()'


LtE.__repr__ = repr_LtE  # type: ignore[method-assign, assignment]


def str_Gt(self: Gt) -> str:
    return '>'


Gt.__str__ = str_Gt  # type: ignore[method-assign, assignment]


def repr_Gt(self: Gt) -> str:
    return 'Gt()'


Gt.__repr__ = repr_Gt  # type: ignore[method-assign, assignment]


def str_GtE(self: GtE) -> str:
    return '>='


GtE.__str__ = str_GtE  # type: ignore[method-assign, assignment]


def repr_GtE(self: GtE) -> str:
    return 'GtE()'


GtE.__repr__ = repr_GtE  # type: ignore[method-assign, assignment]


def str_Is(self: Is) -> str:
    return 'is'


Is.__str__ = str_Is  # type: ignore[method-assign, assignment]


def repr_Is(self: Is) -> str:
    return 'Is()'


Is.__repr__ = repr_Is  # type: ignore[method-assign, assignment]


def str_Tuple(self: Tuple) -> str:
    return '(' + ', '.join([str(e) for e in self.elts]) + ',)'


Tuple.__str__ = str_Tuple  # type: ignore[method-assign, assignment]


def repr_Tuple(self: Tuple) -> str:
    return 'Tuple(' + repr(self.elts) + ')'


Tuple.__repr__ = repr_Tuple  # type: ignore[method-assign, assignment]


def str_List(self: ast.List) -> str:
    return '[' + ', '.join([str(e) for e in self.elts]) + ']'


ast.List.__str__ = str_List  # type: ignore[method-assign, assignment]


def repr_List(self: ast.List) -> str:
    return 'List(' + repr(self.elts) + ')'


ast.List.__repr__ = repr_List  # type: ignore[method-assign, assignment]


def str_Subscript(self: Subscript) -> str:
    return str(self.value) + '[' + str(self.slice) + ']'


Subscript.__str__ = str_Subscript  # type: ignore[method-assign, assignment]


def repr_Subscript(self: Subscript) -> str:
    return 'Subscript(' + repr(self.value) + ', ' + repr(self.slice) \
           + ', ' + repr(self.ctx) + ')'


Subscript.__repr__ = repr_Subscript  # type: ignore[method-assign, assignment]