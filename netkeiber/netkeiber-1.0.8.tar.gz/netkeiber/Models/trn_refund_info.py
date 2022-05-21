import LibHanger.Models.modelFields as fld
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.elements import Null

# Baseクラス生成
Base = declarative_base()

class trn_refund_info(Base):
	
	# テーブル名
	__tablename__ = 'trn_refund_info'
	
	# スキーマ
	__table_args__ = {'schema': 'nkaz'}
	
	# 列定義
	racecourse_id = fld.CharFields(2,primary_key=True,default='')
	refund_id = fld.CharFields(10,primary_key=True,default='')
	race_no = fld.NumericFields(2,0,primary_key=True,default=0)
	refund_kbn = fld.NumericFields(1,0,primary_key=True,default=0)
	refund_seq = fld.NumericFields(1,0,primary_key=True,default=0)
	horse_no = fld.CharFields(20,default='')
	pay = fld.NumericFields(9,0,default=0)
	pop = fld.NumericFields(4,0,default=0)
	updinfo = fld.CharFields(40,default='')
