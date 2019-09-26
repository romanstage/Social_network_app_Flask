from flask import Flask, render_template,redirect,url_for,request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
import os
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField,TextAreaField
from wtforms.validators import InputRequired, Length
from flask_wtf.file import FileField, FileAllowed
from flask_uploads import UploadSet, configure_uploads, IMAGES
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from datetime import datetime


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

manager = Manager(app)
manager.add_command('db', MigrateCommand)

class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    username = db.Column(db.String(30))
    image = db.Column(db.String(100))
    password = db.Column(db.String(50))
    join_date = db.Column(db.DateTime)

    tweets = db.relationship('Tweet',backref='user',lazy='dynamic')

class Tweet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    text = db.Column(db.String(180))
    date_created = db.Column(db.DateTime)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class RegisterForm(FlaskForm):
    name = StringField('Full name', validators=[InputRequired('Необходимо ввести полное имя.'), Length(max=100, message='Длина полного имени не может превышать 100 символов.')])
    username = StringField('Username', validators=[InputRequired('Необходимо ввести имя пользователя.'), Length(max=30, message='Имя пользователя не может превышать 30 символов.')])
    password = PasswordField('Password', validators=[InputRequired('Необходимо ввести пароль.')])
    image = FileField(validators=[FileAllowed(IMAGES, 'Только фотографии доступны для загрузки')])

class LoginForm(FlaskForm):
    username = StringField('Username',validators=[InputRequired('Необходимо ввести полное имя.'), Length(max=100, message='Длина полного имени не может превышать 100 символов.')]) #todo see if I need to change it later to russian(in register form as well)
    password = PasswordField('Password',validators=[InputRequired('Необходимо ввести пароль.')])
    remember = BooleanField('Remember me')

class TweetForm(FlaskForm):
    text = TextAreaField('Message', validators=[InputRequired('Необходимо ввести текст сообщения.')])

@app.route('/')
def index():
    form = LoginForm()

    if form.validate_on_submit():
        return f"<h1>Username: {form.username.data}, Password: {form.password.data}, Remember: {form.remember.data}</h1>"

    return render_template('index.html', form=form)


@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return redirect(url_for('index'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if not user:
            return render_template('index.html',form=form,
                                   message='Проверьте правильность ввода имени пользователя или пароля')

        if check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)

            return redirect(url_for('profile'))

        return render_template('index.html', form=form,
                                   message='Проверьте правильность ввода имени пользователя или пароля')

    return render_template('index.html', form=form)

@app.route('/profile')
@login_required
def profile():
    current_user
    return render_template('profile.html',current_user=current_user)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/timeline')
def timeline():
    form = TweetForm()

    #todo добавить позже возможность просматривать и для не залогиненных пользователей
    user_id = current_user.id
    tweets = Tweet.query.filter_by(user_id=user_id).order_by(Tweet.date_created.desc()).all()

    current_time = datetime.now()

    return render_template('timeline.html',form=form,tweets=tweets,current_time=current_time)

@app.route('/post_tweet',methods=['POST'])
@login_required
def post_tweet():
    form = TweetForm()
    if form.validate():
        tweet=Tweet(user_id=current_user.id,text=form.text.data,date_created=datetime.now())
        db.session.add(tweet)
        db.session.commit()
        return redirect(url_for('timeline'))

    return 'Что-то пошло не так' #todo добавь позже нормальную страницу с ошибкой

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

@app.route('/register',methods=['GET','POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        image_filename = photos.save(form.image.data)
        image_url = photos.url(image_filename)

        new_user = User(name=form.name.data,
                        username=form.username.data,
                        password=generate_password_hash(form.password.data),
                        image=image_url,
                        join_date=datetime.now()) #todo измени название месяца на русском в профиле или сделай такой формат 02.09.2019

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('profile'))

    return render_template('register.html', form=form)

if __name__ == '__main__':
    # manager.run()
    app.run(debug=True)

