import tornado
import tornado.web
import jinja2
import template

from models import *
from config import *


if config['use_memcache']:
        templateLoader = template.MemcacheLoader( searchpath="/" )
else:
        tpl_searchpath = config['template_dir'] if config['template_dir'].startswith(base_path) \
                                else os.path.join(base_path, config['template_dir'])
        templateLoader = jinja2.FileSystemLoader( searchpath=tpl_searchpath )

templateEnv = jinja2.Environment( loader=templateLoader )



class Handler(tornado.web.RequestHandler):
	def __init__(self, *args, **kwargs):
		super(Handler, self).__init__(*args, **kwargs)

	@tornado.gen.coroutine
	def get(self, *args, **kwargs):
		self.method = 'GET'
		self.user_data = self.user_data()
		res = yield self.handler(*args, **kwargs)
		self.write(res)

	
	@tornado.gen.coroutine
	def post(self, *args, **kwargs):
		self.method = 'POST'
		self.user_data = self.user_data()
		res = yield self.handler(*args, **kwargs)
		self.write(res)

        def user_data(self):
		ret = {
			'logged': False,
		}

                cookie_session_id = self.get_secure_cookie('confman_session_id')
                cookie_login = self.get_secure_cookie('confman_login')
                session = SessionModel.get(session_id=cookie_session_id)
                if session and session['session_id'] == cookie_session_id and session['login']:
                        ret['logged'] = True
			ret['login'] = session['login']
			ret['session_id'] = session['session_id']
		
		return ret

	def render_template(self, name, variables={}):
        	TEMPLATE_FILE = name
        	template = templateEnv.get_template( TEMPLATE_FILE )
        	variables.update(config)
        	variables['request'] = self.request
        	variables['user_data'] = self.user_data
        	return template.render( variables )

