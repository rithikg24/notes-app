from flask import Flask,render_template,request,flash,redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin,login_user,login_required,logout_user,current_user,LoginManager
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash,check_password_hash

app = Flask(__name__)
app.secret_key = "super secret key"


db_name="notes.db"

app.config['SQLALCHEMY_DATABASE_URI']=f"sqlite:///{db_name}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

db=SQLAlchemy(app)

class Note(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    data=db.Column(db.String(10000))
    date=db.Column(db.DateTime(timezone=True),default=func.now())
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email=db.Column(db.String(200),unique=True)
    password=db.Column(db.String(200))
    name=db.Column(db.String(200))
    notes=db.relationship('Note') 

login_manager=LoginManager()
login_manager.login_view="/login"
login_manager.init_app(app)
login_status=0

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route("/")
def home():
    return render_template('home.html',login_status=login_status)
    #return "<h1>Test</h1>"

@app.route("/login",methods=['GET',"POST"])
def login():
    if request.method=="POST":
        email=request.form['email']
        password=request.form['password']

        user=User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password,password):
                #flash("Logged In Successfully!!",category='success')
                login_status=1
                login_user(user,remember=True)
                return redirect("/dashboard")
            else:
                flash("Incorrect Password, Try Again",category='error')
        else:
            flash("Email does not exist.",category='error')
    return render_template('login.html',user=current_user)

@app.route("/signup",methods=['GET',"POST"])
def sign_up():
    if request.method=='POST':
        name=request.form['name']
        email=request.form['email']
        password=request.form['password']
        confirm_password=request.form['confirm_password']

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(name) < 2:
            flash('Name must be greater than 1 character.', category='error')
        elif password != confirm_password:
            flash('Passwords don\'t match.', category='error')
        elif len(password) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = User(email=email, name=name, password=generate_password_hash(
                password, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            #login_user(new_user, remember=True)
            flash('Account created!', category='success')
            login_user(user,remember=True)
            login_status=1
            return redirect("/dashboard")

    return render_template('signup.html',user=current_user)


@app.route("/dashboard",methods=['POST',"GET"])
@login_required
def dashboard():
    if request.method=="POST":
        note=request.form['data']
        new_note = Note(data=note)
        db.session.add(new_note)
        db.session.commit()
        flash('Note added!', category='success')
    
    notes_list=Note.query.all()
    return render_template("dashboard.html",notes_list=notes_list)

@app.route("/edit/<int:id>",methods=['POST','GET'])
def edit(id):
    if request.method=='POST':
        note=Note.query.filter_by(id=id).first()
        note.data=request.form['data']
        note.id=id
        db.session.add(note)
        db.session.commit()
        flash("Note Updated Successfully!!",category="success")
        return redirect("/dashboard")
    note=Note.query.filter_by(id=id).first()
    return render_template("edit.html",note=note)
    

@app.route("/delete/<int:id>")
def delete(id):
    note=Note.query.filter_by(id=id).first()
    db.session.delete(note)
    db.session.commit()
    return redirect("/dashboard")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged Out Successfully!!",category='success')
    return redirect("/login")


if __name__=='__main__':
    app.run(debug=True)


