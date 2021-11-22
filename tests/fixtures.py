import pytest
from vN import GitRepo
from vN.shell import bash


@pytest.fixture(scope='function')
def git_repo(tmpdir):
    root = str(tmpdir.realpath())
    bash("""
        set -euo pipefail

        git init
        git branch | grep -q main || git checkout -b main

        echo Hello World > README.md
        git add README.md
        git commit -m 'initial commit'

        git tag v1
    """, cwd=root)
    return GitRepo(root)
