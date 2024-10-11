class Conntroller:
    def __init__(self, state1, state2):
        self.state1 = state1
        self.state2 = state2

    def registrayshin(self, login: str, psw: str):
        return self.state1.set_user(login, psw)

    def authentication(self, login: str, psw: str):
        if self.state1.chek_user(login) == False:
            if self.state1.check_psw(login, psw):
                return self.state2.creat_pair_jwt(login)
            else:
                return {'error': 'Пороль не верный'}
        else:
            return {'error': 'Пользователь с таким логином не зарегистрирован.'}


controller = None

def get_controller():
    if controller is None:
        raise ValueError('Controller is none.')
    return controller



