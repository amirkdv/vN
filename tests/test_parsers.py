import pytest
from vN import vNError
from vN import GitState, RC_ID


def test_state_parse_clean():
    state = GitState.parse('v14-0-g12345678')
    assert state.latest == 14
    assert state.n_commits == 0
    assert state.sha == '12345678'
    assert state.dirty is False


def test_state_equality():
    assert GitState.parse('v14-0-g12345678') == GitState.parse('v14-0-g12345678')
    assert GitState.parse('v14-2-g12345678') != GitState.parse('v14-0-g12345678')
    assert GitState.parse('v13-0-g12345678') != GitState.parse('v14-0-g12345678')
    assert GitState.parse('v14-0-g87654321') != GitState.parse('v14-0-g12345678')


@pytest.mark.parametrize('invalid_state', [
    'v12-g1234578',
    'v12-rc-12345678',
    'v1.1-0-g1234578',
])
def test_parse_state_invalid(invalid_state):
    with pytest.raises(vNError):
        GitState.parse(invalid_state)


def test_state_equality_dirty():
    dirty = 'v14-0-g12345678-dirty'
    assert GitState.parse(dirty) != GitState.parse(dirty)


def test_state_parse_with_n():
    state = GitState.parse('v3-12-gabcdef12')
    assert state.latest == 3
    assert state.n_commits == 12
    assert state.sha == 'abcdef12'
    assert state.dirty is False


def test_state_parse_dirty():
    state = GitState.parse('v13-22-g87654321-dirty')
    assert state.latest == 13
    assert state.n_commits == 22
    assert state.sha == '87654321'
    assert state.dirty is True


@pytest.mark.parametrize('state,rc_id', [
    ('v4-0-g87654321', 'v4-rc-87654321'),
    ('v4-22-g87654321', 'v5-rc-87654321'),
])
def test_rc_id_with_n(state, rc_id):
    state = GitState.parse(state)
    assert rc_id == str(state.rc_id)


@pytest.mark.parametrize('state,rc_id', [
    ('v4-22-g87654321', 'v5-rc-87654321'),
    ('v4-0-g12345678', 'v4-rc-12345678'),
])
def test_parse_rc_id(state, rc_id):
    state = GitState.parse(state)
    rc_id = RC_ID.parse(rc_id)
    assert rc_id == state.rc_id
    assert str(rc_id) == str(state.rc_id)
