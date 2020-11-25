from flask import Flask
from lib.datasources import WebEarningCalendar
from json import dumps

app = Flask(__name__)
calendar = WebEarningCalendar()

@app.route('/')
def hello_world():
  return 'Hello, World!'

@app.route('/d/<date_str>')
def fetch_by_date(date_str):
  return dumps(calendar.get_for_date(date_str=date_str))
