#!/usr/bin/env python3

import logging

from maelstrom.node import Node


class Echo1(Node):
    def on_echo(self, src, dest, body):
        return {'echo': body['echo'], 'type': 'echo_ok'}


def main():
    logging.basicConfig(level=logging.DEBUG)
    Echo1().serve()
