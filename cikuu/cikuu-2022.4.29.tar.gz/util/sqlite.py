# 2022.3.21
import fire,json,os,collections, sqlite3

class util(object):
	def __init__(self, dbfile): 
		self.conn	= sqlite3.connect(dbfile, check_same_thread=False)  
		self.conn.execute('PRAGMA synchronous=OFF')
		self.conn.execute('PRAGMA case_sensitive_like = 1')

	def loadjson(self, infile) :
		''' ''' 
		pass

	def dump(self, outfile) :
		''' ''' 
		pass


if __name__ == "__main__":  
	fire.Fire(util)