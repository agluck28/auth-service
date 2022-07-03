'''
Set of functions to handle generation of jwts for the pi-car-robot app
'''
import jwt
import time
from typing import Tuple


class JwtCreator():
    '''
    Lightweight class used for creating and decoding JWTs
    Main support is being able to set the same secret
    for all tokens created with this utility
    '''

    def __init__(self, secret: str) -> None:
        self.secret = secret

    def create_token(self, life_span: int, **kwargs) -> str:
        '''
        Creates a JWT with the passed in life span and user data
        '''
        payload = {
            'iat': time.time(),
            'exp': time.time() + life_span
        }

        for key, value in kwargs.items():
            payload[key] = value

        return jwt.encode(payload, self.secret, 'HS256')

    def decode_token(self, token: str) -> Tuple:
        '''
        Decodes the passed in token and checks if expired
        Returns true if valid along with the message as the second element
        of the tuple. If expired, returns false and expired. For errors in decoding
        returns false and the error message
        '''
        try:
            message = jwt.decode(token, self.secret, algorithms=['HS256'])
            return (True, message)
        except (jwt.exceptions.ExpiredSignatureError):
            return (False, 'Token Expired')
        except (jwt.exceptions.InvalidTokenError) as e:
            return (False, e)


if __name__ == '__main__':

    secret = 'test'

    helper = JwtCreator(secret)

    token = helper.create_token(5, access='all')

    message = helper.decode_token(token)

    print(message)
