from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
import os
from flask_uploads import UploadSet, configure_uploads, IMAGES
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user



app = Flask(__name__)

photos = UploadSet('photos', IMAGES)

app.config['UPLOADED_PHOTOS_DEST'] = 'images'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'kdfgkjfdlkgjfdlkjgfj4dkgsfdklgjfdkjgkfdjglj'

login_manager = LoginManager(app)
login_manager.login_view = 'login'

configure_uploads(app,photos)

db = SQLAlchemy(app)
migrate = Migrate(app,db)

@app.template_filter('time_since')
def time_since(delta):

    seconds = delta.total_seconds()

    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)

    if days > 0:
        return f'{int(days)}д'
    elif hours > 0:
        return f'{int(hours)}ч'
    elif minutes > 0:
        return f'{int(minutes)}м'
    else:
        return 'Только что'

from views import *

manager = Manager(app)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    # manager.run()
    app.run(debug=True)

