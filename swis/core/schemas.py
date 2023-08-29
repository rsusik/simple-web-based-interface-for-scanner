# pydentic models
from enum import Enum
from pydantic import BaseModel
from typing import List, Optional

# class ScanModeEnum(str, Enum):
#     color = 'color'
#     gray = 'gray'
#     lineart = 'lineart'

# class ScanFormatEnum(str, Enum):
#     png = 'png'
#     jpeg = 'jpeg'
#     pdf = 'pdf'

class ScanRequest(BaseModel):
    mode: str
    #margin_left: str # l
    #margin_top: str # t
    #width: str # x
    #height: str # y
    resolution: str # dpi
    format: str
    filename: Optional[str] = None

class MakePdf(BaseModel):
    target: Optional[str] = None
    filenames: List[str] = None


class ScanResult(BaseModel):
    code: int
    detail: str
    filename: Optional[str] = None

class ProcessResult(BaseModel):
    returncode: int
    stdout: str
    stderr: str

class MergeResult(BaseModel):
    returncode: int
    detail: str
    filename: Optional[str] = None

class ScanListItem(BaseModel):
    filename: str
    thumbnail: str

class ScanList(BaseModel):
    returncode: int
    detail: str
    filenames: List[ScanListItem] = None
    