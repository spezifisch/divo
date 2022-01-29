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

import importlib
import unittest
from unittest.mock import patch


class TestRestAppImports(unittest.TestCase):
    @patch.dict("sys.modules", {"fastapi": None})
    def test_import_error_fastapi(self) -> None:
        with self.assertRaises(ImportError) as ctx:
            importlib.import_module("divo.rest.app")
        assert "fastapi" in str(ctx.exception)

    @patch.dict("sys.modules", {"pydantic": None})
    def test_import_error_pydantic(self) -> None:
        with self.assertRaises(ImportError) as ctx:
            importlib.import_module("divo.rest.app")
        assert "pydantic" in str(ctx.exception)

    @patch.dict("sys.modules", {"uvicorn": None})
    def test_import_error_uvicorn_run(self) -> None:
        app = importlib.import_module("divo.rest.app")
        with self.assertRaises(ImportError) as ctx:
            app.run()
        assert "uvicorn" in str(ctx.exception)
