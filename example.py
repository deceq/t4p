from t4p import application

def index(request):
	return 'Index page!'

app = application.Application([
	(r'/', index),
])

app.start()
