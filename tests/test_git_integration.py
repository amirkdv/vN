import pytest
from .fixtures import *
from vN import vNError


def test_init_state(git_repo):
    state = git_repo.state()
    assert state.latest == 1
    assert state.n_commits == 0
    assert state.dirty is False
    assert state.rc_id.release == 1


def test_invalid_state(git_repo):
    git_repo.state('v1')
    with pytest.raises(vNError):
        git_repo.state('v2')


def test_dirty_state(git_repo):
    git_repo.bash_exec("""
        echo 'feature 1' >> features.txt
        git add features.txt
        git commit -m 'add feature 1'

        echo 'feature 2' >> features.txt
    """)
    state = git_repo.state()
    assert state.latest == 1
    assert state.n_commits == 1
    assert state.dirty is True
    assert state.rc_id.release == 2
    assert state.rc_id.dirty is True


def test_new_commit(git_repo):
    git_repo.bash_exec("""
        echo 'feature 1' >> features.txt
        git add features.txt
        git commit -m 'add feature 1'
    """)
    state = git_repo.state()
    assert state.latest == 1
    assert state.n_commits == 1
    assert state.dirty is False
    assert state.rc_id.release == 2


def test_commit_and_tag(git_repo):
    git_repo.bash_exec("""
        echo 'feature 1' >> features.txt
        git add features.txt
        git commit -m 'add feature 1'
    """)
    old_state = git_repo.state()

    git_repo.bash_exec("""
        git tag v2
    """)
    new_state = git_repo.state()

    assert new_state.latest == 2
    assert new_state.n_commits == 0
    assert new_state.dirty is False
    assert new_state.rc_id.release == 2

    assert old_state.sha == new_state.sha
    assert old_state.rc_id == new_state.rc_id


def test_latest_release(git_repo):
    assert git_repo.latest_release() == 1

    git_repo.bash_exec("""
        echo 'feature 1' >> features.txt
        git add features.txt
        git commit -m 'add feature 1'
    """)
    assert git_repo.latest_release() == 1

    git_repo.bash_exec("""
        git tag v3
    """)
    assert git_repo.latest_release() == 3


def test_release_tags(git_repo):
    assert git_repo.release_tags() == ['v1']

    git_repo.bash_exec("""
        echo 'feature 1' >> features.txt
        git add features.txt
        git commit -m 'add feature 1'
    """)
    assert git_repo.release_tags() == ['v1']

    git_repo.bash_exec("""
        git tag v2
    """)
    assert git_repo.release_tags() == ['v1', 'v2']

    git_repo.bash_exec("""
        git tag v2.1
    """)
    assert git_repo.release_tags() == ['v1', 'v2']

    git_repo.bash_exec("""
        git tag v4
    """)
    assert git_repo.release_tags() == ['v1', 'v2', 'v4']


def test_release_rc_ids(git_repo):
    assert git_repo.release_tags() == ['v1']

    git_repo.bash_exec("""
        echo 'feature 1' >> features.txt
        git add features.txt
        git commit -m 'add feature 1'
    """)
    rc_ids = git_repo.release_rc_ids()
    assert len(rc_ids) == 1
    assert rc_ids[0].release == 1

    git_repo.bash_exec("""
        git tag v2
    """)
    rc_ids = git_repo.release_rc_ids()
    assert len(rc_ids) == 2
    assert rc_ids[1].release == 2
