from json import dumps, loads
from rpc_rabbitmq.RpcBaseMethod import RpcBaseMethod
from rpc_rabbitmq.RpcBaseRequest import RpcBaseRequest

QUEUE = 'authenticate_user'

SCHEMA = {
    'email': 'email',
    'password': 'apassword',
    'access': 'access',
    'life_span': 'optional number, default 3600'
}

class AuthenticateUser(RpcBaseMethod):

    def __init__(self, db, jwt):
        super().__init__()
        self.queue = QUEUE
        self.db = db
        self.jwt = jwt

    def method(self, channel, pika_method, props, body):
        try:
            creds = loads(body.decode('utf-8'))
            email = creds['email']
            password = creds['password']
            access = creds['access']
            #default to 1 hour for token lifespan 
            life_span = 3600
            if 'life_span' in creds:
                life_span = creds['life_span']
            success = self.db.authenticate_user(email, password, access)
            token = self.jwt.create_token(life_span=life_span, access=access)
            if success['code'] == 200:
                success['token'] = token
            self.response = dumps(success)
        except RuntimeWarning as e:
            self.response = dumps({'code': 500, 'msg': f'{e}'})
        super().method(channel, pika_method, props, body)

class Request_AuthenticateUser(RpcBaseRequest):

    def __init__(self, RpcClient, email, password, access, life_span = None, timeout_ms: int = 1000):
        super().__init__(RpcClient, timeout_ms)
        self.routing_key = QUEUE
        self.request = {
            'email': email,
            'password': password,
            'access': access
        }
        if life_span is not None:
            self.request['life_span'] = life_span

    def make_request(self):
        return super().make_request()

