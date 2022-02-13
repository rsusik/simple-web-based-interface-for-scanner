# pydentic models
from enum import Enum
from pydantic import BaseModel
from typing import Optional

class ScanModeEnum(str, Enum):
    color = 'color'
    gray = 'gray'
    lineart = 'lineart'

class ScanFormatEnum(str, Enum):
    png = 'png'
    jpeg = 'jpeg'
    pdf = 'pdf'

class ScanRequest(BaseModel):
    mode: ScanModeEnum
    #margin_left: str # l
    #margin_top: str # t
    #width: str # x
    #height: str # y
    resolution: str # dpi
    format: ScanFormatEnum
    filename: Optional[str] = None

class ScanResult(BaseModel):
    code: int
    detail: str
    filename: Optional[str] = None

class ProcessResult(BaseModel):
    returncode: int
    stdout: str
    stderr: str
