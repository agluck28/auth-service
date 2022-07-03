from piCarRobotApi.auth.AuthorizeUser import AuthorizeUser
from piCarRobotApi.auth.GetAllUsers import GetAllUsers
from piCarRobotApi.auth.AddUser import AddUser
from piCarRobotApi.auth.DeleteUser import DeleteUser
from piCarRobotApi.auth.AuthenticateUser import AuthenticateUser
from piCarRobotApi.auth.UpdateAccess import UpdateAccess
from auth.jwt_helper import JwtCreator
from auth.PiRobotCarAuth import PiRobotCarAuth
from rpc_rabbitmq.RabbitRpc import RabbitRpcServer
from dotenv import dotenv_values
import logging
import argparse, sys

FORMAT = '%(asctime)s %(levelname)s: %(message)s'
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format=FORMAT)




def main(env: str):
    try:
        config = dotenv_values(env)
    except SyntaxError as e:
        print(e)
        sys.exit()

    print(config)

    DB = config['DATABASE_NAME']
    DB_URL = config['DATABASE_URL']
    UN = config['DATABASE_USER_NAME']
    PW = config['DATABASE_PASSWORD']
    SECRET = config['SECRET']
    RABBIT_URL = config['RABBIT_URL']
    RABBIT_EXCHANGE = config['RABBIT_EXCHANGE']
    RABBIT_PASS = config['RABBIT_PASS']
    RABBIT_USER = config['RABBIT_USER']

    db = PiRobotCarAuth(DB, DB_URL, UN, PW)

    jwt = JwtCreator(SECRET)

    methods = [
        AuthorizeUser(jwt),
        GetAllUsers(db),
        AddUser(db),
        AuthenticateUser(db, jwt),
        UpdateAccess(db),
        DeleteUser(db)
    ]

    server = RabbitRpcServer(RABBIT_EXCHANGE, methods, RABBIT_URL, rabbit_user_name=RABBIT_USER,
                             rabbit_password=RABBIT_PASS)

    logger.info('Starting Server...')

    try:
        server.start()
    except:
        logger.info('Stopping Server...')
        server.close()
        db.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='User Auth Service for Pi Car Robot')
    parser.add_argument('-e', '--env', type=str, dest='env')
    args = parser.parse_args()
    main(args.env)
