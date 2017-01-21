#=============================================================================
# FILE: rct.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
#=============================================================================

import re
import subprocess
import tempfile

from .base import Base
from deoplete.util import getlines

class Source(Base):
    def __init__(self, vim):
        Base.__init__(self, vim)

        self.name = 'rct'
        self.filetypes = ['ruby']
        self.mark = '[R]'
        self.rank = 500
        self.min_pattern_length = 0
        self.executable_rct = self.vim.call('executable', 'rct-complete')
        self.encoding = self.vim.eval('&encoding')

    def get_complete_position(self, context):
        m = re.search(r'(?<=\.)[a-zA-Z_?!]*', context['input'])
        if m:
            return m.start()
        return -1

    def gather_candidates(self, context):
        if not self.executable_rct:
            return []

        words = []
        with tempfile.NamedTemporaryFile(mode='w') as f:
            f.writelines(getlines(self.vim))
            f.flush()
            try:
                words = [x.decode(self.encoding).split('\t') for x in
                         subprocess.check_output(
                             ['rct-complete', '--completion-class-info',
                              '--dev', '--fork',
                              '--line=' + str(context['position'][1]),
                              '--column=' + str(context['complete_position']),
                              f.name
                              ]).splitlines()]
            except subprocess.CalledProcessError:
                return []
        return [{'word': x[0], 'menu': x[1]} for x in words]
