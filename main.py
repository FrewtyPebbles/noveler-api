from datetime import timedelta
from functools import wraps
import inspect
import json as JSON
from flask import Flask, jsonify, make_response, render_template, request
import hashlib
from config import *
from utility import *
from flask_cors import CORS
import jwt

app = Flask(__name__)
cors = CORS(app)

app.config["SECRET_KEY"] = secrets["secret_key"]

@app.route("/", methods=["GET","POST"])
def root():
    return base_response


def verify_token(func):
    def wrapper(*args, **kwargs):
        token = request.json["token"]
        if not token:
            return {"message":"Token is missing."}, 403
        try:
            kwargs["_jwt_data"] = jwt.decode(token, app.config["SECRET_KEY"], algorithms=['HS256'])
            return func(*args, **kwargs)
        except:
            return {"message": "Token is not valid."}, 403

    wrapper.__name__ = func.__name__
    return wrapper

@app.route(f"/login", methods=["POST","GET"])
def login():
    #### LOGOUT IS HANDLED BY CLIENT
    auth = request.authorization

    if auth:
        #auth is not null so hash password
        print(auth.password)
        Password = auth.password
        HAlg = hashlib.sha256(secrets["hash_hmac_key"].encode())
        HAlg.update(Password.encode())
        Password_hash = HAlg.hexdigest()
        print(Password_hash)
        conn = pymysql.connect(**db_conf)
        curr = conn.cursor()
        curr.execute("SELECT ID FROM account WHERE Email = %s AND Password = %s", (auth.username, Password_hash))
        
        if len(curr.fetchall()) > 0:
            # Login exists in database

            token = jwt.encode({
                'Username':auth.username,
                'Password':Password_hash,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
            }, app.config["SECRET_KEY"])
            
            return {
                "token":token,
                "valid": True,
                **base_response
            }

    return make_response({
        "error": "Account not found.",
        "valid": False,
        **base_response
    }, 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})

@app.route(f"/register", methods=["POST"])
def register():
    Email:str = request.json["Email"]
    FName:str = request.json["FName"]
    LName:str = request.json["LName"]
    Password:str = request.json["Password"]
    
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
def new_project(_jwt_data):
        Name = request.json["Name"]
        proj = Project(Name, _jwt_data)
        proj.create()
        proj.add_manager(_jwt_data["Username"])
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
def list_projects(_jwt_data):
    db_cursor.execute("""SELECT * FROM project;""")
    projects = db_cursor.fetchall()
    print(projects)
    return {
        "projects": projects,
        **base_response
    }

@app.route("/project/season-new", methods=["POST", "GET"])
@verify_token
def add_season(_jwt_data):
    project = Project(request.json["ProjectName"], _jwt_data)
    Name = request.json["Name"]
    Description = request.json["Description"]
    return {
        "success":project.add_season(Name, Description),
        **base_response
    }

@app.route("/project/season-list", methods=["POST", "GET"])
@verify_token
def list_seasons(_jwt_data):
    project = Project(request.json["ProjectName"], _jwt_data)
    return {
        "seasons":project.get_seasons(),
        **base_response
    }


@app.route("/project/season/<int:season_number>/episode-new", methods=["POST", "GET"])
@verify_token
def add_episode(_jwt_data, season_number:int):
    project = Project(request.json["ProjectName"], _jwt_data)
    Name = request.json["Name"]
    Description = request.json["Description"]
    
    return {
        "season number":season_number,
        "success":project.add_episode(season_number, Name, Description),
        **base_response
    }

@app.route("/project/season/episode-new", methods=["POST", "GET"])
@verify_token
def add_episode_with_form(_jwt_data):
    project = Project(request.json["ProjectName"], _jwt_data)
    Name = request.json["Name"]
    Description = request.json["Description"]
    season_number = request.json["Season"]
    
    return {
        "season number":season_number,
        "success":project.add_episode(season_number, Name, Description),
        **base_response
    }

@app.route("/project/season/<int:season_number>/episode-list", methods=["POST", "GET"])
@verify_token
def list_episode(_jwt_data, season_number:int):
    project = Project(request.json["ProjectName"], _jwt_data)
    Name = request.json["Name"]
    Description = request.json["Description"]
    
    return {
        "season number":season_number,
        "episodes":project.list_episodes(season_number, Name, Description),
        **base_response
    }

