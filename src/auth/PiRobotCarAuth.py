from typing import Tuple
import psycopg2

try:
    from hasher_salter import hash_new_password, is_correct_password
except:
    from .hasher_salter import hash_new_password, is_correct_password


class PiRobotCarAuth():
    '''
    Helper for authorization for the Pi-Robot-Car project
    Supports connection to the DB, retrieving users, adding users,
    deleting users and validating users
    '''

    def __init__(self, database: str,
                 db_url: str = 'localhost',
                 user_name: str = '', password: str = '') -> None:
        try:
            self.connection = psycopg2.connect(dbname=database,
                                               user=user_name,
                                               password=password,
                                               host=db_url)
            self.connection.autocommit = True
        except (RuntimeError, RuntimeWarning) as e:
            raise e
        except (psycopg2.Error) as error:
            raise RuntimeWarning(self._handle_exceptions(error))

    def get_all_users(self) -> Tuple:
        '''
        Returns all users authorized for the DB
        '''
        query = """
        SELECT "email"
        FROM users.picar;
        """
        try:
            cur = self.connection.cursor()
            cur.execute(query)
            results = cur.fetchall()
            cur.close()
            return results
        except (psycopg2.Error) as error:
            if cur is not None:
                cur.close()
            raise RuntimeWarning(self._handle_exceptions(error))

    def add_user(self, email: str, password: str, access: list[str]) -> None:
        try:
            # create the salt
            (salt, pw_hash) = hash_new_password(password)
            query = """
            INSERT INTO users.picar(email, password, salt, access)
            VALUES(%s, %s, %s, %s);
            """
            cur = self.connection.cursor()
            cur.execute(query, (email, pw_hash.hex(), salt.hex(), access, ))
            cur.close()
        except (psycopg2.Error) as error:
            if cur is not None:
                cur.close()
            raise RuntimeWarning(self._handle_exceptions(error))

    def update_access(self, email: str, access: list[str]) -> None:
        try:
            query = """
            UPDATE users.picar
            SET access = (select array_agg(distinct e) from unnest(access || %s) e)
            WHERE email=%s AND not access @> %s;
            """
            cur = self.connection.cursor()
            cur.execute(query, (access, email, access, ))
            cur.close()
        except (psycopg2.Error) as error:
            if cur is not None:
                cur.close()
            raise RuntimeWarning(self._handle_exceptions(error))

    def authenticate_user(self, email: str, password: str, access: str) -> dict:
        try:
            query = """
            SELECT password, salt, access FROM users.picar
            WHERE email=%s;
            """
            cur = self.connection.cursor()
            cur.execute(query, (email, ))
            (pw_hash, salt, acc) = cur.fetchone()
            cur.close()
            if pw_hash is None:
                # no user return
                return {'code': 401, 'msg': 'Wrong Username or Password'}
            correct = is_correct_password(
                bytearray.fromhex(salt), bytearray.fromhex(pw_hash), password)
            if access in acc and correct:
                return {'code': 200, 'msg': 'Allowed'}
            elif access in acc:
                return {'code': 401, 'msg': 'Wrong Username or Password'}
            else:
                return {'code': 401, 'msg': 'Wrong Access Level'}
        except (psycopg2.Error) as error:
            if cur is not None:
                cur.close()
            raise RuntimeWarning(self._handle_exceptions(error))

    def delete_user(self, email: str) -> None:
        try:
            query = """
            DELETE FROM users.picar
            WHERE email=%s;
            """
            cur = self.connection.cursor()
            cur.execute(query, (email, ))
            cur.close()
        except (psycopg2.Error) as error:
            if cur is not None:
                cur.close()
            raise RuntimeWarning(self._handle_exceptions(error))

    def _handle_exceptions(self, err):
        print(err.pgcode, err.pgerror)
        match (err.pgcode):
            case '23505':
                return 'User already exists'
            case _:
                return f'Op Failed: {err.pgerror}'

    def close(self) -> None:
        self.connection.close()
