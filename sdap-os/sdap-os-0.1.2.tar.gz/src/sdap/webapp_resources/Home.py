from flask_restful import Resource

class Home(Resource):

    def get(self):
        return "SDAP server with object storage back-end.\n " \
               "Apply algorithms to collections of earth observation data. \n" \
               "Next go to /collections , /operators or /jobs"