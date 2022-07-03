from json import dumps, loads
from rpc_rabbitmq.RpcBaseMethod import RpcBaseMethod
from rpc_rabbitmq.RpcBaseRequest import RpcBaseRequest

QUEUE = 'update_access'
SCHEMA = {
    'email': 'email account',
    'access': ['new', 'access', 'levels']
}

class UpdateAccess(RpcBaseMethod):

    def __init__(self, db):
        super().__init__()
        self.queue = QUEUE
        self.db = db

    def method(self, channel, pika_method, props, body):
        try:
            print(body)
            request = loads(body.decode('utf-8'))
            self.db.update_access(request['email'], request['access'])
            self.response = dumps({'success': True})
        except RuntimeWarning as e:
            self.response = dumps({'success': False, 'info': f'{e}'})
        super().method(channel, pika_method, props, body)


class Request_UpdateAccess(RpcBaseRequest):

    def __init__(self, RpcClient, email, access: list[str], timeout_ms: int = 1000):
        super().__init__(RpcClient, timeout_ms)
        self.routing_key = QUEUE
        self.request = {
            'email': email,
            'access': access
        }

    def make_request(self):
        return super().make_request()