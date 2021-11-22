import re
from pathlib import Path
from typing import List

from .shell import shell
from .shell import bash
from .exceptions import vNError


class GitRepo:
    def __init__(self, root: str = '.'):
        self.root = Path(root)
        if not (self.root / '.git').exists():
            raise vNError("There seems to be no git repo at %s" % self.root)

    def git_exec(self, args) -> List[str]:
        cmd = ['git', '-C', self.root, *args]
        return shell(cmd)

    def bash_exec(self, script: str):
        bash(script, cwd=str(self.root))

    def describe(self, commitish: str = None) -> str:
        cmd = ['describe', '--tag', '--long']
        if commitish:
            cmd += [commitish]
        else:
            cmd += ['--dirty']

        return self.git_exec(cmd)[0]

    def state(self, commitish: str = None) -> 'GitState':
        return GitState.parse(self.describe(commitish))

    def release_tags(self) -> List[str]:
        tags = self.git_exec(['tag', '-l'])
        return [tag for tag in tags if re.match('^v[0-9]+$', tag)]

    def release_exists(self, release: int) -> bool:
        return 'v%d' % release in self.release_tags

    def release_rc_ids(self) -> List['RC_ID']:
        tags = self.release_tags()
        return [self.state(tag).rc_id for tag in tags]

    def changelog(self, commitish_from: str, commitish_to: str):
        raise NotImplementedError

    def latest_release(self):
        return self.state().latest


class GitState:
    def __init__(self,
        latest: int,
        n_commits: int,
        sha: str,
        dirty: bool
    ):
        self.latest = int(latest)
        self.n_commits = int(n_commits)
        self.sha = str(sha)
        self.dirty = bool(dirty)

        self.rc_id = RC_ID(
            sha=self.sha,
            release=self.latest + (1 if self.n_commits > 0 else 0),
            dirty=self.dirty,
        )

    def __eq__(self, other):
        if self.dirty or other.dirty:
            return False

        return self.rc_id == other.rc_id

    def __str__(self):
        return 'GitState(%s)' % self.sha

    @classmethod
    def parse(cls, git_description) -> 'GitState':
        # eg v3-5-gf88a34cf
        #            v    3          -    5             -g    f88a34cf
        pattern = r'^v(?P<latest>\d+)-(?P<n_commits>\d+)-g(?P<sha>[0-9a-f]+)(?P<dirty>-dirty)?$'
        match = re.match(pattern, git_description)
        if match is None:
            raise vNError("Invalid git version string: " + git_description)

        vdict = match.groupdict()
        return cls(**vdict)


class RC_ID:
    def __init__(self,
        release: int,
        sha: str,
        dirty: bool
    ):
        self.release = int(release)
        self.sha = str(sha)
        self.dirty = bool(dirty)

    @classmethod
    def parse(cls, rc_id: str, dirty_ok=False) -> 'RC_ID':
        rc_id = str(rc_id)
        # eg v3-rc-f88a34cf
        #            v    3           -rc- f88a34cf
        pattern = r'^v(?P<release>\d+)-rc-(?P<sha>[0-9a-f]+)(?P<dirty>-dirty)?$'
        match = re.match(pattern, rc_id)
        if match is None:
            raise vNError("Invalid RC id: " + rc_id)

        vdict = match.groupdict()
        if vdict['dirty'] and not dirty_ok:
            raise vNError("RC id is dirty: " + rc_id)

        return cls(**vdict)

    def __eq__(self, other):
        if self.dirty or other.dirty:
            return False

        return self.sha == other.sha and self.release == other.release

    def __str__(self):
        return 'v{release}-rc-{sha}{dirty}'.format(
            release=self.release,
            sha=self.sha,
            dirty='-dirty' if self.dirty else '',
        )
