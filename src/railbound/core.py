import copy
import logging
from enum import Enum
import sys
from typing import Dict, List, Tuple
from pydantic import BaseModel

logger = logging.getLogger("railbound.core")

from .helper import (
    switch_rdl_l,
    switch_url_r,
    road_ud,
    road_rl,
    road_ur,
    road_helper2,
    road_helper3,
)
from .model import (
    BLOCK,
    B_Empty,
    B_Out,
    B_Switch,
    BlockEnum,
    Train,
    Direction,
    B_Block,
    B_Road,
    GAME_MAP,
)

d2graphic = {
    Direction.Up: "^",
    Direction.Down: "v",
    Direction.Left: "<",
    Direction.Right: ">",
}


def next_state(
    g: GAME_MAP, trains: List[Train], wait_train: int
) -> Tuple[GAME_MAP, List[Train], int]:
    # 似乎不需要 深拷贝直接改状态就好了?
    g = copy.deepcopy(g)
    trains = copy.deepcopy(trains)
    dij: Dict[Direction : Tuple[int, int]] = {
        Direction.Up: [-1, 0],
        Direction.Down: [1, 0],
        Direction.Left: [0, -1],
        Direction.Right: [0, 1],
    }
    for train in trains:
        if train.id < wait_train:
            continue
        i = train.i
        j = train.j
        d = train.d  # 车朝向右，那么就是走左入口进入
        in_d: Direction = (d + 2) % 4
        grid = g[i][j]
        if grid.t == BlockEnum.Road:
            assert isinstance(grid, B_Road)
            out_d = grid.trans[in_d]
        elif grid.t == BlockEnum.Switch:
            assert isinstance(grid, B_Switch)
            out_d = grid.trans_group[grid.trans_idx][in_d]
            grid.trans_idx = (grid.trans_idx + 1) % len(grid.trans_group)
        else:
            raise Exception(f"Wrong block type at {i},{j}")
        di, dj = dij[out_d]
        # print("\t ===== state =====")
        # dump(g, trains)
        # print("\t ===== state =====")
        if (out_d + 2) % 4 not in g[i + di][j + dj].entry:
            print(f"failed ({i},{j}) => ({i+di},{j+dj})")
            sys.exit(1)
        train.i = i + di
        train.j = j + dj
        train.d = out_d
    # 碰撞检测
    for i0 in range(len(trains)):
        if trains[i0].id < wait_train:
            continue
        for i1 in range(i0 + 1, len(trains)):
            if trains[i1].id < wait_train:
                continue
            if trains[i0].i == trains[i1].i and trains[i0].j == trains[i1].j:
                raise Exception(f"碰撞 {trains[i0].id},{trains[i1].id}")

    # out检测
    for train in trains:
        if train.id < wait_train:
            continue
        if g[train.i][train.j].t == BlockEnum.Out:
            if train.id == wait_train:
                wait_train += 1
            else:
                raise Exception(f"先跑到Out {train.id}")
    return g, trains, wait_train


def dump_g(g: GAME_MAP):
    urdl2ij: Dict[Direction, Tuple[int, int]] = {  #  3 x 3 的输出
        Direction.Up: [0, 1],
        Direction.Left: [1, 0],
        Direction.Right: [1, 2],
        Direction.Down: [2, 1],
    }
    for row in g:
        G: List[str] = ["" for i in range(3)]
        for b in row:
            ch = [["." for i in range(3)] for j in range(3)]
            if b.t == BlockEnum.Empty:
                ch = [[" " for i in range(3)] for j in range(3)]
            elif b.t == BlockEnum.Block:
                ch = [["X" for i in range(3)] for j in range(3)]
            elif b.t == BlockEnum.Out:
                i, j = urdl2ij[b.entry[0]]
                ch[i][j] = "O"
            elif b.t == BlockEnum.Road:
                assert isinstance(b, B_Road)  # pass type check
                ch[1][1] = "R"
                for e in b.entry:
                    i, j = urdl2ij[e]
                    if b.trans[b.trans[e]] == e:
                        ch[i][j] = "A"
                    else:
                        ch[i][j] = "B"
            elif b.t == BlockEnum.Switch:
                assert isinstance(b, B_Switch)  # pass type check
                ch[1][1] = "S"
                for e in b.entry:
                    i, j = urdl2ij[e]
                    if b.trans_group[b.trans_idx][b.trans_group[b.trans_idx][e]] == e:
                        ch[i][j] = "A"
                    else:
                        ch[i][j] = "B"
            for i in range(3):
                G[i] += "".join(ch[i])
        for text in G:
            print(text)


