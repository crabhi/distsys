#!/usr/bin/env python3

import logging

from maelstrom.node import Node


class MyNode(Node):
    def __init__(self):
        super().__init__()
        self.messages = set()
        self.topology = None

    def on_broadcast(self, src, dest, body):
        self.messages.add(body['message'])
        for node in self.node_ids:
            if node == self.node_id:
                continue
            self.send(node, {'type': 'secondary_broadcast', 'message': body['message']})
        return {'type': 'broadcast_ok'}

    def on_secondary_broadcast(self, src, dest, body):
        self.messages.add(body['message'])

    def on_topology(self, src, dest, body):
        self.topology = body['topology']
        return {'type': 'topology_ok'}

    def on_read(self, src, dest, body):
        return {'type': 'read_ok', 'messages': list(self.messages)}


def main():
    logging.basicConfig(level=logging.DEBUG)
    MyNode().serve()
