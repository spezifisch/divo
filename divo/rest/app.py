"""
This file is part of divo (https://github.com/spezifisch/divo).
Copyright (c) 2022 spezifisch (https://github.com/spezifisch)

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation.
This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.
"""

try:
    import uvicorn
except ImportError:
    pass  # this is fine if the user doesn't call run(). this way we support using hypercorn etc.

try:
    from fastapi import FastAPI
    from pydantic import BaseModel
except ImportError:
    print("divo is missing extra dependencies. You need to install divo[rest]")
    raise

app = FastAPI()


class RootOut(BaseModel):
    Hello: str


@app.get("/", response_model=RootOut)
async def read_root() -> RootOut:
    return RootOut(Hello="World")


def run() -> None:
    """Start REST API with uvicorn"""
    uvicorn.run("divo.rest.app:app")