@app.route("/project/season/episode-list", methods=["POST", "GET"])
@verify_token
def list_episode_with_form(_jwt_data):
    project = Project(request.json["ProjectName"], _jwt_data)
    Name = request.json["Name"]
    Description = request.json["Description"]
    season_number = request.json["Season"]
    
    return {
        "season number":season_number,
        "success":project.list_episodes(season_number, Name, Description),
        **base_response
    }

@app.route("/project/character-new", methods=["POST", "GET"])
@verify_token
def add_character(_jwt_data):
    project = Project(request.json["ProjectName"], _jwt_data)
    
    return {
        "success":project.add_character(request.json["Name"], request.json["ShortSummary"], request.json["About"]),
        **base_response
    }

@app.route("/project/event-new", methods=["POST", "GET"])
@verify_token
def add_event(_jwt_data):
    project = Project(request.json["ProjectName"], _jwt_data)
    
    return {
        "success":project.add_event(request.json["Title"], request.json["Time"], request.json["Description"]),
        **base_response
    }

@app.route("/project/place-new", methods=["POST", "GET"])
@verify_token
def add_place(_jwt_data):
    project = Project(request.json["ProjectName"], _jwt_data)
    
    return {
        "success":project.add_place(request.json["Name"], request.json["ShortSummary"], request.json["Abstract"], request.json["Description"]),
        **base_response
    }

@app.route("/project/character/<string:character>/role-new", methods=["POST", "GET"])
@verify_token
def add_role(_jwt_data, character:str):
    project = Project(request.json["ProjectName"], _jwt_data)
    
    return {
        "success":project.add_character_role(character, request.json["Title"], request.json["Description"]),
        **base_response
    }

@app.route("/project/character/<string:character>/relationship-new", methods=["POST", "GET"])
@verify_token
def add_relationship(_jwt_data, character:str):
    project = Project(request.json["ProjectName"], _jwt_data)
    
    return {
        "success":project.add_relationship(character, request.json["OtherCharacter"], request.json["Title"], request.json["Description"]),
        **base_response
    }

@app.route("/project/character/<string:character>/lives-in-new", methods=["POST", "GET"])
@verify_token
def add_lives_in(_jwt_data, character:str):
    project = Project(request.json["ProjectName"], _jwt_data)
    
    return {
        "success":project.add_live_in(
            character,
            request.json["Place"],
            request.json["RelationTitle"],
            request.json["RelationDescription"]
        ),
        **base_response
    }

@app.route("/project/event/<string:Event>/in-event-new", methods=["POST", "GET"])
@verify_token
def add_character_in_event(_jwt_data, Event:str):
    project = Project(request.json["ProjectName"], _jwt_data)
    
    return {
        "success":project.add_person_in_event(
            Event,
            request.json["Character"],
            request.json["RoleTitle"],
            request.json["Description"]
        ),
        **base_response
    }

@app.route("/project/place/<string:ParentPlace>/in-place-new", methods=["POST", "GET"])
@verify_token
def add_place_in_place(_jwt_data, ParentPlace:str):
    project = Project(request.json["ProjectName"], _jwt_data)
    
    return {
        "success":project.add_place_in_place(
            request.json["InnerPlace"],
            ParentPlace,
            request.json["RelationTitle"],
            request.json["RelationDescription"]
        ),
        **base_response
    }

@app.route("/project/place/<string:Place>/event-new", methods=["POST", "GET"])
@verify_token
def add_event_in_place(_jwt_data, Place:str):
    project = Project(request.json["ProjectName"], _jwt_data)
    
    return {
        "success":project.add_event_in_place(
            Place,
            request.json["Event"]
        ),
        **base_response
    }

@app.route("/project-list-by-manager", methods=["POST", "GET"])
@verify_token
def list_managed_projects(_jwt_data:dict):
    try:
        conn = pymysql.connect(**db_conf)
        curr = conn.cursor()
        curr.execute("""
            SELECT p.*
            FROM project p, account a, manager m
            WHERE p.ID = m.ProjectID
            AND m.ManagerID = a.ID
            AND a.Email = %s""", (_jwt_data["Username"],))
        projects = curr.fetchall()
        proj_list = []
        for proj in projects:
            # get emails of managers
            curr.execute("""
            SELECT a.Email, a.FName
            FROM project p, account a, manager m
            WHERE a.ID = m.ManagerID
            AND m.ProjectID = p.ID
            AND p.Name = %s""", (proj["Name"],))
            managers = curr.fetchall()
            proj_list.append({
                "Project":proj,
                "Managers":managers
            })
        print(proj_list)
        return {
            "projects":proj_list,
            **base_response
        }
    except:
        return {
            "success":False,
            **base_response
        }