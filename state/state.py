import json
import os

class AgentState(object):
    def __init__(self):
        if not os.path.exists("state.json"):
            json.dump({}, open("state.json", "w")) 
        self.state = json.load(open("state.json", "r"))

    def get(self, key):
        return self.state.get(key, None)

    def set(self, key, value):
        self.state[key] = value
        json.dump(self.state, open("state.json", "w"))
