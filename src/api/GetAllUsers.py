from json import dumps
from  rpc_rabbitmq.RpcBaseMethod import RpcBaseMethod
from rpc_rabbitmq.RpcBaseRequest import RpcBaseRequest

QUEUE = 'get_all_users'
SCHEMA = None

class GetAllUsers(RpcBaseMethod):

    def __init__(self, db):
        super().__init__()
        self.queue = QUEUE
        self.db = db

    def method(self, channel, pika_method, props, body):
        try:
            users = self.db.get_all_users()
            allUsers = []
            for user in users:
                allUsers.append(user[0])
            self.response = dumps({
                'users': allUsers
            })
        except RuntimeWarning as e:
            self.response = dumps({'success': False, 'info': f'{e}'})
        super().method(channel, pika_method, props, body)

class Request_GetAllUsers(RpcBaseRequest):

    def __init__(self, RpcClient, timeout_ms: int = 1000):
        super().__init__(RpcClient, timeout_ms)
        self.routing_key = QUEUE
        #can't send empty request
        self.request = {'msg': 'data'}
