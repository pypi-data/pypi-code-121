import LibHanger.Models.modelFields as fld
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.elements import Null

# Baseクラス生成
Base = declarative_base()

class mst_racecourse(Base):
	
	# テーブル名
	__tablename__ = 'mst_racecourse'
	
	# スキーマ
	__table_args__ = {'schema': 'nkaz'}
	
	# 列定義
	racecourse_id = fld.CharFields(2,primary_key=True,default='')
	racecourse_nm = fld.CharFields(20,default='')
	updinfo = fld.CharFields(40,default='')
