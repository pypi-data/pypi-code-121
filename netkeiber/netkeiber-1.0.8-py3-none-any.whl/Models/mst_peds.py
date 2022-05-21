import LibHanger.Models.modelFields as fld
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.elements import Null

# Baseクラス生成
Base = declarative_base()

class mst_peds(Base):
	
	# テーブル名
	__tablename__ = 'mst_peds'
	
	# スキーマ
	__table_args__ = {'schema': 'nkaz'}
	
	# 列定義
	peds_id = fld.CharFields(10,primary_key=True,default='')
	peds_seq = fld.NumericFields(2,0,primary_key=True,default=0)
	gen1_horse_id = fld.CharFields(12,default='')
	gen2_horse_id = fld.CharFields(12,default='')
	gen3_horse_id = fld.CharFields(12,default='')
	gen4_horse_id = fld.CharFields(12,default='')
	gen5_horse_id = fld.CharFields(12,default='')
	updinfo = fld.CharFields(40,default='')
