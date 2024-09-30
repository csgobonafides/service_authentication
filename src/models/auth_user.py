from src.data.state_db import work_to_user
from src.models.work_to_jwt import jwt_work


class OAuthentication:

    def auth_user(self, login, psw):
        if not work_to_user.chek_user(login):
            if work_to_user.check_psw(login, psw):
                return jwt_work.creat_pair_jwt(login)
            else:
                return {'error': 'Пороль не верный'}
        else:
            return {'error': 'Пользователь с таким логином не зарегистрирован.'}


    def exit_user(self, access):
        pass


user_auth = OAuthentication()