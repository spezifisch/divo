# type: ignore
"""
This file is part of mettmail (https://github.com/spezifisch/mettmail).
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

import nox


@nox.session(reuse_venv=True)
def lint(session):
    session.install("poetry")
    session.run("poetry", "install", "--no-root")
    session.run("flake8", "--max-line-length=120", "divo")
    session.run("mypy", "--strict", "divo")
    session.run("black", "--check", "divo")
