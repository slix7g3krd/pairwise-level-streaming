import pytest
from gameplay import level_streaming as mod

CASES = [
    ("neighbor", 'm.neighbor_cells((0, 0), 0) == [(0, 0)]'),
    ("physics", 'm.physics_ready(True, True) is True'),
    ("physics_false", 'm.physics_ready(True, False) is False'),
    ("hlod", 'm.hlod_choice("parent", "child", 150.0) == "parent"'),
    ("rebase", 'm.rebase((10.0, 10.0), (2.0, 3.0)) == approx((-8.0, -7.0))'),
    ("navmesh", 'm.navmesh_version(2, True) == 3'),
    ("audio_light", 'm.audio_light_ready(True, True) is True'),
    ("budget", 'm.byte_budget(10, 10) is True'),
    ("refs", 'm.has_refs(1) is True'),
    ("mission", 'm.mission_priority(5, 2) == 2005'),
    ("region", 'm.region_saved((0, 0), (0, 0)) is True'),
    ("owner", 'm.multiplayer_owner([(3, 4), (3, 2)]) == (3, 2)'),
    ("retry", 'm.retry_allowed(2, 3) is True'),
    ("entity", 'm.entity_isolation("s", "e") == "s:e"'),
    ("age", 'm.unload_age(10, 4) == 6')
]

@pytest.mark.parametrize("name,expr", CASES, ids=[c[0] for c in CASES])
def test_contract(name, expr):
    assert eval(expr, {"m": mod, "approx": pytest.approx})
