# from wtforms.fields import form
import secrets


import os
from configuration import app, db, mail,babel
from flask import render_template, redirect, session, flash,request
from form import Signup, Login, NewsForm, SubscribeForm, Forgot, NewPswd, SearchForm
from db import Author, News
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from flask_bcrypt import Bcrypt

sec = URLSafeTimedSerializer("Thisissecrettime")
bcrypt = Bcrypt(app)

@app.before_first_request
def creat_all():
    db.create_all()


@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(app.config['LANGUAGES'])







@app.route("/")
def index():
    form = SearchForm()
    if "id" in session:
        return render_template("index.html",form=form)
    else:
        return render_template("newindex.html")


@app.route('/logout')
def logout():
    session.clear()  # remove author from session
    return redirect('/')


def save_file(file_from_form):  # with python's "os" function we will save news-image into 'static/images' folder
    file_name, file_extension = os.path.splitext(file_from_form)
    file = file_name + file_extension
    print(file)
    file_path = os.path.join(app.root_path, 'static/images', file)
    print(file_path)
    file_from_form.save(file_path)
    print(file)
    return file


@app.route('/add_article', methods=['GET', 'POST'])
def add_article():
    if 'id' in session:
        author_login = Author.query.filter_by(id=session.get('id')).first()
        form = NewsForm()
        if form.validate_on_submit():
            print(form.img.data.filename)  # just to show, image filename
            if form.img.data:
                file = save_file(form.img.data)
                print(file)  # just to show, image data
                news_create = News(title=form.title.data, gender=form.gender.data, year=form.year.data, img=file, text=form.text.data, author=author_login)
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
        if author_login and bcrypt.check_password_hash(author_login.pswd,form.pswd.data):
            session['id'] = author_login.id
            return redirect('/')
    return render_template("login.html", form=form)


@app.route("/regist", methods=['GET', 'POST'])
def regist(self):
    form = Signup()
    if form.validate_on_submit():
        print(form)
        print(form.data)
        hash_pswd = bcrypt.generate_password_hash(form.pswd.data).decode('utf-8')
        self.author_signup = Author(sname=form.sname.data, email=form.email.data, pswd=hash_pswd)
        email = form.email.data
        token = sec.dumps(email, salt="email-confirm")
        msg = Message(subject='Confrim your email', body='http://127.0.0.1:5000/{}'.format(token), recipients=[email])
        mail.send(msg)
        flash("Massege sended")
        return  redirect("/")
       #db.session.add(author_signup)  # adding Author-class instance into db
        # db.session.commit()  # i will save this account after email check

    return render_template("regist.html", form=form)

@app.route('/<token>',methods=['GET'])
def confirm(token,self):
    print(token)
    try:
        email = sec.loads(token,salt="email-confirm",max_age=1800)
    except SignatureExpired:
        return "Your token link time out"
    db.session.add(self.author_signup)
    db.session.commit()
    return render_template('parent.html', message='signup done!')


@app.route("/post", methods=['GET','POST'])
def post():

    author_login = Author.query.filter_by(id=session.get('id')).first()
    news = News.query.all()
    id = author_login.id
    return render_template("post.html", news=news)



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


@app.route("/myaccount", methods=['GET', 'POST'])
def my_account():
    form = SubscribeForm()
    if 'id' in session:
        author_login = Author.query.filter_by(id=session.get('id')).first()
        news = News.query.all()
        id = author_login.id
        if form.validate_on_submit():
            a = Author.query.filter_by(id=form.author_id.data).first()
            # a.subscribes.append(author_login)
            author_login.subscribes.append(a)
            db.session.commit()
        followers_id = []
        for i in author_login.subscribes:
            followers_id.append(i.id)

    return render_template("my_account.html", news=news,form=form,id=id,followers_id=followers_id)




@app.route("/mysub", methods=['GET', 'POST'])
def mysub():
    news = []
    if 'id' in session:
        author_login = Author.query.filter_by(id=session.get('id')).first()
        followers = []
        for i in author_login.subscribes:
            followers.append(i.id)
            news = News.query.filter(News.author_id.in_(followers)).all()

    return render_template("mysub.html", news=news)


@app.route('/answers', methods=['GET', 'POST'])
def answer():
    return render_template("answer.html")


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    return render_template("settings.html")





if __name__=="__main__":
    app.run(debug=True)