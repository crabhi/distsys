#!/usr/bin/env python3

import logging

from maelstrom.node import Node


class MyNode(Node):
    def __init__(self):
        super().__init__()
        self.counter = 0


    def on_generate(self, src, dest, body):
        self.counter += 1
        return {'type': 'generate_ok', 'id': f'{self.node_id}_{self.counter}'}


def main():
    logging.basicConfig(level=logging.DEBUG)
    MyNode().serve()
