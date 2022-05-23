'''
These set of classes are intended to format a particular type of data in a human-readable form
by supporting string.format()
'''

import datetime

class StatValue(object):

    def __init__(self, value):
        self.value = value
    
class ByteSizeValue(StatValue):
    
    def __init__(self, value):
        '''        
        :param value: The value in Bytes
        :type value: number
        '''
        
        super(ByteSizeValue, self).__init__(value=value)    
    
    
    def __format__(self, format_spec):

        # KB is the smallest size we want to display
        file_size = float(self.value)/(1024.0*1024.0)

        for unit in ["K", "M", "G", "T", "P", "E", "Z"]:
            if abs(file_size) < 1024.0:
                return "{:3.1f} {}Bytes".format(file_size, unit)
            file_size/= 1024.0
        
        # YottaByte follows ZettaByte
        return "{:.1f}YBytes".format(file_size)
    

class FileProgressValue(StatValue):
        
    def __format__(self,  format_spec):

        file_progress_text = []

        for filename, progress_fields in self.value.items():

            file_progress_text.append("{}: {} Bytes/{} Bytes".format(filename, 
                                                         progress_fields['bytes_uploaded'], 
                                                         progress_fields['bytes_to_upload']))
            
        return "\n".join(file_progress_text)
    
class PercentageValue(StatValue):
    
    def __format__(self, format_spec):
                
        if self.value is None:
            return "N/A"
            
        else:
            return "{:.0%}".format(self.value)
        
class TimeRemainingValue(StatValue):
    
    def __init__(self, value):

        if value is not None:
            value = datetime.timedelta(seconds=value)
            
        super(TimeRemainingValue, self).__init__(value)        
    
    def __format__(self, format_spec):
                
        if self.value is None:
            return "N/A"
            
        else:
            return "{}".format(self.value)  