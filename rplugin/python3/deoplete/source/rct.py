#=============================================================================
# FILE: rct.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
#=============================================================================

import re
import subprocess
from subprocess import PIPE
import tempfile

from .base import Base
from deoplete.util import getlines, debug

class Source(Base):
    def __init__(self, vim):
        Base.__init__(self, vim)

        self.name = 'rct'
        self.filetypes = ['ruby']
        self.mark = '[R]'
        self.rank = 500
        self.executable_rct = self.vim.call('executable', 'rct-complete')
        self.encoding = self.vim.eval('&encoding')
        self.input_pattern = r'\.[a-zA-Z0-9_?!]*'

    def get_complete_position(self, context):
        m = re.search('[a-zA-Z0-9_?!]*$', context['input'])
        return m.start() if m else -1

    def gather_candidates(self, context):
        if not self.executable_rct:
            return []

        words = []
        line = context['position'][1]
        column = context['complete_position']
        cmd = [
                'rct-complete',
                '--completion-class-info',
                '--dev',
                '--fork',
                '--line=%s' % line,
                '--column=%s' % column
                ]
        buf = '\n'.join(getlines(self.vim)).encode(self.encoding)
        try:
            rct_proc = subprocess.run(cmd, check=True, input=buf, stdout=PIPE)
            output = rct_proc.stdout.splitlines()
            words = [x.decode(self.encoding).split('\t') for x in output]
        except subprocess.CalledProcessError:
            return []
        return [{'word': x[0], 'menu': x[1] if len(x) > 1 else ''}
                for x in words]
