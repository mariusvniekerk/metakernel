# Copyright (c) Calico Development Team.
# Distributed under the terms of the Modified BSD License.
# http://calicoproject.org/

import sys
import os
from jupyter_kernel import Magic, option
try:
    import jedi
except ImportError:
    jedi = None
else:
    from jedi import Interpreter
    from jedi.api.helpers import completion_parts
    from jedi.parser.user_context import UserContext


class PythonMagic(Magic):
    env = {}

    def line_python(self, *args):
        """%python CODE - evaluate code as Python"""
        code = " ".join(args)
        self.retval = self.eval(code)

    def eval(self, code):
        try:
            return eval(code.strip(), self.env)
        except:
            try:
                exec(code.strip(), self.env)
            except Exception as exc:
                return "Error: " + str(exc)
        if "retval" in self.env:
            return self.env["retval"]

    @option(
        "-e", "--eval_output", action="store_true", default=False,
        help="Use the retval value from the Python cell as code in the kernel language."
    )
    def cell_python(self, eval_output=False):
        """%%python - evaluate contents of cell as Python"""
        if self.code.strip():
            if eval_output:
                self.eval(self.code)
                self.code = str(self.env["retval"]) if ("retval" in self.env and 
                                                        self.env["retval"] != None) else ""
                self.retval = None
                self.env["retval"] = None
                self.evaluate = True
            else:
                self.retval = self.eval(self.code)
                self.env["retval"] = None
                self.evaluate = False

    def post_process(self, retval):
        if retval:
            return retval
        else:
            return self.retval

    def get_completions(self, text):
        '''Get Python completions'''
        # https://github.com/davidhalter/jedi/blob/master/jedi/utils.py
        if jedi is None:
            return []

        interpreter = Interpreter(text, [self.env])
        path = UserContext(text, (1, len(text))).get_path_until_cursor()
        path, dot, like = completion_parts(path)
        before = text[:len(text) - len(like)]
        completions = interpreter.completions()

        completions = [before + c.name_with_symbols for c in completions]
        return completions

    def get_help_on(self, expr, level=0):
        """Implement basic help for functions"""
        if not expr:
            return ''

        last = expr.split()[-1]
        default = 'No help available for "%s"' % last

        parts = last.split('.')

        obj = self.env.get(parts[0], None)
        if not obj:
            return default

        for p in parts[1:]:
            obj = getattr(obj, p, None)
            if not obj:
                return default

        return getattr(obj, '__doc__', default)


def register_magics(kernel):
    kernel.register_magics(PythonMagic)

