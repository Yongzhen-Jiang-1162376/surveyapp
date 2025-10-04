from enum import Enum


class Role(Enum):
    SITEADMIN = "siteadmin"
    
    def __str__(self):
        return self.value

class Status(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    
    def __str__(self):
        return self.value
