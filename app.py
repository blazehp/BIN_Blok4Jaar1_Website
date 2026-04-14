# https://flask.palletsprojects.com/en/stable/tutorial/layout/

from flask import Flask, render_template, redirect

app = Flask(__name__)

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/blast')
def blast():
  return render_template('blast.html')

if __name__ == '__main__':
    # Start Server
    app.run(debug=True, port=3000)

