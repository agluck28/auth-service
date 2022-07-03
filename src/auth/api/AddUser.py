from json import dumps, loads
from rpc_rabbitmq.RpcBaseMethod import RpcBaseMethod
from rpc_rabbitmq.RpcBaseRequest import RpcBaseRequest

QUEUE = 'add_user'

SCHEMA = {'email': 'email',
          'password': 'apassword',
          'access': 'accesslevel'}


class AddUser(RpcBaseMethod):

    def __init__(self, db):
        super().__init__()
        self.queue = QUEUE
        self.db = db

    def method(self, channel, pika_method, props, body):
        request = loads(body.decode('utf-8'))
        try:
            self.db.add_user(request['email'],
                             request['password'], request['access'])
            self.response = dumps({'success': True})
        except RuntimeWarning as e:
            self.response = dumps({'success': False, 'info': f'{e}'})
        super().method(channel, pika_method, props, body)


class Request_AddUser(RpcBaseRequest):

    def __init__(self, email, password, access, RpcClient, timeout_ms: int = 1000):
        super().__init__(RpcClient, timeout_ms)
        self.routing_key = QUEUE
        self.request = {
            'email': email,
            'password': password,
            'access': access
        }
    
    def make_request(self):
        return super().make_request()