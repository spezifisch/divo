#!/usr/bin/env python3
"""
This file is part of divo (https://github.com/spezifisch/divo).
Copyright (c) 2021 spezifisch (https://github.com/spezifisch), carolosf (https://github.com/carolosf).

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation.
This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.
"""

import sys
from binascii import hexlify
from test import test_pattern

import click
from loguru import logger

import divo.bluetooth_socket
import divo.command
import divo.image
import divo.packet
import divo.packet_stream
import divo.pixoo

from .evo_encoder import EvoEncoder
from .evo_pixmap import RawPixmap
from .helpers import clean_unhexlify


def get_pixoo(mac_address: str) -> pixoo.Pixoo:
    if not mac_address:
        raise ValueError("no mac address given")

    bt = bluetooth_socket.BluetoothSocket(mac_address, socket_timeout=2.0)
    d = pixoo.Pixoo(bt)
    return d


@click.group()
@click.option("--debug/--no-debug", default=False)
@click.pass_context
def cli(ctx, debug):
    ctx.ensure_object(dict)

    logger.remove()
    if debug:
        logger.add(sys.stderr, level="DEBUG")
    else:
        logger.add(sys.stderr, level="INFO")

    # image may be rendered to different outputs later
    ctx.obj["screen"] = image.Screen()


@cli.command()
@click.pass_context
def direct(ctx, args):
    screen = ctx.obj["screen"]
    palette, payload = args
    palette = clean_unhexlify(palette)
    payload = clean_unhexlify(payload)

    psd = packet_stream.PacketStreamDecoder(palette, payload)
    psd.image.print_to(screen)


@cli.command()
@click.argument("raw_data", nargs=-1)
@click.option("--send", is_flag=True)
@click.option("--mac-address")
@click.pass_context
def raw(ctx, raw_data, send, mac_address):
    screen = ctx.obj["screen"]

    # parse all packets, one per argument
    packets = [clean_unhexlify(arg) for arg in raw_data]
    command_parser = command.CommandParser()
    commands = [packet.Packet.parse(command_parser, p) for p in packets]
    if None in commands:
        missing = commands.index(None)
        raise ValueError(f"couldn't parse packet no. {missing}")

    palette = commands[0].palette
    payload = commands[0].image  # TODO reassemble image data

    psd = packet_stream.PacketStreamDecoder(palette, payload)

    print("palette data:", hexlify(palette))
    print("palette:")
    psd.palette.print_to(screen)

    print("image data:", hexlify(payload))
    print("image:")
    psd.image.print_to(screen)

    if send:
        logger.info(f"sending image to {mac_address}")
        dev = get_pixoo(mac_address)
        for p in packets:
            dev.write(p)


@cli.command()
@click.argument("path", nargs=1)
@click.option("--send", is_flag=True)
@click.option("--mac-address")
@click.pass_context
def img(ctx, path, send, mac_address):
    screen = ctx.obj["screen"]

    print(path)
    rp = RawPixmap(16, 16)
    img = rp.load_image(path)
    rp.set_rgb_pixels(rp.decode_image(img))

    ee = EvoEncoder()
    data = ee.image_bytes(rp.get_pixel_data())
    print("raw command: " + bytes.hex(data))

    packets = [clean_unhexlify(bytes.hex(data))]
    command_parser = command.CommandParser()
    commands = [packet.Packet.parse(command_parser, p) for p in packets]
    if None in commands:
        missing = commands.index(None)
        raise ValueError(f"couldn't parse packet no. {missing}")

    palette = commands[0].palette
    payload = commands[0].image  # TODO reassemble image data

    psd = packet_stream.PacketStreamDecoder(palette, payload)

    print("palette data:", hexlify(palette))
    print("palette:")
    psd.palette.print_to(screen)

    print("image data:", hexlify(payload))
    print("image:")
    psd.image.print_to(screen)

    if send:
        logger.info(f"sending image to {mac_address}")
        dev = get_pixoo(mac_address)
        for p in packets:
            dev.write(p)


@cli.command()
@click.option("--mac-address", required=True)
@click.option("--test-id", default=1, required=True)
def test(mac_address, test_id):
    dev = get_pixoo(mac_address)

    test_pattern(test_id, dev)


if __name__ == "__main__":
    cli(obj={})
