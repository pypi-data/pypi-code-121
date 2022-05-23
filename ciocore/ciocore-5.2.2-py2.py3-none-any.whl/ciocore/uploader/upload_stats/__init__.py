import datetime

from .stats_formats import ByteSizeValue, FileProgressValue, PercentageValue, TimeRemainingValue

class UploadStats(object):
    '''
    Data structure for storing state progress of the uploader
    '''
    
    TEMPLATE = """
################################################################################
     files to process: {self.files_to_analyze}
      files to upload: {self.files_to_upload}
       data to upload: {self.bytes_to_upload}
             uploaded: {self.bytes_uploaded}
         elapsed time: {self.elapsed_time}
     percent complete: {self.percent_complete}
        transfer rate: {self.transfer_rate}/s
       time remaining: {self.time_remaining}
        file progress: {self.file_progress}
################################################################################        
"""
    
    def __init__(self):
        
        self.files_to_analyze = None
        self.files_to_upload = None
        self.bytes_to_upload = None
        self.bytes_uploaded = None
        self.elapsed_time = None
        self.percent_complete = None
        self.transfer_rate = None
        self.time_remaining = None
        self.file_progress = {}
        
    def get_formatted_text(self):
        return self.TEMPLATE.format(self=self)
        
    @classmethod
    def create(cls, metric_store, num_files_to_process, job_start_time):
        '''
        Factory for creating an UploadStats objects from a metric_store
        '''
        
        new_obj = cls()
        new_obj.files_to_analyze = num_files_to_process
        new_obj.files_to_upload = cls.get_files_to_upload(metric_store)
        new_obj.bytes_to_upload = ByteSizeValue(cls.get_bytes_to_upload(metric_store)*1024.0)
        new_obj.bytes_uploaded = ByteSizeValue(cls.get_bytes_uploaded(metric_store)*1024.0)
        new_obj.elapsed_time = cls.get_elapsed_time(job_start_time)
        new_obj.percent_complete = PercentageValue(cls.get_percent_complete(metric_store))
        new_obj.transfer_rate = ByteSizeValue(cls.get_transfer_rate(metric_store, job_start_time)*1024.0)            
        new_obj.time_remaining = TimeRemainingValue(cls.get_estimated_time_remaining(metric_store, job_start_time))
        
        # Merge the MD5 and files dicts
        files_dict = metric_store.get_dict("files")
        md5_dict = metric_store.get_dict("file_md5s")
        md5_cache_dict = metric_store.get_dict("file_md5s_cache_hit")
        combined_dict = {}
        
        for k in list(files_dict.keys()) + list(md5_dict.keys()):
            combined_dict[k] = files_dict.get(k, {'bytes_uploaded':0, 'bytes_to_upload':0})
            combined_dict[k]['md5'] = md5_dict.get(k)
            combined_dict[k]['md5_was_cached'] = md5_cache_dict.get(k)
        
        new_obj.file_progress = FileProgressValue(combined_dict)

        return new_obj        
        
    @classmethod
    def get_files_to_upload(cls, metric_store):
        
        num_files_to_upload = metric_store.get("num_files_to_upload")
        return num_files_to_upload
    
    @classmethod
    def get_bytes_to_upload(cls, metric_store):
        
        bytes_to_upload = metric_store.get("bytes_to_upload")
        return bytes_to_upload
    
    @classmethod    
    def get_bytes_uploaded(cls, metric_store):
        
        bytes_uploaded = metric_store.get("bytes_uploaded")
        return bytes_uploaded
    
    @classmethod
    def get_percent_complete(cls, metric_store):
        
        bytes_to_upload = cls.get_bytes_to_upload(metric_store)
        bytes_uploaded = cls.get_bytes_uploaded(metric_store)

        if bytes_to_upload:
            percent_complete = float(bytes_uploaded) / float(bytes_to_upload)
            
        elif float(bytes_to_upload) == float(0):
            percent_complete = None
        
        else:
            percent_complete = 0.0
            
        return percent_complete
    
    @classmethod
    def get_elapsed_time(cls, job_start_time):

        if job_start_time:
            elapsed_time = datetime.datetime.now() - job_start_time
        
        else:
            elapsed_time = datetime.timedelta(seconds=0)
            
        return elapsed_time
    
    @classmethod
    def get_transfer_rate(cls, metric_store, job_start_time):
        
        elapsed_time = cls.get_elapsed_time(job_start_time).seconds

        if elapsed_time:
            transfer_rate = cls.get_bytes_uploaded(metric_store) / elapsed_time
        else:
            transfer_rate = 0        
            
        return transfer_rate
    
    @classmethod
    def get_estimated_time_remaining(cls, metric_store, job_start_time):
        """
        This method estimates the time that is remaining, given the elapsed time and percent
        complete.

        It uses the following formula:

        let; t0 = elapsed time P = percent complete (0 <= n <= 1)

        time_remaining = (t0 - t0 * P) / P

        which is derived from percent_complete = elapsed_time / (elapsed_time + time_remaining)
        """
        
        elapsed_time = cls.get_elapsed_time(job_start_time).seconds
        percent_complete = cls.get_percent_complete(metric_store)
        
        if percent_complete is None:
            return None
        
        if float(percent_complete) == 0.0:
            return 0.0

        estimated_time = (elapsed_time - elapsed_time * percent_complete) / percent_complete
        return estimated_time