from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse, Response, StreamingResponse
import numpy as np
import pydantic
from pydantic import BaseModel, validator
import pydicom
import io
from io import BytesIO

app = FastAPI()

def transformations(file):
    dcm_file = file

    ## increasing brightness
    dcm_file.PixelData = (dcm_file.pixel_array + 30).tobytes()

    return dcm_file
    
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
        if len(value) < 132 or value[128:132] != b"DICM":            ## here b prefix means this is a bytes literal, not a string. ## first 128 bytes are "preamble"                                                    (can be anything or zero-filled) + 4 for DICM so length shold be atleast 132
            raise ValueError("File does not appear to a DICOM file")
        return value
    
@app.post('/generate')
def generate(file: UploadFile = File(...)):

    file_byte = file.file.read()
    verified_file  = XRay(**{'filename':file.filename, 
            'content':file_byte})

    dcm_file = pydicom.dcmread(BytesIO(verified_file.content))
    ## applying preprocessing/transformations
    transformed_dcm_file = transformations(dcm_file)
    
    output_buffer = BytesIO()
    transformed_dcm_file.save_as(output_buffer)
    output_buffer.seek(0)  # reset pointer for streaming

    # Return as downloadable DICOM file
    return StreamingResponse(
        output_buffer,
        media_type="application/dicom",
        headers={
            "Content-Disposition": f'attachment; filename="edited_{file.filename}"'
        }
    )

    # return Response(status_code=200, content=io.BytesIO(transformed_dcm_file))