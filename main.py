from flask import Flask,request,session,redirect
from flask import render_template
from datetime import datetime
from werkzeug import secure_filename
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
import json
import os,math
with open('config.json','r') as c:
    params= json.load(c)["params"]
local_server=True
app = Flask(__name__)
app.secret_key='super-secret-key'
app.config['UPLOAD_FOLDER']=params['upload_location']
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL=True,
    MAIL_USERNAME=params['gmail-user'],
    MAIL_PASSWORD=params['gmail-pass']
)
mail=Mail(app)
if(local_server):
 app.config["SQLALCHEMY_DATABASE_URI"] = params['local_uri']
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = params['prod_uri']
db = SQLAlchemy(app)

class Contact(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(20), unique=True, nullable=False)
    phone_num = db.Column(db.String(12), unique=True)
    mes = db.Column(db.String(90), unique=False, nullable=False)
    date = db.Column(db.String(12), unique=True,nullable=True)

class Post(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title= db.Column(db.String(80), unique=False, nullable=False)
    slug = db.Column(db.String(20), unique=True, nullable=False)
    content = db.Column(db.String(120))
    date = db.Column(db.String(12), unique=True,nullable=True)
    tagline= db.Column(db.String(29), unique=True, nullable=True)
    img_file = db.Column(db.String(12), unique=True, nullable=True)
class Dash(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False)
    phone_num = db.Column(db.String(12), unique=True,nullable=False)
    email = db.Column(db.String(20),unique=True, nullable=False)
    password= db.Column(db.String(10), unique=True, nullable=False)
    date = db.Column(db.String(8), unique=True, nullable=True)
@app.route("/")
def home():
  posts = Post.query.filter_by().all()
  last=math.ceil(len(posts)/int(params['no_of_post']))
  page=request.args.get('page')
  if(not str(page).isnumeric()):
      page = 1
  page=int(page)
  posts=posts[(page-1)*int(params['no_of_post']):(page-1)*int(params['no_of_post'])+int(params['no_of_post'])]
  if(page==1):
      prev="#"
      next="/?page="+ str(page+1)
  elif(page == last):
      prev = "/?page=" + str(page - 1)
      next ="#"
  else:
      prev = "/?page=" + str(page - 1)
      next = "/?page=" + str(page + 1)

  return render_template ("index.html",params=params,posts=posts,prev=prev,next=next)
@app.route("/about")
def about():
  return render_template ("about.html",params=params)
@app.route("/logout")
def logout():
    session.pop('user')
    return redirect('/dash')

@app.route("/signin",methods = ['GET','POST'])
def signin():
    if (request.method == 'POST'):
        '''Addd Entry To the Database'''
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        phone = request.form.get('phone_num')
        entry = Dash(email=email, password=password, date=datetime.now(),name=name,phone_num=phone)
        db.session.add(entry)
        db.session.commit()
    return render_template ("signin.html",params=params,multiparams=params)

@app.route("/admin")
def admin():
  return render_template ("admin.html",params=params)

@app.route("/uploader",methods = ['GET','POST'])
def uploader():
    if 'user' in session and session['user'] == params['admin_user']:
     if(request.method=='POST'):
        f=request.files['file1']
        f.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(f.filename)))
        return "Uploaded Successfully"


@app.route("/dash",methods = ['GET','POST'])
def dash():

    if 'user' in session and session['user']==params['admin_user']:
        post = Post.query.all()
        return render_template("dashbord.html", params=params,post=post)
    if(request.method=='POST'):
        username=request.form.get('uname')
        userpass = request.form.get('pass')
        if(username==params['admin_user'] and userpass==params['admin_password']):
            #session variable
            session['user']=username
            post=Post.query.all()
            return render_template("dashbord.html", params=params,post=post)

    return render_template ("login.html",params=params)

@app.route("/post/<string:post_slug>", methods=['GET'])
def post_route(post_slug):
  post=Post.query.filter_by(slug=post_slug).first()

  return render_template ("post.html",params=params,post=post)

@app.route("/delete/<string:sno>", methods=['GET','POST'])
def delete(sno):
  if ('user' in session and session['user'] == params['admin_user']):
      post=Post.query.filter_by(sno=sno).first()
      db.session.delete(post)
      db.session.commit()

  return redirect('/dash')
@app.route("/edit/<string:sno>",methods=['GET','POST'])
def edit(sno):
    if 'user' in session and session['user'] == params['admin_user']:
        if request.method=='POST':
            box_title=request.form.get('title')
            tline=request.form.get('tline')
            slug=request.form.get('slug')
            content=request.form.get('content')
            img_file=request.form.get('img_file')
            date=datetime.now()
            if sno=='0':
                post=Post(title=box_title,tagline=tline,slug=slug,content=content,img_file=img_file,date=date)
                db.session.add(post)
                db.session.commit()
            else:
                post=Post.query.filter_by(sno=sno).first()
                post.title=box_title
                post.slug=slug
                post.content=content
                post.tagline=tline
                post.date=date
                db.session.commit()
                return redirect('/edit/'+sno)
        post=Post.query.filter_by(sno=sno).first()
        return render_template ("edit.html",params=params,post=post)


@app.route("/contact",methods = ['GET','POST'])
def contact():
  if(request.method =='POST'):
    '''Addd Entry To the Database'''
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone_num')
    mes = request.form.get('mes')
    entry = Contact(name=name,phone_num=phone,mes=mes,date=datetime.now(),email=email)
    db.session.add(entry)
    db.session.commit()
    mail.send_message('New Message from Blog '+name,sender=email,recipients=[params['gmail-user']],body= mes +"\n"+ phone)
  return render_template ("contact.html",params=params)

app.run(debug=True)