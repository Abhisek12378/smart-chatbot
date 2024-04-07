import time
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Union
import os
from handle_file import FileProcessor
from datetime import datetime
import traceback
from fastapi import BackgroundTasks

load_dotenv()

class Response(BaseModel):
    result: Union[str, None]


origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",
    os.getenv("FRONTEND_APP_URL")
]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the directory to save uploaded files
UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)
@app.on_event("startup")
async def startup_event():
    BackgroundTasks().add_task(cleanup_files)

@app.post("/predict", response_model=Response)
async def predict(background_tasks: BackgroundTasks,file: UploadFile = File(...), question: str = Form(...), timestamp: str = Form(...)) -> Response:
    try:
        timestamp_dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
        formatted_str = timestamp_dt.strftime("%Y%m%d_%H%M%S")
        file_name = list(os.path.splitext(file.filename))[0] + "_" + formatted_str + list(os.path.splitext(file.filename))[1]
        file_location = os.path.join(UPLOAD_DIR, file_name)
        if not (os.path.exists(file_location)):
            with open(file_location, "wb") as file_object:
                file_object.write(file.file.read())
        else:
            pass
        file_process_obj = FileProcessor()
        query_result = str(file_process_obj.process_file(file_location, question))
        background_tasks.add_task(cleanup_files)
        return {"result": query_result}

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

    return {"result": query_result}


def cleanup_files():
    current_time = time.time()
    for filename in os.listdir(UPLOAD_DIR):
        file_path = os.path.join(UPLOAD_DIR, filename)
        file_mod_time = os.path.getmtime(file_path)
        if current_time - file_mod_time > 3600:
            os.remove(file_path)