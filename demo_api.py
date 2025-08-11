from fastapi import FastAPI, File, UploadFile
import numpy as np
import pydantic
from pydantic import BaseModel, validator

app = FastAPI()

class XRay(BaseModel):
    filename: str
    content: bytes

    @validator('filename')
    def filename_validator(cls, value):
        if not value.lower().endswith('.dcm'):
            raise ValueError("File extension should be '.dcm'")
        return value
    
    @validator('content')
    def content_validator(cls, value):
        if len(value) < 132 or value[128:132] != b"DICM":            ## he b prefix means this is a bytes literal, not a string. ## first 128 bytes are "preamble"                                                    (can be anything or zero-filled) + 4 for DICM so length shold be atleast 132
            raise ValueError("File does not appear to a DICOM file")
        return value
    

app.post('/generate')
def generate(file: UploadFile = File(...)):
    
