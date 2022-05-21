import LibHanger.Models.modelFields as fld
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.elements import Null

# Baseクラス生成
Base = declarative_base()

class log_race_id(Base):
	
	# テーブル名
	__tablename__ = 'log_race_id'
	
	# スキーマ
	__table_args__ = {'schema': 'nkaz'}
	
	# 列定義
	race_id = fld.CharFields(12,primary_key=True,default='')
	create_datetime = fld.DateTimeFields(default=Null)
	result = fld.NumericFields(1,0,default=0)
	uuid = fld.CharFields(40,default='')
	type = fld.CharFields(50,default='')
	value = fld.CharFields(50,default='')
	stacktrace = fld.CharFields(2000,default='')
	error_point = fld.CharFields(30,default='')
	updinfo = fld.CharFields(40,default='')
