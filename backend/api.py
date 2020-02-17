#!/usr/bin/env python3
import os
import smtplib, ssl
from email.message import EmailMessage
import random, string
from flask import Flask, abort, request, jsonify, g, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

DB_FILE = os.environ.get('DB_FILE', 'db.sqlite')
SMTP_PORT = os.environ.get('SMTP_PORT', 465)
SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
SMTP_EMAIL = os.environ.get('SMTP_EMAIL', None)
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', None)

# initialization
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'supersecretkey')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_FILE}'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# extensions
db = SQLAlchemy(app)
auth = HTTPBasicAuth()


class User(db.Model):
    __tablename__ = 'users'
    # TODO: Don't use id, use _id
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    email = db.Column(db.String(32), index=True)
    password_hash = db.Column(db.String(64))

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=600):
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None    # valid token, but expired
        except BadSignature:
            return None    # invalid token
        user = User.query.get(data['id'])
        return user


def send_email(_receiver: str, _subject: str, _message: str):
    if not SMTP_EMAIL or not SMTP_PASSWORD:
        return None
    # Create a secure SSL context

    msg = EmailMessage()
    msg.set_content(_message)

    msg['Subject'] = _subject
    msg['From'] = SMTP_EMAIL
    msg['To'] = _receiver

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.send_message(msg)
    except Exception as err:
        return err

    return 'Email sent.'


@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    user = User.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = User.query.filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True


@app.route('/api/register', methods=['POST'])
def user_register():
    """ curl -i -X POST -H "Content-Type: application/json" -d '{"username":"uname","password":"pword"}' http://localhost:5000/api/register
    """
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        return jsonify({
            'success': False,
            'error': 'Missing arguments.'
        }), 400
    if User.query.filter_by(username=username).first() is not None:
        return jsonify({
            'success': False,
            'error': 'User already exists.'
        }), 403
    user = User(username=username)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({
        'success': True,
        'username': user.username
    }), 201, {
        'Location': url_for('get_user', id=user.id, _external=True)
    }


@app.route('/api/email', methods=['POST'])
@auth.login_required
def email_change():
    """ curl -u uname:pword -i -X POST -H "Content-Type: application/json" -d '{"new_email": "root@runarsf.dev"}' http://localhost:5000/api/email
    """
    new_email = request.json.get('new_email')
    g.user.email = new_email
    db.session.commit()
    return jsonify({
        'success': True,
        'message': 'Email changed.'
    }), 200


@app.route('/api/change', methods=['POST'])
@auth.login_required
def password_change():
    """ curl -u uname:pword -i -X POST -H "Content-Type: application/json" -d '{"new_password": "newpword"}' http://localhost:5000/api/change
    """
    _new_password = request.json.get('new_password')
    g.user.hash_password(_new_password)
    db.session.commit()
    return jsonify({
        'success': True,
        'message': 'Password changed.'
    }), 200


@app.route('/api/forgot', methods=['POST'])
def password_reset():
    """ curl -i -X POST -H "Content-Type: application/json" -d '{"email": "root@runarsf.dev", "username": "uname"}' http://localhost:5000/api/forgot
        TODO: Consider checking username as well as email.
    """
    _email = request.json.get('email')
    _username = request.json.get('username')

    user = User.query.filter_by(username=_username).first()
    if not user:
      return jsonify({
        'success': False,
        'error': 'A user with that username could not be found.'
      })
    if not user.email == _email:
      return jsonify({
        'success': False,
        'error': 'A user with that email address does not exist.'
      })

    _new_password = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(12))
    _subject = 'Password reset request.'
    _message = f"""\
    Your new password: {_new_password}

    If you did not request this email, you can safely ignore it."""

    _email_sent = send_email(_email, _subject, _message)
    if not _email_sent:
        return jsonify({
            'success': False,
            'error': 'Failed to send email.'
        })
    user.hash_password(_new_password)
    return jsonify({
        'success': True,
        'message': _email_sent
    }), 200


@app.route('/api/user/<int:id>', methods=['GET'])
def get_user(id):
    """ curl -i -X GET -H "Content-Type: application/json" http://localhost:5000/api/user/1
    """
    user = User.query.get(id)
    if not user:
        return jsonify({
            'success': False,
            'error': 'User not found.'
        }), 400
    return jsonify({
        'success': True,
        'username': user.username
    }), 200


@app.route('/api/token', methods=['GET'])
@auth.login_required
def get_token():
    """ curl -u uname:pword -i -X GET -H "Content-Type: application/json" http://localhost:5000/api/token
    """
    _tokenDurationHours = 600
    token = g.user.generate_auth_token(_tokenDurationHours)
    return jsonify({
        'success': True,
        'token': token.decode('ascii'),
        'duration': _tokenDurationHours
    }), 200


@app.route('/api/profile', methods=['GET'])
@auth.login_required
def get_profile():
    """ curl -u uname:pword -i -X GET -H "Content-Type: application/json" http://localhost:5000/api/profile
    """
    return jsonify({
        'success': True,
        'username': g.user.username,
        'email': g.user.email,
        'password_hash': g.user.password_hash
    }), 200


@app.route('/api/health', methods=['GET'])
def get_health():
    """ curl -i -X GET -H "Content-Type: application/json" http://localhost:5000/api/health
    """
    return jsonify({
        'success': True
    }), 200


@app.errorhandler(404)
def page_not_found(err):
    # curl -i -X GET -H "Content-Type: application/json" http://localhost:5000/api/this_page_does_not_exist
    #return render_template('404.html'), 404
    #abort(404, description="Resource not found") # To be used when aborting from other functions
    return jsonify({
        'success': False,
        'error': 'The resource does not exist.'
    }), 404


@app.errorhandler(405)
def method_not_allowed(err):
    """ curl -i -X POST -H "Content-Type: application/json" http://localhost:5000/api/health
    """
    return jsonify({
        'success': False,
        'error': 'Method not allowed.'
    }), 405


if __name__ == '__main__':
    if not os.path.exists(DB_FILE):
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
