from quick_sqlite.quick_sqlite import QuickSqlite

#sq = SimpleSqlite()
key = b'pRmgMa8T0INjEAfksaq2aafzoZXEuwKI7wDe4c1F8AY='
err_path = './test/test_db'
database = QuickSqlite('test_db', False)
#database.alter_table('test', 'ADD', 'password CHAR (255)')
#database.insert_table('test', 'name, email, password', ['J', 'P', 'K'])
#database.insert_table('test', 'name, email, password', ['Y', 'A', 'S'])
#database.insert_table('test', 'name, email, password', ['Z', 'X', 'C'])
p = database.select_data('test', '*', 'name, password', ['Z', 'C'])
#database.create_table('test', 'name, email, password')
print(p)
