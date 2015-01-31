import uuid

from models import SessionModel, UserModel
from json_return import JSONReturn


class Registration(object):

    def login(self, request):
        if request.method == 'GET':
            return request.render_template('users/login_form.html')

        login = request.request.body_arguments.get('login', None)[0]
        password = request.request.body_arguments.get('password', None)[0]

        if not login or not password:
            return JSONReturn.ok(False)

        user = UserModel.get(login=login)

        if user and login == user['login'] and password == user['password']:
            session_id = str(uuid.uuid4())
            SessionModel(session_id=session_id, login=login).save()
            request.set_secure_cookie('confman_session_id', session_id)
            request.set_secure_cookie('confman_login', login)
            return JSONReturn.ok(True)

        return JSONReturn.ok(False)

    def logout(self, request):
        cookie_session_id = request.get_secure_cookie('confman_session_id')
        cookie_login = request.get_secure_cookie('confman_login')
        SessionModel(session_id=cookie_session_id, login=cookie_login).delete()
        request.clear_cookie('confman_session_id')
        request.clear_cookie('confman_login')
        return request.render_template('users/logout.html')

    def is_logged(self, request):
        cookie_session_id = request.get_secure_cookie('confman_session_id')
        cookie_login = request.get_secure_cookie('confman_login')
        session = SessionModel.get(session_id=cookie_session_id)
        if session and session['session_id'] == cookie_session_id \
           and session['login'] == cookie_login:
            return True
        return False

    def login_required_scope(func):
        def wrap(self, request, *args, **kwargs):
            if self.is_logged(request):
                return func(self, request, *args, **kwargs)
            else:
                return '403 forbidden'
        return wrap

    @staticmethod
    def login_required(func):
        def wrap(self, request, *args, **kwargs):
            r = Registration()
            if r.is_logged(request):
                return func(self, request, *args, **kwargs)
            else:
                return '<meta http-equiv="refresh"\
                         content="0; url=/user/login" />'
        return wrap

    @login_required_scope
    def add_user(self, request, login, password):
        status = UserModel(login=login, password=password).save()
        return JSONReturn.ok(status)

    def get_user(self, request, login):
        user = UserModel.get(login=login)

        if user:
            return JSONReturn.ok(user)

        return JSONReturn.error()

    def remove_user(self, request, login):
        # TODO: fix it
        status = UserModel(login=login).save()
        return JSONReturn.ok(status)
