from railbound.model import B_Road, B_Switch, Direction


# fix始终有,在default和switch切换
def switch_helper(fix: Direction, default: Direction, switch: Direction):
    return B_Switch(
        entry=[fix, default, switch],
        trans_group=[
            {
                fix: default,
                default: fix,
                switch: default,
            },
            {
                fix: switch,
                switch: fix,
                default: switch,
            },
        ],
    )


def switch_rdl_l():  # 右下左，默认是左
    return switch_helper(Direction.Down, Direction.Left, Direction.Right)


def switch_url_r():  # 上右左, 默认是右
    return switch_helper(Direction.Up, Direction.Right, Direction.Left)


def road_helper2(a: Direction, b: Direction):
    return B_Road(entry=[a, b], trans={a: b, b: a})


# a-1,a,a+1, main=-1/+1 表示连续的三个, main表示a的转向
def road_helper3(a: Direction, main: int):
    l = (a - 1 + 4) % 4
    r = (a + 1 + 4) % 4
    if main == -1:
        return B_Road(entry=[l, a, r], trans={a: l, l: a, r: l})
    elif main == 1:
        return B_Road(entry=[l, a, r], trans={a: r, l: r, r: a})
    else:
        assert False


def road_ud():
    return road_helper2(Direction.Up, Direction.Down)


def road_ur():
    return road_helper2(Direction.Up, Direction.Right)


def road_rl():
    return road_helper2(Direction.Right, Direction.Left)
