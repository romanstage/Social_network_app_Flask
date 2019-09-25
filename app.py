from flask import Flask, render_template,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
import os
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Length
from flask_wtf.file import FileField, FileAllowed
from flask_uploads import UploadSet, configure_uploads, IMAGES
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

photos = UploadSet('photos', IMAGES)

app.config['UPLOADED_PHOTOS_DEST'] = 'images'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'kdfgkjfdlkgjfdlkjgfj4dkgsfdklgjfdkjgkfdjglj'

configure_uploads(app,photos)

db = SQLAlchemy(app)
migrate = Migrate(app,db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    username = db.Column(db.String(30))
    image = db.Column(db.String(100))
    password = db.Column(db.String(50))

class RegisterForm(FlaskForm):
    name = StringField('Full name', validators=[InputRequired('Необходимо ввести полное имя.'), Length(max=100, message='Длина полного имени не может превышать 100 символов.')])
    username = StringField('Username', validators=[InputRequired('Необходимо ввести имя пользователя.'), Length(max=30, message='Имя пользователя не может превышать 30 символов.')])
    password = PasswordField('Password', validators=[InputRequired('Необходимо ввести пароль.')])
    image = FileField(validators=[FileAllowed(IMAGES, 'Только фотографии доступны для загрузки')])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/timeline')
def timeline():
    return render_template('timeline.html')

@app.route('/register',methods=['GET','POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        image_filename = photos.save(form.image.data)
        image_url = photos.url(image_filename)

        new_user = User(name=form.name.data,
                        username=form.username.data,
                        password=generate_password_hash(form.password.data),
                        image=image_url)

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('profile'))

    return render_template('register.html', form=form)

if __name__ == '__main__':
    # manager.run()
    app.run(debug=True)

