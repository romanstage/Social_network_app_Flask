from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField
from wtforms.validators import InputRequired, Length
from flask_wtf.file import FileField, FileAllowed
from flask_uploads import IMAGES

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