def dump(g: GAME_MAP, trains: List[Train]):
    dump_g(g)

    M: List[List[Tuple[int, Direction]]] = [
        [[-1, Direction.Up] for j in range(len(row))] for row in g
    ]
    for t in trains:
        M[t.i][t.j] = [t.id, t.d]

    print()
    for row in M:
        for n, d in row:
            if n == -1:
                print("__ ", end="")
            else:
                print(f"{n}{d2graphic[d]} ", end="")
        print()
    print()


def run(g: GAME_MAP, trains: List[Train], wait_train: int) -> bool:
    tick = 100  # 可能死循环
    while tick:
        try:
            n_g, n_t, n_c = next_state(g, trains, wait_train)
        except Exception as e:
            # 碰撞
            # logger.exception(e)
            return False
        if n_c == len(trains):
            print("===== Found =====")
            dump(n_g, n_t)
            print("===== Found =====")
            return True
        g, trains, wait_train = n_g, n_t, n_c
        # dump(g, trains)
        # input("Press [Enter]")  # 手动查看
        tick -= 1

    logger.warning("Might Dead Loop")
    return False


possible_block = []

# 2 通路
for i in range(4):
    for j in range(i + 1, 4):
        possible_block.append(road_helper2(i, j))

# 3 通路
for i in range(4):
    for j in [-1, 1]:
        possible_block.append(road_helper3(i, j))

print(len(possible_block))


def simple_check(g: GAME_MAP, i: int, j: int) -> bool:  # 每个check时左侧和上侧都填完了
    def _has(_i: int, _j: int, d: Direction):
        if g[_i][_j].t in [B_Block, B_Empty]:
            return False
        return d in g[_i][_j].entry

    if i == 0 and _has(i, j, Direction.Up):
        return False

    if i > 0:
        if _has(i, j, Direction.Up) and not _has(i - 1, j, Direction.Down):
            return False
        if not _has(i, j, Direction.Up) and _has(i - 1, j, Direction.Down):
            return False
    if j == 0 and _has(i, j, Direction.Left):
        return False
    if j > 0:
        if _has(i, j, Direction.Left) and not _has(i, j - 1, Direction.Right):
            return False
        if not _has(i, j, Direction.Left) and _has(i, j - 1, Direction.Right):
            return False
    return True


def solve(g: GAME_MAP, trains: List[Train], left: int):
    width = len(g[0])
    for i, row in enumerate(g):
        if len(row) != width:
            raise AssertionError(f"len(row[{i}]) = {len(row)}, width = {width}")
    dump(g, trains)
    try_cnt = 0

    def dfs(d_g: GAME_MAP, d_t: List[Train], d_l: int, sti: int, stj: int) -> bool:
        nonlocal try_cnt
        if d_l == 0:
            for i in range(len(d_g)):
                for j in range(len(d_g[i])):
                    if not simple_check(d_g, i, j):  # 快速剪枝
                        return False
            # print("Before run")
            # dump_g(d_g)
            # print("Before run")
            try_cnt += 1
            print(f"try_cnt = {try_cnt}")
            return run(d_g, d_t, 0)

        for i in range(len(d_g)):
            for j in range(len(d_g[i])):
                # 快速剪枝
                if g[i][j].t != BlockEnum.Empty and not simple_check(d_g, i, j):
                    # print(f"failed {i},{j}")
                    # dump_g(d_g)
                    return False
                if sti * len(d_g[0]) + stj >= i * len(d_g[0]) + j:
                    continue

                if d_g[i][j].t == BlockEnum.Empty:
                    clone_g = copy.deepcopy(d_g)
                    clone_t = copy.deepcopy(d_t)
                    for p in possible_block:
                        clone_g[i][j] = p
                        if not simple_check(clone_g, i, j):  # 快速剪枝
                            continue
                        if dfs(clone_g, clone_t, d_l - 1, i, j):
                            return True
        return False

    print("?", left)
    dfs(g, trains, left, 0, -1)
