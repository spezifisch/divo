#!/usr/bin/env python

import sys
from binascii import hexlify

from loguru import logger
import click

import bluetooth_socket
import command
from helpers import clean_unhexlify
import image
import packet
import packet_stream
import pixoo
from test import test_pattern


def get_pixoo(mac_address: str) -> pixoo.Pixoo:
    if not mac_address:
        raise ValueError("no mac address given")

    bt = bluetooth_socket.BluetoothSocket(mac_address, socket_timeout=2.0)
    d = pixoo.Pixoo(bt)
    return d


@click.group()
@click.option('--debug/--no-debug', default=False)
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
@click.option("--mac-address", required=True)
@click.option("--test-id", default=1, required=True)
def test(mac_address, test_id):
    dev = get_pixoo(mac_address)

    test_pattern(test_id, dev)


if __name__ == "__main__":
    cli(obj={})
