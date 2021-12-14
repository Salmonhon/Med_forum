# from wtforms.fields import form
import secrets

import form
from configuration import app,db,mail
from flask import render_template,redirect,session,flash
from form import Signup,Login,NewsForm,SubscribeForm,Forgot,NewPswd
from db import Author, News
from flask_mail import Message
from random import *
from itsdangerous import URLSafeTimedSerializer,SignatureExpired

sec = URLSafeTimedSerializer("Thisissecrettime")
otp = randint(1, 9999999)

@app.before_first_request
def creat_all():
    db.create_all()



@app.route("/")
def index():
    if "id" in session:
        return render_template("parent1.html")
    return render_template("newindex.html")


@app.route('/logout')
def logout():
    session.clear()  # remove author from session
    return redirect('/')


@app.route("/add_article", methods=['GET', 'POST'])
def add_article():
    if 'id' in session:
        author_login = Author.query.filter_by(id=session.get('id')).first()
        form = NewsForm()
        if form.validate_on_submit():
            news_create = News(title=form.title.data, intro=form.intro.data, text=form.text.data, author=author_login)
            print(news_create)  # just to show published news
            db.session.add(news_create)
            db.session.commit()
            return redirect('/post')
        return render_template('add-article.html', form=form)
    else:
        return redirect('/')





@app.route("/forgot_password",methods=['GET', 'POST'])
def forgot():
    form = Forgot()
    if form.validate_on_submit():
        auth = Author.query.filter_by(email=form.email.data).first()
        email = form.email.data
        token = sec.dumps(email, salt="reset")
        print("first part")
        msg = Message(subject='Link for reset your password', body='http://127.0.0.1:5000/iforget/{}'.format(token), recipients=[email])
        print("second part")
        flash("Link for reset is sended")
        mail.send(msg)

    return render_template("forget_email.html",form=form)



@app.route("/iforget/<token>",methods=['GET', 'POST'])
def i_forget(token):
    try:
        email = sec.loads(token,salt="reset",max_age=30)
    except SignatureExpired:
        return "Your token link time out"
    form = Forgot()
    author = Author.query.filter_by(email=form.email.data).first()
    db.session.delete(author.pswd)
    form2 = NewPswd
    author_new_pswd = Author(pswd=form2.pswd.data)
    db.session.add(author_new_pswd)
    db.session.commit()
    return render_template("new_pswd.html",form2=form2)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = Login()

    if form.validate_on_submit():
        author_login = Author.query.filter_by(email=form.email.data).first()
        if author_login.pswd == form.pswd.data:
            session['id'] = author_login.id
            return redirect('/')
    return render_template("login.html", form=form)


@app.route("/regist", methods=['GET', 'POST'])
def regist():
    form = Signup()

    if form.validate_on_submit():
        print(form)
        print(form.data)
        author_signup = Author(sname=form.sname.data, email=form.email.data, pswd=form.pswd.data)
        email = form.email.data
        token = sec.dumps(email, salt="email-confirm")
        msg = Message(subject='Confrim your email', body='http://127.0.0.1:5000/{}'.format(token), recipients=[email])
        mail.send(msg)

        db.session.add(author_signup)  # adding Author-class instance into db
        # db.session.commit()  # save db
        return render_template('parent.html', message='Check your email!')
    return render_template("regist.html", form=form)

@app.route('/<token>',methods=['GET'])
def confirm(token):
    print(token)
    try:
        email = sec.loads(token,salt="email-confirm",max_age=30)
    except SignatureExpired:
        return "Your token link time out"
    db.session.commit()
    return render_template('parent.html', message='signup done!')


@app.route("/post", methods=['GET','POST'])
def post():
    form = SubscribeForm()
    author_login = Author.query.filter_by(id=session.get('id')).first()
    news = News.query.all()
    id = author_login.id
    # sub = Author.query.filter_by(author_login).all()
    print(author_login)
    if form.validate_on_submit():
        a = Author.query.filter_by(id=form.author_id.data).first()
        # a.subscribes.append(author_login)
        author_login.subscribes.append(a)
        db.session.commit()
    followers_id = []
    for i in author_login.subscribes:
        followers_id.append(i.id)
    print(author_login.subscribes,"count")

    return render_template("post.html", news=news, form=form, id=id, followers_id=followers_id)



@app.route("/subscriptions", methods=['GET', 'POST'])
def subscriptions():
    author_login = Author.query.filter_by(id=session.get('id')).first()
    followers_id = []
    for i in author_login.subscribes:
        followers_id.append(i.id)
        print(i.id,"qwert")
        news = News.query.filter(News.author_id.in_(followers_id)).all()
    print(author_login.subscribes,"chislo podpisok")

    print(news)

    return render_template("my_subscriptions.html", news=news)


@app.route("/new", methods=['GET', 'POST'])
def new():
    return render_template("newindex.html")

@app.route("/add", methods=['GET', 'POST'])
def add():
    return render_template("addPost.html")

@app.route("/parent1", methods=['GET', 'POST'])
def parent():
    return render_template("parent1.html")


if __name__=="__main__":
    app.run(debug=True)