import LibHanger.Models.modelFields as fld
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.elements import Null

# Baseクラス生成
Base = declarative_base()

class trn_race_result(Base):
	
	# テーブル名
	__tablename__ = 'trn_race_result'
	
	# スキーマ
	__table_args__ = {'schema': 'nkaz'}
	
	# 列定義
	race_id = fld.CharFields(12,primary_key=True,default='')
	horse_no = fld.NumericFields(2,0,primary_key=True,default=0)
	arrival_order = fld.NumericFields(2,0,default=0)
	incoming_flg = fld.NumericFields(1,0,default=0)
	frame_no = fld.NumericFields(2,0,default=0)
	horse_id = fld.CharFields(10,default=Null)
	horse_nm_en = fld.CharFields(30,default='')
	sex_age = fld.CharFields(10,default='')
	weight = fld.NumericFields(3,0,default=0)
	jockey_id = fld.CharFields(5,default='')
	time = fld.CharFields(10,default='')
	time_second = fld.NumericFields(3,0,default=0)
	arr_diff = fld.CharFields(10,default='')
	barr_diff_num = fld.NumericFields(3,1,default=0)
	tarr_diff_num = fld.NumericFields(3,1,default=0)
	corner1 = fld.NumericFields(1,0,default=Null)
	corner2 = fld.NumericFields(1,0,default=Null)
	corner3 = fld.NumericFields(1,0,default=Null)
	corner4 = fld.NumericFields(1,0,default=Null)
	last3furlong = fld.NumericFields(3,1,default=0)
	win_odds = fld.NumericFields(5,2,default=0)
	popular = fld.NumericFields(2,0,default=0)
	horse_weight = fld.NumericFields(3,0,default=0)
	weight_diff = fld.NumericFields(2,0,default=0)
	trainer_id = fld.CharFields(5,default='')
	howner_id = fld.CharFields(6,default='')
	prize_money = fld.NumericFields(6,1,default=0)
	updinfo = fld.CharFields(40,default='')
