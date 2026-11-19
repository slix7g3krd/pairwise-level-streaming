"""第 61 批：跨过峡谷边界，下一块地形已经显示，碰撞却还是空气，走两步又突然被..."""

def neighbor_cells(cell, radius):
    """邻格预载。"""
    raise NotImplementedError("TODO: neighbor_cells")

def physics_ready(render, physics):
    """物理同步。"""
    raise NotImplementedError("TODO: physics_ready")

def hlod_choice(parent, child, distance):
    """HLOD 选择。"""
    raise NotImplementedError("TODO: hlod_choice")

def rebase(origin, cell):
    """原点换算。"""
    raise NotImplementedError("TODO: rebase")

def navmesh_version(version, rebuild):
    """导航重建。"""
    raise NotImplementedError("TODO: navmesh_version")

def audio_light_ready(audio, light):
    """音频灯光。"""
    raise NotImplementedError("TODO: audio_light_ready")

def byte_budget(size, limit):
    """字节预算。"""
    raise NotImplementedError("TODO: byte_budget")

def has_refs(refs):
    """跨格引用。"""
    raise NotImplementedError("TODO: has_refs")

def mission_priority(distance, mission):
    """任务优先。"""
    raise NotImplementedError("TODO: mission_priority")

def region_saved(cell, saved):
    """区域存档。"""
    raise NotImplementedError("TODO: region_saved")

def multiplayer_owner(positions):
    """多人位置。"""
    raise NotImplementedError("TODO: multiplayer_owner")

def retry_allowed(failures, max_retry):
    """失败重试。"""
    raise NotImplementedError("TODO: retry_allowed")

def entity_isolation(stream_id, entity_id):
    """实体表隔离。"""
    raise NotImplementedError("TODO: entity_isolation")

def unload_age(last_used, now):
    """卸载延迟。"""
    raise NotImplementedError("TODO: unload_age")

def cross_ref(cell_a, cell_b):
    """跨格引用判定。"""
    raise NotImplementedError("TODO: cross_ref")
