from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
  return 'Hello, World!'

@app.route('/d/<date>')
def fetch_date(date):
  return 'Hello, World! - {d}'.format(d=date)
