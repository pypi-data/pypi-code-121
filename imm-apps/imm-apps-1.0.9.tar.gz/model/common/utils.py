"""
This is a tool set for pydantic validation shared by all models
"""
from datetime import date
from dateutil.parser import parse,ParserError

def normalize(name: str):
    if name:
        return ' '.join((word.capitalize()) for word in name.split(' '))
    return ''

def makeList(name:str):
    if name:
        return name.split('\n')
    return []

def trimString(text:str):
    return "" if text==None else text.strip()

class Duration():
    def __init__(self,start_date,end_date):
        try:
            self.start_date=start_date if isinstance(start_date,date) else parse(start_date)
            self.end_date=end_date if isinstance(end_date,date) else parse(end_date)
        except ParserError as err:
            raise ParserError(f'{err.args[0]}," in file ",{__file__}')
        
    @property
    def years(self):
        return self.end_date.year - self.start_date.year - ((self.end_date.month, self.end_date.day) < (self.start_date.month, self.start_date.day))
    
    @property
    def months(self):
        years2months=(self.end_date.year - self.start_date.year)*12
        months2months=self.end_date.month-self.start_date.month
        return years2months+months2months
    
    # get years on a specific date
    def yearsOnDate(self,end_date= date.today()):
        if not isinstance(end_date,date):
            try:
                end_date=parse(end_date)
                return end_date.year - self.start_date.year - ((end_date.month, end_date.day) < (self.start_date.month, self.start_date.day))
            except ParserError as err:
                raise ParserError(f'{err.args[0]}," in file ",{__file__}')
        return end_date.year - self.start_date.year - ((end_date.month, end_date.day) < (self.start_date.month, self.start_date.day))
    
    # get months on a specific date
    def monthsOnDate(self,end_date= date.today()):
        try:
            end_date=end_date if isinstance(end_date,date) else parse(end_date)
        except ParserError as err:
                raise ParserError(f'{err.args[0]}," in file ",{__file__}')
        
        years2months=(end_date.year - self.start_date.year)*12
        months2months=end_date.month-self.start_date.month
        return years2months+months2months
    
    #get days 
    @property
    def days(self):
        return (self.end_date-self.start_date).days
    
    def daysOnDate(self,end_date=date.today()):
        if not isinstance(end_date,date):
            try:
                end_date=parse(end_date).date()
                return (end_date- self.start_date).days
            except ParserError as err:
                raise ParserError(f'{err.args[0]}," in file ",{__file__}')
        return (end_date- self.start_date).days

def main():
    d=Duration('2020-01-01','2022-01-02')
    print(d.days)

if __name__=="__main__":
    main()
    
    
