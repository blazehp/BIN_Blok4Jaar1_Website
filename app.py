# https://flask.palletsprojects.com/en/stable/tutorial/layout/

from flask import Flask, render_template, redirect
import os
from dotenv import load_dotenv

# Load environment variables into the server
# This is the .env when in development mode
load_dotenv()

app = Flask(__name__)

DB_URL = os.getenv("DB_URL")

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/blast')
def blast():
  return render_template('blast.html')

if __name__ == '__main__':
    # Start Server
    app.run()

