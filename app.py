from operator import pos
from flask import Flask, render_template, request, redirect, session
from flask.sessions import NullSession
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

with open('configuration.json', 'r') as f:
    params = json.load(f)["parameters"]
    print(params)

application = Flask(__name__)
application.secret_key = "secret_key_for_login"

if (params['live_server'] == 'true'):

    application.config['SQLALCHEMY_DATABASE_URI'] = params['local_url']
else:
    application.config['SQLALCHEMY_DATABASE_URI'] = params['production_url']

db = SQLAlchemy(application)


class Contact(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=False, nullable=False)
    email = db.Column(db.String(20), unique=False, nullable=False)
    phoneno = db.Column(db.String(12), unique=True, nullable=False)
    date = db.Column(db.String(12), unique=False, nullable=True)
    msg = db.Column(db.String(150), unique=False, nullable=False)


class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30), unique=False, nullable=False)
    subtitle = db.Column(db.String(50), unique=False, nullable=False)
    content = db.Column(db.String(200), unique=False, nullable=False)
    date = db.Column(db.String(12), unique=False, nullable=True)
    slug = db.Column(db.String(15), unique=False, nullable=False)
    img_files = db.Column(db.String(20), unique=False, nullable=False)


class Login(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    email_id = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(20), unique=True, nullable=False)


@application.route('/edit/<string:sno>', methods=["GET", "POST"])
def edit(sno):
    if ('user' in session and session['user'] == params['admin']):
        if (request.method == "POST"):

            post_sno = request.form.get("sno")
            post_title = request.form.get("Title")
            post_subtitle = request.form.get("Subtitle")
            post_content = request.form.get("Content")
            post_slug = request.form.get("slugs")
            post_image = request.form.get("image")
            date = datetime.now()

            if sno=='0':

                post = Posts( title=post_title, subtitle=post_subtitle,
                             content=post_content, slug=post_slug , date = date , img_files= post_image)
                db.session.add(post)
                db.session.commit()
                

            else:
                post = Posts.query.filter_by(sno=sno).first()
                post.title = post_title
                post.subtitle = post_subtitle
                post.content = post_content
                post.slug = post_slug 

                db.session.commit()
                return redirect('/edit/'+sno)

    post = Posts.query.filter_by(sno=sno).first()
    return render_template('edit.html', params=params, post=post ,sno=sno)


@application.route('/delete/<string:sno>', methods=["GET", "POST"])
def delete(sno):
    if ('user' in session and session['user'] == params['admin']):
        post = Posts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
    return redirect('/login')

@application.errorhandler(404)
def page_not_found(e):
    print("e is that one:",e)
    return render_template('404.html'), 404


@application.route('/login', methods=['GET', 'POST'])
def login():

    if ('user' in session and session['user'] == params['admin']):
        posts = Posts.query.all()
        return render_template('dashboard.html', params=params, posts=posts)

    if (request.method == 'POST'):
        email_var = request.form.get("email")
        pass_var = request.form.get("pass")

        logins = Login(email_id=email_var, password=pass_var)

        db.session.add(logins)
        db.session.commit()

        if email_var == params['admin'] and pass_var == params['admin_answer']:
            # set the session variable ,if user is already loged in.
            session['user'] = email_var
            posts = Posts.query.all()
            return render_template('dashboard.html', params=params, posts=posts)

    return render_template('login.html', params=params)


@application.route('/post/<string:post_slug>', methods=["GET"])
def post(post_slug):

    post = Posts.query.filter_by(slug=post_slug).first()

    return render_template('post.html', params=params, post=post)


@application.route('/')
def home():

    posts = Posts.query.filter_by().all()

    return render_template('index.html', params=params, posts=posts)


@application.route('/logout')
def logout():

    session.pop('user')

    return redirect("/login")


@application.route('/contact', methods=['GET', 'POST'])
def contact():
    if(request.method == 'POST'):

        # add entries of contact info to the database:

        name_var = request.form.get("name")
        email_var = request.form.get("email")
        phoneno_var = request.form.get("phoneno")
        message_var = request.form.get("message")

        entry = Contact(name=name_var, email=email_var,
                        phoneno=phoneno_var, date=datetime.now(), msg=message_var)
        db.session.add(entry)
        db.session.commit()

    return render_template('contact.html', params=params)


@application.route('/about')
def about():
    return render_template('about.html', params=params)


if __name__ == "__main__":
    application.run(debug=True)
