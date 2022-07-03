from json import dumps, loads
from rpc_rabbitmq.RpcBaseMethod import RpcBaseMethod
from rpc_rabbitmq.RpcBaseRequest import RpcBaseRequest

QUEUE = 'authorize_user'
SCHEMA = {
    'token': 'jwt token',
    'access': 'access level'
}

class AuthorizeUser(RpcBaseMethod):

    def __init__(self, jwt):
        super().__init__()
        self.queue = QUEUE
        self.jwt = jwt

    def method(self, channel, pika_method, props, body):
        msg = loads(body.decode('utf-8'))
        valid = self.jwt.decode_token(msg['token'])
        #token returned as being valid, check access level is correct for token
        if valid[0]:
            if 'access' in valid[1] and 'access' in msg:
                if msg['access'] != valid[1]['access']:
                    self.response = dumps({
                        'valid': False,
                        'data': 'Invalid Access Request'
                    })
                else:
                    self.response = dumps({
                        'valid': valid[0],
                        'data': valid[1]
                    })
        else:
            self.response = dumps({
                'valid': valid[0],
                'data': valid[1]
            })
        super().method(channel, pika_method, props, body)

class Request_AuthorizeUser(RpcBaseRequest):

    def __init__(self, RpcClient, token: str, access: str, timeout_ms: int = 1000):
        super().__init__(RpcClient, timeout_ms)
        self.routing_key = QUEUE
        self.request = {
            'token': token,
            'access': access
        }

    def make_request(self):
        return super().make_request()

