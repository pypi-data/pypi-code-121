import LibHanger.Models.modelFields as fld
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.elements import Null

# Baseクラス生成
Base = declarative_base()

class trn_horse_result(Base):
	
	# テーブル名
	__tablename__ = 'trn_horse_result'
	
	# スキーマ
	__table_args__ = {'schema': 'nkaz'}
	
	# 列定義
	horse_id = fld.CharFields(10,primary_key=True,default='')
	race_id = fld.CharFields(12,primary_key=True,default='')
	horse_no = fld.NumericFields(2,0,primary_key=True,default=0)
	racecourse_id = fld.CharFields(2,default='')
	open_id = fld.CharFields(8,default='')
	open_nm = fld.CharFields(16,default='')
	pace_firsth = fld.NumericFields(3,1,default=0)
	pace_latterh = fld.NumericFields(3,1,default=0)
	win_horse_id = fld.CharFields(12,default='')
	updinfo = fld.CharFields(40,default='')
