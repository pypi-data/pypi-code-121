from engine.scoringbc import ScoringBCPNP

pa1={
    "noc":'1111',
    "is_working_in_the_position":True,
    "has_one_year_canadian_experience":True,
    "hourly_rate":27,
    "working_hours":40,
    "work_experience":48,
    "region":'Greater Vancouver',
    "education":'Non-trades certification or Diploma',
    "education_bonus":'ECA',
    "clb":6
}

b=ScoringBCPNP(**pa1)
print(pa1)
print(b.total_point)
print(b.noc_level_point,'noc level point')
print(b.noc_00_point,'noc_00 point')
print(b.wage_point,'wage_points')
print(b.work_experience_point,'work_experience_point')
print(b.working_in_the_position_point,'working_in_the_position_point')
print(b.one_year_Canadian_work_experience_point,'one_year_Canadian_work_experience')
print(b.educaiton_level_point,'educaiton_level_points')
print(b.education_bonus_point,'education_bonus_points')
print(b.region_point,'region_points')
print(b.language_level_point,'language_level_points')