#!/usr/bin/env python3

import logging
import time
import threading

from maelstrom.node import Node

HEARTBEAT_SEC = 1
logger = logging.getLogger(__name__)


class MyNode(Node):
    def __init__(self):
        super().__init__()
        self.messages = set()
        self.topology = None
        self.notifier_thread = threading.Thread(target=self._notifier, name="notifier", daemon=True)

    def serve(self):
        self.notifier_thread.start()
        super().serve()

    def _notifier(self):
        while True:
            time.sleep(HEARTBEAT_SEC)
            if not self.messages or not self.node_ids:
                continue

            for node in self.node_ids:
                if node != self.node_id:
                    self.send(node, {'type': 'secondary_broadcast', 'messages': list(self.messages)})

    def on_broadcast(self, src, dest, body):
        self.messages.add(body['message'])
        return {'type': 'broadcast_ok'}

    def on_secondary_broadcast(self, src, dest, body):
        self.messages.update(body['messages'])

    def on_topology(self, src, dest, body):
        self.topology = body['topology']
        return {'type': 'topology_ok'}

    def on_read(self, src, dest, body):
        return {'type': 'read_ok', 'messages': list(self.messages)}


def main():
    logging.basicConfig(level=logging.DEBUG)
    MyNode().serve()
