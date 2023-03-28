import pymysql
import neat_notation as NN

secrets:dict = NN.load("secrets.neat")

VERSION = "0.0.1"
base_response = { "API_INFO" : {
    "version":VERSION,
    "about":"""An api tool for organizing graphic novels."""
}}

db_conf = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "testing",
    "password":"testing",
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
    "client_flag": pymysql.constants.CLIENT.MULTI_STATEMENTS,
    "database": "test_db"
}

db_conn = pymysql.connect(**db_conf)
db_cursor = db_conn.cursor()

#Create the schema
with open("schema.sql") as schema:
    schema_str = schema.read()

    db_cursor.execute(schema_str)
db_conn.commit()