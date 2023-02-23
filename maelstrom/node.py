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
                    resp = {'body': resp}
                    resp['body']['in_reply_to'] = msg['body']['msg_id']
                    resp['src'] = self.node_id
                    resp['dest'] = msg['src']
                    if 'msg_id' not in resp['body']:
                        self.msg_id += 1
                        resp['body']['msg_id'] = self.msg_id
                    logger.info('==>  %s', resp)
                    print(json.dumps(resp))
                    sys.stdout.flush()

            except json.JSONDecodeError:
                logger.exception("Can't parse message")

    def handle_message(self, src, to, body):
        fun = getattr(self, f'on_{body["type"]}', None)
        if not callable(fun):
            logger.error('Unknown handler for message %s -> %s: %s', src, to, body)
            return {
                'type': 'error',
                'code': 12,  # malformed-request
                'text': f'Unknown type: {body["type"]}',
            }

        return fun(src, to, body)

    def on_init(self, src, to, body):
        if self.node_id is not None:
            return {
                'type': 'error',
                'code': 12,  # malformed-request
                'text': f'Already initialized',
            }

        self.node_id = body['node_id']
        self.node_ids = body['node_ids']
        return {'type': 'init_ok'}
