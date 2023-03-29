from config import *
import hashlib
from flask.sessions import SessionMixin
from flask import session

def proc_verify_token(session: SessionMixin):
    if "Email" not in session:
        return False
    db_cursor.execute("SELECT Email, Password FROM account WHERE Email = %s", (session.get("Email"),))
        
    login_response = db_cursor.fetchone()
    HAlg = hashlib.sha256(secrets["hash_hmac_key"].encode())
    HAlg.update((login_response["Password"] + login_response["Email"]).encode())
    
    db_token = HAlg.hexdigest()
    return db_token == session.get("TOKEN")

def verify_token(func):
    def wrapper(*args, **kwargs):
        if proc_verify_token(session):
            return func(*args, **kwargs)

        else:
            return {
            "error":"Token invalid.",
            "redirect":"login",
            **base_response
            }
    wrapper.__name__ = func.__name__
    return wrapper

class Project:
    def __init__(self, project:str, session:SessionMixin) -> None:
        self.project = project
        self.session = session
        db_cursor.execute("""
        SELECT ID from project WHERE Name = %s
        """, (self.project,))
        self.ID = db_cursor.fetchone()["ID"]
        print(self.ID)
    
    def create(self):
        db_cursor.execute("""INSERT INTO project (Name)
        VALUES (%s)""", (self.project))
        db_conn.commit()

    def get_managers(self):
        db_cursor.execute("""
        SELECT ID, FName, LName, Email from account as acct WHERE
            acct.ID in (SELECT man.ManagerID from manager man inner join (SELECT * FROM project proj
            where proj.Name = %s) as p
            ON p.ID = man.ProjectID)
        """, (self.project,))
        return db_cursor.fetchall()

    def get_sketchers(self):
        db_cursor.execute("""
        SELECT ID, FName, LName, Email from account as acct WHERE
            acct.ID in (SELECT sket.SketcherID from sketcher sket inner join (SELECT * FROM project proj
            where proj.Name = %s) as p
            ON p.ID = sket.ProjectID)
        """, (self.project,))
        return db_cursor.fetchall()

    def get_composers(self):
        db_cursor.execute("""
        SELECT ID, FName, LName, Email from account as acct WHERE
            acct.ID in (SELECT comp.ComposerID from composer comp inner join (SELECT * FROM project proj
            where proj.Name = %s) as p
            ON p.ID = comp.ProjectID)
        """, (self.project,))
        return db_cursor.fetchall()
    
    def get_writers(self):
        db_cursor.execute("""
        SELECT ID, FName, LName, Email from account as acct WHERE
            acct.ID in (SELECT writ.WriterID from writer writ inner join (SELECT * FROM project proj
            where proj.Name = %s) as p
            ON p.ID = writ.ProjectID)
        """, (self.project,))
        return db_cursor.fetchall()
    
    def get_tags(self):
        db_cursor.execute("""
        SELECT * FROM project_tag
        WHERE ProjectID in (SELECT ID FROM project where project.Name = %s)
        """, (self.project,))
        return db_cursor.fetchall()
    
    def get_seasons(self):
        db_cursor.execute("""
        SELECT * FROM season s
        WHERE s.ProjectID = %s
        ORDER BY s.SeasonNumber
        """, (self.ID,))
        ret_data = ()
        tuples = db_cursor.fetchall()
        for record in tuples:
            db_cursor.execute("""
            SELECT * FROM episode e
            WHERE e.SeasonID = %s
            ORDER BY e.EpisodeNumber
            """, (record["ID"],))
            record["episodes"] = db_cursor.fetchall()
            ret_data += (record,)
        return ret_data
    
    def get_episodes(self):
        db_cursor.execute("""select e.* from episode e, season s WHERE e.SeasonID = s.ID AND s.ProjectID = %s ORDER BY e.EpisodeNumber""", (self.ID,))
        return db_cursor.fetchall()
    
    def get_episodes_by_season_num(self, SeasonNumber:int = 1):
        db_cursor.execute("""
        select e.* from episode e, season s, project p WHERE p.ID = %s
        AND s.ProjectID = p.ID
        AND e.SeasonID = s.ID
        AND s.SeasonNumber = %s
        """, (self.ID, SeasonNumber,))
        return db_cursor.fetchall()

    def get_episodes_by_season_name(self, Title:str):
        db_cursor.execute("""
        select e.* from episode e, season s, project p WHERE
        p.ID = %s
        AND s.ProjectID = p.ID
        AND e.SeasonID = s.ID
        AND s.Name = %s
        """, (self.ID, Title,))
        return db_cursor.fetchall()
    
    def add_tag(self, tag:str):
        try:
            db_cursor.execute("""
            INSERT INTO project_tag(Tag, ProjectID)
            (SELECT %s, proj.id FROM project as proj
            WHERE proj.Name = %s)
            """, (tag, self.project))
            db_conn.commit()
            return True
        except:
            return False
    
    def add_manager(self, email:str):
        try:
            db_cursor.execute("""INSERT INTO manager (ManagerID, ProjectID)
            (SELECT a.ID, p.ID FROM account a, project p
            WHERE p.Name = %s
            AND a.Email = %s)""", (self.project, email))
            db_conn.commit()
            return True
        except:
            return False

    def add_sketcher(self, email:str):
        try:
            db_cursor.execute("""INSERT INTO sketcher (SketcherID, ProjectID)
            (SELECT a.ID, p.ID FROM account a, project p
            WHERE p.Name = %s
            AND a.Email = %s)""", (self.project, email))
            db_conn.commit()
            return True
        except:
            return False

    def add_composer(self, email:str):
        try:
            db_cursor.execute("""INSERT INTO composer (ComposerID, ProjectID)
            (SELECT a.ID, p.ID FROM account a, project p
            WHERE p.Name = %s
            AND a.Email = %s)""", (self.project, email))
            db_conn.commit()
            return True
        except:
            return False

    def add_writer(self, email:str):
        try:
            db_cursor.execute("""INSERT INTO writer (WriterID, ProjectID)
            (SELECT a.ID, p.ID FROM account a, project p
            WHERE p.Name = %s
            AND a.Email = %s)""", (self.project, email))
            db_conn.commit()
            return True
        except:
            return False

    def add_season(self, Name:str = None, description:str = None):
        try:
            db_cursor.execute("""INSERT INTO season (SeasonNumber, Name, Description, ProjectID)
            (SELECT (count(s.ID) + 1) as seasonNum, %s, %s, p.ID FROM project p, season s
            WHERE p.Name = %s
            AND s.ProjectID = p.ID)
            """, (Name, description, self.project))
            db_conn.commit()
            print("counter")
            return True
        except:
            try:
                
                db_cursor.execute("""
                INSERT INTO season (SeasonNumber, Name, Description, ProjectID)
                (SELECT 1 as "SeasonNumber", %s as "Name", %s as "Description", p.ID as "ProjectID" FROM project as p WHERE p.Name = %s)
                """, (Name, description, self.project))
                db_conn.commit()
                print("literal")
                return True
            except:
                return False

    def add_episode(self, SeasonNumber:int = 1, Title:str = None, Description:str = None):
        try:
            db_cursor.execute("""INSERT INTO episode (SeasonID, EpisodeNumber, Title, Description, ProjectID)
            SELECT s.ID, (count(e.ID) + 1), %s, %s, p.ID FROM season s, project p, episode e
            WHERE p.Name = %s
            AND s.SeasonNumber = %s
            AND s.ProjectID = p.ID
            AND e.SeasonID = s.ID""", (Title, Description, self.project, SeasonNumber))
            db_conn.commit()
            return True
        except:
            try:
                db_cursor.execute("""INSERT INTO episode (SeasonID, EpisodeNumber, Title, Description, ProjectID)
                SELECT s.ID as "SeasonID", 1 as "EpisodeNumber", %s as "Title", %s as "Description", p.ID as "ProjectID" FROM season s, project p
                WHERE p.Name = %s
                AND s.SeasonNumber = %s
                AND s.ProjectID = p.ID
                """, (Title, Description, self.project, SeasonNumber))
                db_conn.commit()
                return True
            except:
                return False
        
    