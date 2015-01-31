from base_model import BaseModel


class UserModel(BaseModel):
    # Fields:
    f_login = None
    f_password = None

    # Configuration:
    conf_key_format = 'user:{login}'
    conf_unique = True


class SessionModel(BaseModel):
    # Fields:
    f_session_id = None
    f_login = None

    # Configuration:
    conf_key_format = 'session:{session_id}'
    conf_unique = True
