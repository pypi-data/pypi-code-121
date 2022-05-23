from __future__ import annotations

import ast


async def sexec(script: str, globals_=None, locals_=None):
   exec_context = {**globals_, **locals_}
   stmts = list(ast.iter_child_nodes(ast.parse(script)))
   if not stmts:
      return None
   if isinstance(stmts[-1], ast.Expr):
      if len(stmts) > 1:
         # noinspection PyArgumentList
         exec(compile(ast.Module(body=stmts[:-1], type_ignores=[]), filename="<ast>", mode="exec"), exec_context)
      # noinspection PyArgumentList
      return eval(compile(ast.Expression(body=stmts[-1].value), filename="<ast>", mode="eval"), exec_context)
   else:
      exec(script, globals_, locals_)


async def aexec(script: str, globals_=None, locals_=None):
   exec_context = {**globals_, **locals_}
   exec(
      f'async def __ex(): ' +
      ''.join(f'\n {li}' for li in script.split('\n')), exec_context
   )
   return await exec_context['__ex']()
