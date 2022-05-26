class NoFetchError(Exception):
    #Used when a fetched pdb file is required but not provided
    def __init__(self):
        self.message = 'No fetched protein. Use method Fetch(PDB_CODE) to fetch a protein.\n'
        return self.message

    def __str__(self):
        return self.message

class BadInternet(Exception):
    def __init__(self):
        self.message = 'Poor or no internet connection. Some functionality may be lost\n\t' \
                       r'Connection to http://www.google.com timeout or failure'

    def __str__(self):
        return self.message

class BadKwarg(Exception):
    def __init__(self, accepted):
        self.message = f'Bad parameter provided. Accepted parameters are as follows: {accepted}'

    def __str__(self):
        return self.message