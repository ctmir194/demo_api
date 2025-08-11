from fastapi import FastAPI, File, UploadFile
import numpy as np
import pydantic
from pydantic import BaseModel


print(dir(pydantic))

app = FastAPI()


class XRay(BaseModel):
    file: File
    

# app.post('/generate')
# def generate(file: UploadFile = File(...)):
