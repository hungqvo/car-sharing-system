from app import app
from flaskext.mysql import MySQL
from pathlib import Path
from dotenv import load_dotenv
import os
load_dotenv(verbose=True)
env_path = os.getcwd()
load_dotenv(dotenv_path= env_path + '/.env')
mysql = MySQL()
# app.config['MYSQL_DATABASE_USER'] = ""
# app.config['MYSQL_DATABASE_PASSWORD'] = ""
# app.config['MYSQL_DATABASE_DB'] = ""
# app.config['MYSQL_DATABASE_HOST'] = ""
app.config['MYSQL_DATABASE_USER'] = os.getenv("USERR")
app.config['MYSQL_DATABASE_PASSWORD'] = os.getenv("PASSWORD")
app.config['MYSQL_DATABASE_DB'] = os.getenv("DATABASE")
app.config['MYSQL_DATABASE_HOST'] = os.getenv("HOST")
mysql.init_app(app)