from flask import Flask
from datasources import WebEarningCalendar
from json import dumps

app = Flask(__name__)
calendar = WebEarningCalendar()

@app.route('/heartbeat')
def hello_world():
  return 'Hello, World!'

@app.route('/<date_str>')
def fetch_by_date(date_str):
  return dumps(calendar.get_for_date(date_str=date_str))
