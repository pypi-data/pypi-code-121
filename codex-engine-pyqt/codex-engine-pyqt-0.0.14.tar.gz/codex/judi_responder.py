import json


class JudiResponder:
    def process_message(self, msg, table):
        for k in msg.keys():
            if k in table.keys():
                if callable(table[k]):
                    return table[k](msg[k])

                elif isinstance(msg[k], str):
                    return table[k][msg[k]]()
                    
                elif isinstance(msg[k], dict):
                    return self.process_message(msg[k], table[k])

        return ''
    
    def respond(self, string):
        message = json.loads(string)
        return self.process_message(message, self.response_tree)