# from wtforms.fields import form



import os
import random
from configuration import app, db, mail,babel
from flask import render_template, redirect, session, flash,request
from form import Signup, Login, NewsForm, SubscribeForm, Forgot, NewPswd, SearchForm, UserForm, AnswerButtonForm, AnswerForm
from db import Author, News, Answer
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from flask_bcrypt import Bcrypt
random = str(random.randint(0,999999))
sec = URLSafeTimedSerializer("Thisissecrettime")
bcrypt = Bcrypt(app)
a = []

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
    file_name, file_extension = os.path.splitext(file_from_form.filename)
    file = random + file_extension
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
        return redirect("/")
    return render_template("forget_email.html",form=form)



@app.route("/iforget/<token>",methods=['GET', 'POST'])
def i_forget(token):
    try:
        email = sec.loads(token,salt="reset",max_age=3600)
    except SignatureExpired:
        return "Your token link time out"
    author = Author.query.filter_by(email=email).first()
    form2 = NewPswd()
    if author:
        if form2.validate_on_submit():
            hash_pswd = bcrypt.generate_password_hash(form2.pswd.data).decode('utf-8')
            author.pswd = hash_pswd
            db.session.commit()
            return redirect("/login")
    return render_template("new_pswd.html", form2=form2)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = Login()
    if form.validate_on_submit():
        author_login = Author.query.filter_by(email=form.email.data).first()
        if author_login.confirmed == "1":
            if author_login and bcrypt.check_password_hash(author_login.pswd,form.pswd.data):
                session['id'] = author_login.id
                return redirect('/')
            else:
                flash("Your password or email not correct")
        else:
            flash("Confirm your email please")
    return render_template("login.html", form=form)


@app.route("/regist", methods=['GET', 'POST'])
def regist():
    form = Signup()
    if form.validate_on_submit():
        print(form)
        print(form.data)
        hash_pswd = bcrypt.generate_password_hash(form.pswd.data).decode('utf-8')
        author_signup = Author(sname=form.sname.data, email=form.email.data, pswd=hash_pswd)
        email = form.email.data
        token = sec.dumps(email, salt="email-confirm")
        msg = Message(subject='Confrim your email', body='http://127.0.0.1:5000/{}'.format(token), recipients=[email])
        mail.send(msg)
        flash("Massege sended to your email")
        db.session.add(author_signup)



        return redirect("/")
        # db.session.commit()  # i will save this account after email check

    return render_template("regist.html", form=form)

@app.route('/<token>',methods=['GET'])
def confirm(token):
    print(token)

    try:
        email = sec.loads(token, salt="email-confirm", max_age=3600)
        author_login = Author.query.filter_by(email=email).first()
        if author_login:
            author_login.confirmed = "1"
            db.session.commit()
        return redirect("/login")
    except SignatureExpired:

        return "Your token link time out"
    # return render_template('parent.html', message='signup done!')


@app.route("/post", methods=['GET','POST'])
def post():
    form = UserForm()
    author_login = Author.query.filter_by(id=session.get('id')).first()
    news = News.query.all()
    id = author_login.id
    form2 = AnswerButtonForm()
    form3 = AnswerForm()
    if form.validate_on_submit():
        user = Author.query.filter_by(id=session.get('id')).first()
        # user_account(user)
    if form2.validate_on_submit():
        answers = Answer.query.filter_by(post_id=form2.post_id.data)
        postid = form2.post_id.data
    if form3.validate_on_submit():
        post_fresh_answer = Answer(answer=form3.answer.data, post_id=postid)
        db.session.add(post_fresh_answer)
        db.session.commit()

        return render_template("answer.html", form3=form3,answers=answers)


    return render_template("post.html", news=news,form=form, form2=form2)



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
    author = Author.query.all()
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

    return render_template("my_account.html", news=news,form=form,id=id,followers_id=followers_id,author=author)




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



@app.route('/settings', methods=['GET', 'POST'])
def settings():
    return render_template("settings.html")

@app.route('/author', methods=['GET', 'POST'])
def user_account(user):
    if 'id' in session:
        news = user.author_news

    return render_template("user_account.html", user=user, news=news)



if __name__=="__main__":
    app.run(debug=True)


