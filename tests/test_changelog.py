from .fixtures import *


def test_changelog_non_merge_commit(git_repo):
    state = git_repo.state()

    git_repo.bash_exec("""
        echo 'feature 1' >> features.txt
        git add features.txt
        git commit -m 'add feature 1'
    """)

    changelog = list(git_repo.changelog('v1'))
    assert len(changelog) == 0


def test_changelog_merge_commit(git_repo):
    state = git_repo.state()

    git_repo.bash_exec("""
        git checkout -b feature/1
        echo 'feature 1' >> features.txt
        git add features.txt
        git commit -m 'add feature 1'

        git checkout main
        git merge --no-ff feature/1 -m 'Merge feature/1'
    """)

    changelog = list(git_repo.changelog('v1'))
    assert len(changelog) == 1
    assert changelog[0]['sha'].startswith(git_repo.state().sha)
    assert changelog[0]['message'][0] == 'Merge feature/1'
