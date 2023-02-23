#!/usr/bin/env python3

import logging

from maelstrom.node import Node


class MyNode(Node):
    def __init__(self):
        super().__init__()
        self.messages = []


    def on_broadcast(self, src, dest, body):
        self.messages.append(body['message'])
        return {'type': 'broadcast_ok'}

    def on_topology(self, src, dest, body):
        self.topology = body['topology']
        return {'type': 'topology_ok'}

    def on_read(self, src, dest, body):
        return {'type': 'read_ok', 'messages': self.messages}


def main():
    logging.basicConfig(level=logging.DEBUG)
    MyNode().serve()
