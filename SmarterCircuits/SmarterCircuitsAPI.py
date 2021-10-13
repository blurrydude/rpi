import time
import _thread
import json
from SmarterLogging import SmarterLog
from flask import request, url_for
from flask_api import FlaskAPI, status, exceptions
from flask_cors import CORS

class SmarterAPI:
    def __init__(self, mcp):
        self.mcp = mcp
        self.app = FlaskAPI(__name__)
        self.cors = CORS(self.app, resources={r"/*": {"origins": "*"}})

        @self.app.route('/pistates',methods=['GET'])
        def pistates():
            return self.mcp.peers
        
        @self.app.route('/states',methods=['GET'])
        def states():
            return self.mcp.config.circuits
        
        @self.app.route('/control/<text>')
        def control(text):
            self.mcp.mqtt.publish("smarter_circuits/command",text)

        _thread.start_new_thread(self.start, ())

    def start(self):
        self.app.run(debug=False, port=8080, host=self.mcp.ip_address)
