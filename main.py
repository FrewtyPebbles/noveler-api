from datetime import timedelta
from flask import Flask, render_template, request, session
import hashlib
from config import *
from utility import *

app = Flask(__name__)
app.secret_key = secrets["secret_key"]

@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(days=3)


@app.route("/", methods=["GET","POST"])
def root():
    return base_response


@app.route(f"/login", methods=["POST"])
def login():

    if "TOKEN" in session:
        
        return {
            "valid": proc_verify_token(session),
            "?": "Logged in with TOKEN.",
            **base_response
        }

    

    Email = request.form["Email"]
    Password = request.form["Password"]
    HAlg = hashlib.sha256(secrets["hash_hmac_key"].encode())
    HAlg.update(Password.encode())
    Password_hash = HAlg.hexdigest()
    print(Password_hash)
    db_cursor.execute("SELECT ID FROM account WHERE Email = %s AND Password = %s", (Email, Password_hash))
    if len(db_cursor.fetchall()) > 0:
        HAlg = hashlib.sha256(secrets["hash_hmac_key"].encode())
        HAlg.update((Password_hash + Email).encode())
        Token_hash = HAlg.hexdigest()
        print((Token_hash))
        session["TOKEN"] = Token_hash
        session["Email"] = Email

        return {
            "valid": True,
            **base_response
        }
    else:
        return {
            "error": "Account not found.",
            "valid": False,
            **base_response
        }
    
@app.route("/logout")
def logout():
    session.pop("TOKEN",None)
    session.pop("Email",None)
    return {
        **base_response
    }

@app.route(f"/register", methods=["POST"])
def register():
    Email:str = request.form["Email"]
    FName:str = request.form["FName"]
    LName:str = request.form["LName"]
    Password:str = request.form["Password"]
    
    HAlg = hashlib.sha256(secrets["hash_hmac_key"].encode())
    HAlg.update(Password.encode())
    Password_hash = HAlg.hexdigest()
    print(Password_hash)
    
    try:
        db_cursor.execute("""INSERT INTO account (FName, LName, Email, Password)
        VALUES (%s, %s, %s, %s)""", (FName, LName, Email, Password_hash))
        db_conn.commit()

        return {
            **base_response
        }
    except:
        return {
            "error":"An account already exists with the provided Email.",
            **base_response
        }

@app.route(f"/project-new", methods = ["POST"])
@verify_token
def new_project():
        Name = request.form["Name"]
        proj = Project(Name, session)
        proj.create()
        proj.add_manager(session.get("Email"))
        return {
            "name":Name,
            "managers":proj.get_managers(),
            "composers":proj.get_composers(),
            "sketchers":proj.get_sketchers(),
            "tags":proj.get_tags(),
            "writers":proj.get_writers(),
            **base_response
        }


@app.route(f"/project-list", methods=["GET", "POST"])
@verify_token
def list_projects():
    db_cursor.execute("""SELECT * FROM project;""")
    projects = db_cursor.fetchall()
    print(projects)
    return {
        "projects": projects,
        **base_response
    }

@app.route("/project/season-new", methods=["POST", "GET"])
@verify_token
def add_season():
    project = Project(request.form["ProjectName"], session)
    Name = request.form["Name"]
    Description = request.form["Description"]
    return {
        "success":project.add_season(Name, Description),
        **base_response
    }

@app.route("/project/season-list", methods=["POST", "GET"])
@verify_token
def list_seasons():
    project = Project(request.form["ProjectName"], session)
    return {
        "seasons":project.get_seasons(),
        **base_response
    }


@app.route("/project/season/<int:season_number>/episode-new", methods=["POST", "GET"])
@verify_token
def add_episode(season_number:int):
    project = Project(request.form["ProjectName"], session)
    Name = request.form["Name"]
    Description = request.form["Description"]
    
    return {
        "season number":season_number,
        "success":project.add_episode(season_number, Name, Description),
        **base_response
    }

@app.route("/project/season/episode-new", methods=["POST", "GET"])
@verify_token
def add_episode_with_form():
    project = Project(request.form["ProjectName"], session)
    Name = request.form["Name"]
    Description = request.form["Description"]
    season_number = request.form["Season"]
    
    return {
        "season number":season_number,
        "success":project.add_episode(season_number, Name, Description),
        **base_response
    }

@app.route("/project/season/<int:season_number>/episode-list", methods=["POST", "GET"])
@verify_token
def list_episode(season_number:int):
    project = Project(request.form["ProjectName"], session)
    Name = request.form["Name"]
    Description = request.form["Description"]
    
    return {
        "season number":season_number,
        "episodes":project.list_episodes(season_number, Name, Description),
        **base_response
    }

@app.route("/project/season/episode-list", methods=["POST", "GET"])
@verify_token
def list_episode_with_form():
    project = Project(request.form["ProjectName"], session)
    Name = request.form["Name"]
    Description = request.form["Description"]
    season_number = request.form["Season"]
    
    return {
        "season number":season_number,
        "success":project.list_episodes(season_number, Name, Description),
        **base_response
    }