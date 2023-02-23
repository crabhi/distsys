import json
import logging
import sys


logger = logging.getLogger(__name__)


class Node:
    def __init__(self):
        self.node_id = None
        self.msg_id = 0
        self.node_ids = None

    def serve(self):
        for line in sys.stdin:
            try:
                msg = json.loads(line)
                logger.info('<==  %s', msg)

                if msg['dest'] != self.node_id and self.node_id is not None:
                    raise ValueError(f'unexpected message: {msg}')

                resp = self.handle_message(msg['src'], msg['dest'], msg['body'])
                if resp:
                    resp['in_reply_to'] = msg['body']['msg_id']
                    self.send(msg['src'], resp)

            except json.JSONDecodeError:
                logger.exception("Can't parse message")

    def handle_message(self, src, dest, body):
        fun = getattr(self, f'on_{body["type"]}', None)
        if not callable(fun):
            logger.error('Unknown handler for message %s -> %s: %s', src, dest, body)
            return {
                'type': 'error',
                'code': 12,  # malformed-request
                'text': f'Unknown type: {body["type"]}',
            }

        return fun(src, dest, body)

    def on_init(self, src, dest, body):
        if self.node_id is not None:
            return {
                'type': 'error',
                'code': 12,  # malformed-request
                'text': f'Already initialized',
            }

        self.node_id = body['node_id']
        self.node_ids = body['node_ids']
        return {'type': 'init_ok'}

    def send(self, dest, body):
        if 'msg_id' not in body:
            self.msg_id += 1
            body['msg_id'] = self.msg_id

        msg = {
            'src': self.node_id,
            'dest': dest,
            'body': body,
        }

        logger.info('==>  %s', msg)
        print(json.dumps(msg))
        sys.stdout.flush()
