import LibHanger.Models.modelFields as fld
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.elements import Null

# Baseクラス生成
Base = declarative_base()

class mst_horse_sign(Base):
	
	# テーブル名
	__tablename__ = 'mst_horse_sign'
	
	# スキーマ
	__table_args__ = {'schema': 'nkaz'}
	
	# 列定義
	horse_sign_id = fld.CharFields(2,primary_key=True,default='')
	horse_sign_nm = fld.CharFields(20,default='')
	updinfo = fld.CharFields(40,default='')
