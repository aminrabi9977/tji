# from pydantic import BaseModel
# from typing import List, Optional
# class websiteReport(BaseModel):
#     title: str
#     summary: str
#     content: str
#     hasgtag: str
# ----------------------------------
from pydantic import BaseModel
from typing import List, Optional
from pydantic.config import ConfigDict

class websiteReport(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    title: str
    summary: str
    content: str
    hasgtag: str