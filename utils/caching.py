import yaml
from os.path import exists
from typing import Optional, Union
from datetime import datetime, date

class Cache:
    def __init__(self, cache_file_name: Optional[str] = ".cache"):
        self._today = date.today()
        self.cache_file_name = cache_file_name
        self.get_current_cache()

    def verify_quota(self):
        cache = self.get_current_cache()
        self.LAST_UPDATED = datetime.strptime(cache['LAST_UPDATED'], "%d-%m-%y")
        self.QUOTA = float(cache['QUOTA_MIN_USED'])

        # Update LAST_UPDATED cache and reset quota limits if month changes 
        if self._today.month > self.LAST_UPDATED.month:
            self.reset_cache()

        elif self._today.month == self.LAST_UPDATED.month:
            if self.QUOTA >= 50*60:
                err_msg = """ERROR - QUATA ALREADY EXCEEDED. Here is what u could do:
                1. Try using a different account and manually reset the quota limit.
                2. Wait until next month and try again."""
                raise Exception(err_msg)

        else:
            raise ValueError("Last update month greater then this month.")
    
    def reset_cache(self):        
        _dic = {
                "LAST_UPDATED": self._today.strftime("%d-%m-%y"),
                "QUOTA_MIN_USED": 0
            }
        with open(self.cache_file_name, 'w') as outfile:
            yaml.dump(data=_dic, stream=outfile, default_flow_style=False)
    
    def get_current_cache(self):
        if not exists(self.cache_file_name):
            self.reset_cache()
            
        # Open Cache
        with open(self.cache_file_name, 'r') as stream:
            cache = yaml.safe_load(stream)
        
        self.LAST_UPDATED = datetime.strptime(cache['LAST_UPDATED'], "%d-%m-%y")
        self.QUOTA = float(cache['QUOTA_MIN_USED'])
        return cache
    
    def update_cache(self, add_to_quota: Union[int, float]):
        _dic = {
                "LAST_UPDATED": self._today.strftime("%d-%m-%y"),
                "QUOTA_MIN_USED": self.QUOTA + add_to_quota
            }
        with open(self.cache_file_name, 'w') as outfile:
            yaml.dump(data=_dic, stream=outfile, default_flow_style=False)


