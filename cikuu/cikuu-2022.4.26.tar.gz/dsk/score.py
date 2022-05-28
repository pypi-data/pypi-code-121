# 2022.3.20 dims-to-score
from collections import Counter 

def five_score(v, five_v, five_scores=[0.0,60.0,80.0,90.0,100.0], f = lambda v, v1,v2,s1,s2: s1 + (s2-s1) * (v-v1)/(v2-v1)): 
	if v < five_v[0] : return five_scores[0]
	elif v >= five_v[0] and v < five_v[1] : return f(v, five_v[0], five_v[1], five_scores[0], five_scores[1])
	elif v >= five_v[1] and v < five_v[2] : return f(v, five_v[1], five_v[2], five_scores[1], five_scores[2])
	elif v >= five_v[2] and v < five_v[3] : return f(v, five_v[2], five_v[3], five_scores[2], five_scores[3])
	elif v >= five_v[3] and v < five_v[4] : return f(v, five_v[3], five_v[4], five_scores[3], five_scores[4])
	elif v >= five_v[4] : return five_scores[4]

def dims_score(dims:dict={"doc_tc": 191.0, "asl": 74.6154, "ttr2": 62.2009, "ttr": 57.0651, "ast": 14.6923, "snt_num": 13.0, "cl_sum": 8.0, "pred_diff_max3": 5.9, "ttr1": 5.5769, "word_diff_avg": 4.7957, "awl": 4.2723, "prmods_tc": 4.2308, "e_snt.fitted": 3.0, "ast_sd": 1.3431, "mwe_pv": 1.0769, "spell_correct_ratio": 1.0, "kp_correct_ratio": 0.8849, "internal_sim": 0.8794574205761223, "mwe_disconj": 0.8462, "simple_sent_ri": 0.7647, "cl_ratio": 0.6162, "snt_correct_ratio": 0.3077, "simple_sent_ratio": 0.3077, "grammar_correct_ri": 0.3077, "prmods_ratio": 0.2763, "word_gt7": 0.2669, "n_ratio": 0.2407, "v_ratio": 0.1884, "jj_ratio": 0.1099, "art_ratio": 0.0523, "comma_ratio": 0.0471, "b3_b1": 0.0411, "rb_ratio": 0.0366, "b3": 0.0262, "cc_ratio": 0.0157, "kp_correct_ri": 0.0}, 
	formula:dict= {   # five-range-value, cate, coef, cate-coef
"ast":[9.9, 11.99, 15.3, 18.51, 25.32,				2,0.0882, 0.3241],
"awl":[3.5, 4.1, 4.56, 5.1, 6.0,					3,0.0882, 0.5],
"b3":[0, 0.03, 0.08, 0.12, 0.15 ,					1, 0.0956, 0.2096],
"cl_sum":[1, 6.68, 12, 16, 26,						2,0.0441, 0.1621],
"grammar_correct_ri":[0.6, 0.85, 0.92, 0.97,1.0,	2,0.0368, 0.1352],
"internal_sim":[0.0, 0.08, 0.2, 0.3, 0.4,			4, 0.0735, 0.7688],
"kp_correct_ri":[0.7, 0.9, 0.95, 0.97, 1,			1, 0.0368, 0.0807],
"mwe_pv":[0.01,8.03, 12, 20.21, 25,					4, 0.0221, 0.2312],
"pred_diff_max3":[3.84, 5.11, 6.51, 7.9, 10.09 ,	1, 0.0368, 0.0807],
"prmods_ratio":[0.06, 0.21, 0.3, 0.4, 0.5,			2, 0.0294, 0.108],
"prmods_tc":[1.1, 2.76, 4.75, 6.76, 10.0,			2, 0.0368, 0.1352],
"simple_sent_ri":[0.4, 0.65, 0.9, 0.95, 1,			2, 0.0368, 0.1352],
"snt_correct_ratio":[0.01, 0.2, 0.45, 0.75, 1,		1, 0.0368, 0.0807],
"spell_correct_ratio":[0.8, 0.9, 0.97, 0.99, 1,		1, 0.1471, 0.3226],
"ttr1":[3.43, 4.28, 5.2, 6, 6.8,					3, 0.0882, 0.5],
"word_diff_avg":[4.47, 4.73, 5.25,5.8, 6.6,			1, 0.0441, 0.0967],
"word_gt7":[0.11, 0.19, 0.3, 0.42, 0.49,			1, 0.0588, 0.1289]}, 
	qiwang:list=[0.0,60.0,80.0,90.0,100.0]):
	''' five-range-value, cate, coef, cate-coef '''
	dim_scores = {}
	for name, vf in formula.items():
		if name in dims:
			dim_scores[name] = { 'score': five_score( dims[name], vf, qiwang), 'value': dims[name], 'range':vf[0:5], 'cate': vf[5] , 'coef': vf[6], 'cate-coef': vf[7]}
	score = sum([ v['score'] * v['coef'] for name, v in dim_scores.items()])
	ratio = sum([ v['coef'] for name, v in dim_scores.items()])
	
	return {"formula_score": score/ratio, 
	'cate_score': ( si:=Counter(), [ si.update( {ar['cate'] : ar['score'] * ar['cate-coef']})  for ar in dim_scores.values()] )[0] } #'cate_score_default'

if __name__ == '__main__':
	res = dims_score()
	print (res)