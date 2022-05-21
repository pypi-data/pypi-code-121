import LibHanger.Models.modelFields as fld
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.elements import Null

# Baseクラス生成
Base = declarative_base()

class trn_race_id(Base):
	
	# テーブル名
	__tablename__ = 'trn_race_id'
	
	# スキーマ
	__table_args__ = {'schema': 'nkaz'}
	
	# 列定義
	race_id = fld.CharFields(12,primary_key=True,default='')
	racecourse_id = fld.CharFields(2,primary_key=True,default='')
	open_id = fld.CharFields(8,primary_key=True,default='')
	scraping_count = fld.NumericFields(3,0,default=0)
	get_time = fld.NumericFields(4,0,default=0)
	get_status = fld.NumericFields(1,0,default=0)
	updinfo = fld.CharFields(40,default='')
