import LibHanger.Models.modelFields as fld
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.elements import Null

# Baseクラス生成
Base = declarative_base()

class trn_open_info(Base):
	
	# テーブル名
	__tablename__ = 'trn_open_info'
	
	# スキーマ
	__table_args__ = {'schema': 'nkaz'}
	
	# 列定義
	open_id = fld.CharFields(8,primary_key=True,default='')
	racecourse_id = fld.CharFields(2,primary_key=True,default='')
	race_no = fld.NumericFields(2,0,primary_key=True,default=0)
	race_id = fld.CharFields(12,default='')
	win_horse = fld.CharFields(10,default='')
	win_jockey = fld.CharFields(5,default='')
	snd_horse = fld.CharFields(10,default='')
	snd_jockey = fld.CharFields(5,default='')
	trd_horse = fld.CharFields(10,default='')
	trd_jockey = fld.CharFields(5,default='')
	updinfo = fld.CharFields(40,default='')
