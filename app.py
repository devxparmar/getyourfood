import os
import pathlib
import requests
import pdfkit
from flask import Flask , render_template,session, abort , request , flash, url_for, redirect 
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests
from pathlib import Path



app = Flask(__name__)
app.config ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///food.db'
app.config ['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db=SQLAlchemy(app)

app.secret_key = "GetYourFood.com"

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

GOOGLE_CLIENT_ID = "755875403067-ol0189o364a521lca5ui0tsiik1nql5e.apps.googleusercontent.com"
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="https://getyourfood.social/auth"
)

def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)  # Authorization required
        else:
            return function()

    return wrapper

def must_login(function):
    def wrapper1(*args, **kwargs):
        if "google_id" not in session:
            return redirect("/login")
        else:
            return function()

    return wrapper1

def must_login1(function):
    def wrapper2(*args, **kwargs):
        if "google_id" not in session:
            return redirect("/login")
        else:
            return function()

    return wrapper2

class food(db.Model):
    sno = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100))
    pno = db.Column(db.String(10))
    email = db.Column(db.String(30))
    addr = db.Column(db.String(100))
    city = db.Column(db.String(50))
    state = db.Column(db.String(50))
    quantity = db.Column(db.Integer)
    #date_added = db.Column(db.DataTime, default=datetime.utcnow)
    def _repr_(self) -> str:
        return f"{self.sno} - {self.name}"

@app.route("/")
def Home():
    return render_template('index.html')


@app.route("/login")
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)

@app.route("/logout")
def logout():
    session.clear()
    f = open("user", "r+") 
    f.seek(0) 
    f.truncate() 
    return redirect("/")


@app.route("/auth")
def auth():
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        abort(500)  # State does not match!

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )
    user=open("user","w")
    user.write(id_info.get("email"))
    user.close()
    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    return redirect("/protected_index")


@app.route("/donate_food")
@must_login
def donate():
    return render_template('pr-6c.htm',email = session['name'])

@app.route("/collect_food")
@must_login1
def collect():
    all_create = food.query.all()
    return render_template('collect_food.htm' , all_create=all_create ,email = session['name'])

@app.route('/collect_food', methods=['GET', 'POST'])
def filter():
    if request.method=='POST':
        city = request.form['filter_city']
    food1= food.query.filter_by(city=city)
    all_create=food1.all()
    return render_template('collect_food.htm' , all_create=all_create , email = session['name'])

@app.route('/donate_food', methods=['GET', 'POST'])
def form():
    if request.method=='POST':
        name = request.form['txt1']
        pno = request.form['txt2']
        email = request.form['txt3']
        addr = request.form['txt4']
        city = request.form['txt5']
        state = request.form['txt6']
        quantity = request.form['txt7']
     
        food1 = food(name = name , pno = pno , email = email , addr = addr , city = city , state = state , quantity = quantity)
        db.session.add(food1)
        db.session.commit()
        
    all_create = food1.query.all() 
    return render_template('/protected_index.html', all_create=all_create, email = session['name'])

@app.route("/protected_index")
@login_is_required
def protected_index():
    return render_template('protected_index.html',email = session['name'])


@app.route('/delete/<int:sno>')
def delete(sno):
    food1 = food.query.filter_by(sno=sno).first()
    db.session.delete(food1)
    db.session.commit()
    return redirect("/protected_index")

@app.route('/print/<int:sno>')
def print(sno):
    food2 = food.query.filter_by(sno=sno).first()
    return render_template('pdf.htm' , food2 = food2)
if __name__=="__main__":
    app.run(debug=True,port=8000)
   
    
    
    
