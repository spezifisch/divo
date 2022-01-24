"""
This file is part of divo (https://github.com/spezifisch/divo).
Copyright (c) 2021 spezifisch (https://github.com/spezifisch).

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation.
This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.
"""

from binascii import unhexlify
from typing import List


def clean_unhexlify(val: str) -> bytes:
    val = val.strip().replace(" ", "").replace("\n", "")
    return unhexlify(val)


def chunks(s: str, n: int) -> List[str]:
    return [s[i : i + n] for i in range(0, len(s), n)]
