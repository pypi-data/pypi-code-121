from pydantic import BaseModel
from engine.scoring import getKeyValuePoint,getRangePoint,getNOCLevel
from policy.bcpnp import data
from dataclasses import dataclass

class ScoringBCPNP(BaseModel):
    noc:str='1111'
    is_working_in_the_position:bool=False
    has_one_year_canadian_experience:bool=False
    hourly_rate:float=25
    working_hours:float=40
    work_experience:int=24
    region:str='Greater Vancouver'
    education:str='Bachelor'
    education_bonus:str='ECA'
    clb:int=4

    @property
    def skill_level(self):
        return getNOCLevel(self.noc)
    
    @property
    def noc_level_point(self):
        return getKeyValuePoint(data.skill_level_points,self.skill_level)
    
    @property
    def noc_00_point(self):
        return getKeyValuePoint(data.skill_level_bonus_points,self.skill_level)
    
    @property
    def wage_point(self):
        return getRangePoint(data.wage_points,int(self.hourly_rate*self.working_hours*52))
    
    @property
    def work_experience_point(self):
        return getRangePoint(data.work_experience_points,self.work_experience)
    
    @property
    def working_in_the_position_point(self):
        return getKeyValuePoint(data.working_in_the_position_points,self.is_working_in_the_position)
    
    @property
    def one_year_Canadian_work_experience_point(self):
        return getKeyValuePoint(data.one_year_experience_point,self.has_one_year_canadian_experience)
    
    @property
    def educaiton_level_point(self):
        return getKeyValuePoint(data.education_points,self.education)
    
    @property
    def education_bonus_point(self):
        return getKeyValuePoint(data.education_bonus_points,self.education_bonus)
    
    @property
    def region_point(self):
        return getKeyValuePoint(data.region_points,self.region)
    
    @property
    def language_level_point(self):
        return getKeyValuePoint(data.language_points,self.clb)
    
    @property
    def total_point(self):
        return (self.noc_level_point+self.noc_00_point+self.wage_point+self.work_experience_point+
                self.working_in_the_position_point+self.one_year_Canadian_work_experience_point+
                self.educaiton_level_point+self.education_bonus_point+self.region_point+self.language_level_point)