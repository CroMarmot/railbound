from enum import Enum
from typing import List, Tuple
from pydantic import BaseModel

from .helper import switch_rdl_l, switch_url_r, road_ud, road_rl, road_ur
from .model import BLOCK, B_Empty, B_Out, Train, Direction, B_Block, B_Road, GAME_MAP
from .core import solve


# all position and train_id is 0-index
def main():
    """
    E E E S(r,d,l') E E O[D]
    E E S(r',u,l) E S(r',u,l) E E
    B T B B              B B B
    B R T R              T R T
    """
    g: GAME_MAP = [
        [
            B_Empty(),
            B_Empty(),
            B_Empty(),
            switch_rdl_l(),
            B_Empty(),
            B_Block(),
            B_Out(entry=[Direction.Down]),
        ],
        [
            B_Empty(),
            B_Empty(),
            switch_url_r(),
            B_Empty(),
            switch_url_r(),
            B_Empty(),
            B_Empty(),
        ],
        [
            B_Block(),
            road_ud(),
            B_Block(),
            B_Block(),
            B_Block(),
            B_Block(),
            B_Block(),
        ],
        [
            B_Block(),
            road_ur(),
            road_rl(),
            road_rl(),
            road_rl(),
            road_rl(),
            road_rl(),
        ],
    ]
    trains = [
        Train(i=2, j=1, d=Direction.Up, id=0),
        Train(i=3, j=2, d=Direction.Left, id=1),
        Train(i=3, j=4, d=Direction.Left, id=2),
        Train(i=3, j=6, d=Direction.Left, id=3),
    ]
    solve(
        g,
        trains,
        9,
    )


main()
