from app import app

app.config.from_object('config')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../hr.sqlite3'
app.config['SECRET_KEY'] = '@/Secret---Key@@'
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = ''
app.config['MAIL_PASSWORD'] = ''
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
