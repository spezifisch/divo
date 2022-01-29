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

import unittest
from unittest.mock import MagicMock, call, patch

from click.testing import CliRunner

import divo.main


@patch("colorconsole.terminal.get_terminal", autospec=True)
class TestMain(unittest.TestCase):
    packet_8color = (
        "01860044000a0a04aa7f00f4010008000000ff0000ff5500ffaa00ffff02adff0000ff00ffffff88c6fa0000e000000000001c0000000"
        "08003000000007000000000000e00000000c001000000003800000000000700000000e000000000001c00000000800300000000700000"
        "0000000e00000000c00100000000380000000000070000000000ee1602"
    )

    def test_help(self, mock_terminal: MagicMock):
        runner = CliRunner()
        result = runner.invoke(divo.main.cli, ["--help"])
        assert result.exit_code == 0
        assert result.output.startswith("Usage:")

    def test_raw(self, mock_terminal: MagicMock):
        runner = CliRunner()
        result = runner.invoke(divo.main.cli, ["raw", self.packet_8color], color=True)
        assert result.exit_code == 0

        # check image dimensions
        expected_colorless_image = "image:\n" + "\n".join(["█" * 32] * 16) + "\n"
        assert result.output.endswith(expected_colorless_image)

        # check color output
        mock_terminal.assert_called_once()
        mock_terminal.return_value.xterm24bit_set_fg_color.assert_called()
        mock_terminal.return_value.reset.assert_called()

        assert len(mock_terminal.return_value.xterm24bit_set_fg_color.call_args_list) >= 16 * 16

        # sorry for this
        expected_colors_list = (
            [
                (0, 0, 0),
                (255, 0, 0),
                (255, 85, 0),
                (255, 170, 0),
                (255, 255, 2),
                (173, 255, 0),
                (0, 255, 0),
                (255, 255, 255),
            ]
            + 7 * [(0, 0, 0)]
            + [(255, 255, 255)]
            + 15 * 16 * [(0, 0, 0)]
        )
        # set diagonal pixels
        for i in range(1, 16):
            expected_colors_list[16 * i + (15 - i)] = (255, 255, 255)

        expected_colors = [call(*x) for x in expected_colors_list]
        assert expected_colors == mock_terminal.return_value.xterm24bit_set_fg_color.call_args_list[-16 * 16 :]
