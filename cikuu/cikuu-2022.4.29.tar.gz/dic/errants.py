# 2020-9-10 #https://github.com/chrisjbryant/errant
import errant, spacy		
errant.annotator = errant.load('en', nlp=spacy.load('en_core_web_sm'))

errant_filter = {"R:SPELL":"t.tag_ not in ('NNP','NNPS')"} #R:SPELL=NNP -> t.tag_ not in ('NNP','NNPS') |   A and B , in one unit
errant_type = {
"M:DET":"{ 'error': '冠词缺失', 'explanation':f'建议添加冠词<b>{edit.c_str}</b>'}",
"R:ADV":"{ 'error': '副词误用', 'explanation':f'建议<b>{edit.o_str}</b>修改为<b>{edit.c_str}</b>'}",
"M:NOUN:POSS":"{ 'error': '名词所有格缺失', 'explanation':f'建议添加名词所有格<b>{edit.c_str}</b>'}",
"M:PREP":"{ 'error': '介词缺失', 'explanation':f'建议添加介词<b>{edit.c_str}</b>'}",
"R:PRON":"{ 'error': '代词误用', 'explanation':f'建议<b>{edit.o_str}</b>修改为<b>{edit.c_str}</b>'}",
"UNK":"{ 'error': '未知错误', 'explanation':f'检测到但未修正错误'}",
"R:VERB:SVA":"{ 'error': '主谓不一致', 'explanation':f'请检查动词<b>{edit.o_str}</b>形态'}",
"R:ADJ":"{ 'error': '形容词误用', 'explanation':f'建议<b>{edit.o_str}</b>修改为<b>{edit.c_str}</b>'}",
"M:CONTR":"{ 'error': '缩略形式缺失', 'explanation':f'建议添加缩略形式<b>{edit.c_str}</b>'}",
"R:ADJ:FORM":"{ 'error': '形容词形式错误', 'explanation':f'建议<b>{edit.o_str}</b>修改为<b>{edit.c_str}</b>'}",
"M:VERB:TENSE":"{ 'error': '动词时态缺失', 'explanation':f'建议添加动词时态<b>{edit.c_str}</b>'}",
"R:DET":"{ 'error': '冠词误用', 'explanation':f'建议<b>{edit.o_str}</b>修改为<b>{edit.c_str}</b>'}",
"U:VERB:TENSE":"{ 'error': '动词时态多余', 'explanation':f'动词时态<b>{edit.o_str}</b>疑似多余'}",
"R:NOUN":"{ 'error': '名词误用', 'explanation':f'建议<b>{edit.o_str}</b>修改为<b>{edit.c_str}</b>'}",
"R:NOUN:POSS":"{ 'error': '名词所有格误用', 'explanation':f'建议<b>{edit.o_str}</b>修改为<b>{edit.c_str}</b>'}",
"R:VERB:TENSE":"{ 'error': '动词时态误用', 'explanation':f'建议<b>{edit.o_str}</b>修改为<b>{edit.c_str}</b>'}",
"U:VERB:FORM":"{ 'error': '动词形式多余', 'explanation':f'动词形式<b>{edit.o_str}</b>疑似多余'}",
"U:PUNCT":"{ 'error': '标点符号多余', 'explanation':f'标点符号<b>{edit.o_str}</b>疑似多余'}",
"U:NOUN":"{ 'error': '名词多余', 'explanation':f'名词<b>{edit.o_str}</b>疑似多余'}",
"R:ORTH":"{ 'error': '大小写/或空格错误', 'explanation':f'建议<b>{edit.o_str}</b>修改为<b>{edit.c_str}</b>'}",
"R:NOUN:INFL":"{ 'error': '名词词形变化错误', 'explanation':f'建议<b>{edit.o_str}</b>修改为<b>{edit.c_str}</b>'}",
"R:NOUN:NUM":"{ 'error': '名词单复数错误', 'explanation':f'建议<b>{edit.o_str}</b>修改为<b>{edit.c_str}</b>'}",
"M:CONJ":"{ 'error': '连词缺失', 'explanation':f'建议添加连词<b>{edit.c_str}</b>'}",
"R:VERB":"{ 'error': '动词误用', 'explanation':f'建议<b>{edit.o_str}</b>修改为<b>{edit.c_str}</b>'}",
"M:PRON":"{ 'error': '代词缺失', 'explanation':f'建议添加代词<b>{edit.c_str}</b>'}",
"M:NOUN":"{ 'error': '名词缺失', 'explanation':f'建议添加名词<b>{edit.c_str}</b>'}",
"M:ADV":"{ 'error': '副词缺失', 'explanation':f'建议添加副词<b>{edit.c_str}</b>'}",
"U:CONJ":"{ 'error': '连词多余', 'explanation':f'连词<b>{edit.o_str}</b>疑似多余'}",
"R:PUNCT":"{ 'error': '标点符号误用', 'explanation':f'建议<b>{edit.o_str}</b>修改为<b>{edit.c_str}</b>'}",
"U:ADV":"{ 'error': '副词多余', 'explanation':f'副词<b>{edit.o_str}</b>疑似多余'}",
"R:CONTR":"{ 'error': '缩略形式错误', 'explanation':f'建议<b>{edit.o_str}</b>修改为<b>{edit.c_str}</b>'}",
"U:PREP":"{ 'error': '介词多余', 'explanation':f'介词<b>{edit.o_str}</b>疑似多余'}",
"U:DET":"{ 'error': '冠词多余', 'explanation':f'冠词<b>{edit.o_str}</b>疑似多余'}",
"M:VERB:FORM":"{ 'error': '动词形式缺失', 'explanation':f'建议添加动词形式<b>{edit.c_str}</b>'}",
"M:ADJ":"{ 'error': '形容词缺失', 'explanation':f'建议添加形容词<b>{edit.c_str}</b>'}",
"M:VERB":"{ 'error': '动词缺失', 'explanation':f'建议添加动词<b>{edit.c_str}</b>'}",
"U:CONTR":"{ 'error': '缩略形式多余', 'explanation':f'缩略形式<b>{edit.o_str}</b>疑似多余'}",
"U:VERB":"{ 'error': '动词多余', 'explanation':f'动词<b>{edit.o_str}</b>疑似多余'}",
"U:PART":"{ 'error': '与动词构成短语动词的副词或介词多余', 'explanation':f'与动词构成短语动词的副词或介词<b>{edit.o_str}</b>疑似多余'}",
"R:OTHER":"{ 'error': '单词误用', 'explanation':f'建议修改为<b>{edit.c_str}</b>'}",
"U:NOUN:POSS":"{ 'error': '名词所有格多余', 'explanation':f'名词所有格<b>{edit.o_str}</b>疑似多余'}",
"R:WO":"{ 'error': '语序错误', 'explanation':f'建议<b>{edit.o_str}</b>修改为<b>{edit.c_str}</b>'}",
"R:PREP":"{ 'error': '介词误用', 'explanation':f'建议<b>{edit.o_str}</b>修改为<b>{edit.c_str}</b>'}",
"R:VERB:INFL":"{ 'error': '动词词形变化错误', 'explanation':f'建议<b>{edit.o_str}</b>修改为<b>{edit.c_str}</b>'}",
"U:PRON":"{ 'error': '代词多余', 'explanation':f'代词<b>{edit.o_str}</b>疑似多余'}",
"R:CONJ":"{ 'error': '连词误用', 'explanation':f'建议<b>{edit.o_str}</b>修改为<b>{edit.c_str}</b>'}",
"R:SPELL":"{ 'error': '拼写错误', 'explanation':f'请检查<b>{edit.o_str}</b>拼写'}",
"R:PART":"{ 'error': '与动词构成短语动词的副词或介词误用', 'explanation':f'建议<b>{edit.o_str}</b>修改为<b>{edit.c_str}</b>'}",
"U:SPACE":"{ 'error': '空格多余', 'explanation':f'建议删除空格'}",
"U:OTHER":"{ 'error': '单词冗余', 'explanation':f'建议删除<b>{edit.o_str} </b>'}",
"R:MORPH":"{ 'error': '词性误用', 'explanation':f'建议<b>{edit.o_str}</b>修改为<b>{edit.c_str}</b>'}",
"R:VERB:FORM":"{ 'error': '动词形式误用', 'explanation':f'建议<b>{edit.o_str}</b>修改为<b>{edit.c_str}</b>'}",
"M:OTHER":"{ 'error': '单词缺失', 'explanation':f'建议添加<b>{edit.c_str}</b>'}",
"U:ADJ":"{ 'error': '形容词多余', 'explanation':f'形容词<b>{edit.o_str}</b>疑似多余'}",
"M:PART":"{ 'error': '与动词构成短语动词的副词或介词缺失', 'explanation':f'建议添加与动词构成短语动词的副词或介词<b>{edit.c_str}</b>'}",
"M:PUNCT":"{ 'error': '标点符号缺失', 'explanation':f'建议添加标点符号<b>{edit.c_str}</b>'}",
}

