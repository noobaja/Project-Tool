from pydantic import BaseModel
from typing import List

class TaskIdList(BaseModel):
    task_ids: List[str]