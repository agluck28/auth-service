from json import dumps, loads
from  rpc_rabbitmq.RpcBaseMethod import RpcBaseMethod
from rpc_rabbitmq.RpcBaseRequest import RpcBaseRequest

QUEUE = 'delete_user'
SCHEMA = {
    'email': 'email to delete'
}

class DeleteUser(RpcBaseMethod):

    def __init__(self, db):
        super().__init__()
        self.queue = QUEUE
        self.db = db

    def method(self, channel, pika_method, props, body):
        try:
            email = loads(body.decode('utf-8'))['email']
            self.db.delete_user(email)
            self.response = dumps({'code': 200, 'msg': 'User Deleted'})
        except RuntimeWarning as e:
            self.response = dumps({'code': 500, 'msg': f'{e}'})
        super().method(channel, pika_method, props, body)

class Request_DeleteUser(RpcBaseRequest):

    def __init__(self, RpcClient, email, timeout_ms: int = 1000):
        super().__init__(RpcClient, timeout_ms)
        self.routing_key = QUEUE
        self.request = {
            'email': email
        }

    def make_request(self):
        return super().make_request()