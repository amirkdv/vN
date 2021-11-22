from .fixtures import *


def test_init_state(git_repo):
    state = git_repo.state()
    assert state.latest == 1
    assert state.n_commits == 0
    assert state.dirty is False
    assert state.rc_id.release == 1


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
