import time
import uuid


class Session(dict):
    def __init__(self, *args, **kwargs):
        """
        @param kwargs['expiration_time'] a time in seconds from Epoch. 
                If negative the session never expires (default).
        """
        if 'expiration_time' in kwargs:
            self._expiration_time = kwargs['expiration_time']
            del kwargs['expiration_time']
        else:
            self._expiration_time = -1
        
        self._id = str(uuid.uuid4())
        
        super(self.__class__, self).__init__(*args, **kwargs)
    
    def get_id(self):
        return self._id
    
    def get_expiration_time(self):
        return self._expiration_time
    
    def set_expiration_time(self, expiration_time):
        self._expiration_time = expiration_time
    
    def touch(self, seconds):
        assert not self.is_expired()
        
        if self._expiration_time < 0:
            return
        self.set_expiration_time(time.time() + seconds)
    
    def is_expired(self):
        return self._expiration_time >= 0 and time.time() >= self._expiration_time
    
    def expire(self):
        self._expiration_time = 0
