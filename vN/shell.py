import os
import sys
import subprocess
from typing import List
from tempfile import NamedTemporaryFile

from .exceptions import vNError

class vNShellError(vNError):
    pass


def shell(cmd: List[str], **proc_kw) -> List[str]:
    """Runs the given command and returns its stdout as a list of lines."""
    cmd = list(map(str, cmd))
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        **proc_kw
    )
    out, err = proc.communicate()
    if proc.returncode != 0:
        sys.stderr.write(err)
        raise vNShellError('Command failed: %s\n%s' % (' '.join(cmd), err))

    lines = [line.rstrip() for line in out.split('\n')]
    return [line for line in lines if line]


def bash(script: str, **proc_kw):
    with NamedTemporaryFile() as f:
        f.write(script.encode('utf-8'))
        f.flush()
        return shell(['bash', f.name], **proc_kw)
