import json


class JSONReturn(object):

    @staticmethod
    def ok(data=''):
        ret = {'status': True,
               'data': data}
        return json.dumps(ret)

    @staticmethod
    def error(data=''):
        ret = {'status': False,
               'data': data}
        return json.dumps(ret)
