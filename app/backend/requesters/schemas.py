import hashlib
from pydantic import BaseModel, ConfigDict, computed_field


class RequesterSchema(BaseModel):
    id: int
    username: str
    
    model_config = ConfigDict(from_attributes=True)
    

class RequesterCreate(BaseModel):
    username: str
    fp: str 
    
    @computed_field
    @property
    def fp_hash(self) -> str:
        return hashlib.sha256(self.fp.encode()).hexdigest()
