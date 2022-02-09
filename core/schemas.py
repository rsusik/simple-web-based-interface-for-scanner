# pydentic models
from enum import Enum
from pydantic import BaseModel
from typing import Optional

class ModeEnum(str, Enum):
    color = 'color'
    gray = 'gray'
    lineart = 'lineart'

class FormatEnum(str, Enum):
    png = 'png'
    jpeg = 'jpeg'
    pdf = 'pdf'


class ScanRequest(BaseModel):
    mode: ModeEnum
    #margin_left: str # l
    #margin_top: str # t
    #width: str # x
    #height: str # y
    resolution: str # dpi
    format: FormatEnum # png, jpeg, pdf
    filename: Optional[str] = None

class ScanResult(BaseModel):
    code: int
    detail: str
    filename: Optional[str] = None
