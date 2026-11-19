"""第 61 批：关卡流送（level streaming）核心判定。

针对斜向跨越边界时邻格未预加载、渲染/物理异步不同步、HLOD 接缝双份
几何、世界原点重定位坐标错位、导航网格重建失效、音频灯光整片静音、
字节预算超支、跨格引用悬挂、任务格加载靠后、区域状态丢失、多人位置
仲裁、加载失败无重试、实体表互相覆盖等问题，提供纯函数判定逻辑。
"""

# HLOD 父代理（合并体）与子节点（完整几何）的切换距离。
# 远处用 parent 合并代理，贴近后切换到 child 完整几何。
HLOD_DISTANCE = 100.0

# 任务优先级中任务权重的千位基数：任务号越大优先级越高，距离只在同
# 任务号内做次级排序，保证任务目标所在格不会被纯距离排序压到最后。
MISSION_WEIGHT = 1000


def neighbor_cells(cell, radius):
    """邻格预载：返回以 cell 为中心、切比雪夫半径 radius 内的全部格。

    按 (dy, dx) 行优先顺序返回，保证确定性。radius=0 时只返回中心格，
    使斜向跨越边界时对角相邻格也会被纳入预加载集合，而不是只看包围盒
    距离触发当前格。
    """
    cx, cy = cell
    r = int(radius)
    return [
        (cx + dx, cy + dy)
        for dy in range(-r, r + 1)
        for dx in range(-r, r + 1)
    ]


def physics_ready(render, physics):
    """物理同步：渲染网格与碰撞体两条异步链路都就绪才允许落地。

    任一链路未就绪时该格视为不可交互，避免“看得见地形、踩上去是空
    气”以及物理后到时把角色弹回原位。
    """
    return bool(render and physics)


def hlod_choice(parent, child, distance):
    """HLOD 选择：距离远用 parent 合并代理，贴近后用 child 完整几何。

    切换点两侧只返回其中一个节点，杜绝父节点与子节点同时可见造成的
    接缝双份几何。
    """
    if distance >= HLOD_DISTANCE:
        return parent
    return child


def rebase(origin, cell):
    """原点换算：世界原点重定位后，把格坐标换算到新原点的相对坐标。

    新坐标 = 格坐标 - 原点偏移，分量逐轴相减，避免重定位后远处格子
    整体偏移。
    """
    ox, oy = origin
    cx, cy = cell
    return (cx - ox, cy - oy)


def navmesh_version(version, rebuild):
    """导航重建：地形流送触发重建时导航网格版本号 +1。

    角色持有的旧版本路径随版本失效，需要按新版本重新寻路，避免路径
    中途指向已卸载的地形。
    """
    if rebuild:
        return version + 1
    return version


def audio_light_ready(audio, light):
    """音频灯光：音频区域与灯光探针都加载完成才算该格氛围就绪。

    两者随场景异步加载，任一缺失都不宣告完成，防止跨边界时整片静音
    或探针跳变。
    """
    return bool(audio and light)


def byte_budget(size, limit):
    """字节预算：按实际字节数（而非格子数）判定是否在内存预算内。

    贴图尺寸不同的格子占用差异很大，size <= limit 才允许加载。
    """
    return bool(size <= limit)


def has_refs(refs):
    """跨格引用：判断一个格是否仍被外部引用（引用计数或引用集合）。

    refs 既可以是数值型引用计数，也可以是引用集合；为 0/空时才允许
    卸载，防止传送门等跨格指针悬挂到已卸载的旧格。
    """
    if isinstance(refs, (int, float)) and not isinstance(refs, bool):
        return bool(refs > 0)
    return bool(len(refs) > 0)


def mission_priority(distance, mission):
    """任务优先：合并任务权重与距离的流送优先级（值小者优先加载）。

    mission * 1000 + distance：任务号主导，距离仅在同一任务内排序，
    确保任务目标所在格不会因距离远而排在最后。
    """
    return mission * MISSION_WEIGHT + distance


def region_saved(cell, saved):
    """区域存档：判断某格状态是否已包含在存档中。

    saved 既可以是单个已存档格（tuple），也可以是已存档格的集合
    （list/set/frozenset）；保存范围须覆盖离开的旧区域，回到旧格时
    状态才可恢复。注意 tuple 本身就是格坐标，按单个格比较。
    """
    if isinstance(saved, (list, set, frozenset)):
        return bool(cell in saved)
    return bool(cell == saved)


def multiplayer_owner(positions):
    """多人位置：选出离世界原点最近的玩家所在格作为流送仲裁锚点。

    服务器不再只以主机位置为准，而是取所有玩家位置中到原点平方距离
    最小者，使分散在不同格的多玩家共享一致的流送中心。
    """
    return min(positions, key=lambda p: p[0] * p[0] + p[1] * p[1])


def retry_allowed(failures, max_retry):
    """失败重试：失败次数未超过上限时允许重试。

    异步加载失败后按上限自动重试，避免格子因一次失败成为永久空洞；
    failures < max_retry 时返回 True。
    """
    return bool(failures < max_retry)


def entity_isolation(stream_id, entity_id):
    """实体表隔离：为流送线程的实体生成带流送批次前缀的命名空间键。

    形如 "stream_id:entity_id"，不同流送批次的实体写入各自分区，
    加载完成回灌主线程时不会互相覆盖共享实体表。
    """
    return f"{stream_id}:{entity_id}"


def unload_age(last_used, now):
    """卸载延迟：返回格自上次使用以来经历的时长。"""
    return last_used - now


def cross_ref(cell_a, cell_b):
    """跨格引用判定：两个格是否边/角相邻（切比雪夫距离为 1）。

    相邻格之间可能存在传送门等跨格引用，卸载其中一个前需要用本判定
    检查另一个格；同一格返回 False。
    """
    if cell_a == cell_b:
        return False
    ax, ay = cell_a
    bx, by = cell_b
    return max(abs(ax - bx), abs(ay - by)) == 1
