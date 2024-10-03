from enum import Enum
from typing import Dict, List
from pydantic import BaseModel


class Direction(int, Enum):
    Up = 0
    Right = 1
    Down = 2
    Left = 3


class BlockEnum(Enum):  # 默认输入, 不可更改的
    Empty = 0  # 空位
    Block = 1  # 不可放置
    Out = 2  # 出口
    Road = 3
    Switch = 4
    # 不是路
    Train = 5


class B_Empty(BaseModel):
    t: BlockEnum = BlockEnum.Empty
    # TODO 类型推断 感觉Final 也不太行啊? AttributeError: 'B_Empty' object has no attribute 'entry'
    entry: List[Direction] = []


class B_Block(BaseModel):
    t: BlockEnum = BlockEnum.Block
    entry: List[Direction] = []


class B_Out(BaseModel):
    t: BlockEnum = BlockEnum.Out
    entry: List[Direction]


class B_Road(BaseModel):
    t: BlockEnum = BlockEnum.Road
    entry: List[Direction]
    trans: Dict[Direction, Direction]  # 入口到出口


class B_Switch(BaseModel):
    t: BlockEnum = BlockEnum.Switch
    entry: List[Direction]
    trans_group: List[
        Dict[Direction, Direction]
    ]  # 每次经过时 切换 trans表, (idx = (idx+1)%len(trans_group))
    trans_idx: int = 0


BLOCK = B_Empty | B_Block | B_Out | B_Road | B_Switch


class Train(BaseModel):
    i: int
    j: int
    d: Direction
    id: int


GAME_MAP = List[List[BLOCK]]
