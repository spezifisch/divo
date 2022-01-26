# type: ignore
"""
This file is part of divo (https://github.com/spezifisch/divo).
Copyright (c) 2022 spezifisch (https://github.com/spezifisch)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import binascii
import unittest

from divo.helpers import chunks, clean_unhexlify


class TestHelpers(unittest.TestCase):
    def test_clean_unhexlify(self) -> None:
        assert clean_unhexlify("1234567890") == b"\x12\x34\x56\x78\x90"
        assert clean_unhexlify("12 34 56 78 90") == b"\x12\x34\x56\x78\x90"
        assert clean_unhexlify(" 17  4    2 ") == b"\x17\x42"

        with self.assertRaises(binascii.Error):
            clean_unhexlify("foo")

        with self.assertRaises(binascii.Error):
            clean_unhexlify("fooo")

    def test_chunks(self) -> None:
        with self.assertRaises(ValueError):
            chunks("", 0)

        assert chunks("", 1) == []
        assert chunks("", 23) == []
        assert chunks("abc", 1) == ["a", "b", "c"]
        assert chunks("abc", 2) == ["ab", "c"]
        assert chunks("abc", 3) == ["abc"]
        assert chunks("abc", 4) == ["abc"]