def feed_errant(r): 
	errant_filter.update( r.hgetall('errant:filter'))
	errant_type.update( r.hgetall('errant:type'))

def reload_errant(r):
	[errant_type.update({k:v}) for k,v in r.hgetall('errant:type').items()]
	for k,code in r.hgetall("errant:filter").items(): #R:SPELL -> t.tag_ not in ('NNP','NNPS')
		errant_filter.update({k:code})
	return r.hlen('errant:type')

def from_edit(doc, edit):
	op = 's' if edit.type.startswith("R:") else 'i' if edit.type.startswith("M:") else 'd' if edit.type.startswith("U:") else 'x' #missed, unnecessay
	hit =  {'op': op, 'position': doc[edit.o_start].idx, 'ibeg':edit.o_start,'text':edit.o_str, 'replaceText':edit.c_str, 'cate': edit.type, 'error': edit.type, 'explanation':f'Please check <b>{edit.o_str}</b>', 'type':'grammar'}
	try:
		cate_msg = errant_type.get(edit.type,'{}')  # cached_hget('__errant:type', edit.type) 
		hit.update( eval( cate_msg, {'doc':doc, 'hit':hit, 'edit':edit})   )
	except Exception as e:
		print("from_edit ex:", e, hit)
	return hit

def pass_filter(doc, edit): # R:SPELL=NNP -> t.tag_ not in ('NNP','NNPS')
	try:
		code =  errant_filter.get(edit.type, "True" ) 
		return eval ( code, {'doc': doc, 't': doc[edit.o_start]} )
	except Exception as e:
		print("pass_filter ex:", e, edit)
	return False # ?

snt_errants =  lambda doc, edits : [ from_edit(doc, edit) for edit in edits if edit.o_start >= 0 and pass_filter(doc, edit)] 

def init_redis():
	import redis,json
	r = redis.Redis(host='dev.werror.com',port=4328, decode_responses=True)
	r.delete('errant:filter')
	r.delete('errant:type')
	r.hmset('errant:filter', errant_filter)
	r.hmset('errant:type', errant_type)

if __name__ == '__main__':
	pass
	#init_redis()