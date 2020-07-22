#!/usr/bin/env python3
import os
from flask import Flask
from time import sleep

app = Flask(__name__)


# curl -x  localhost:8080 localhost:3001/person1 & curl -x  localhost:8080 localhost:3001/person2 &
@app.route('/<name>')
def hello(name):
    sleep(2)
    return f"Hello {name}!"


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=3001, threaded=True)
