from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Union
import os
from handle_file import FileProcessor
from datetime import datetime
import traceback

# Load environment variables from .env file (if any)
load_dotenv()

class Response(BaseModel):
    result: Union[str, None]

# Consider adding your Heroku app URL to the origins list
origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",
    os.getenv("FRONTEND_URL")
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

@app.post("/predict", response_model=Response)
async def predict(file: UploadFile = File(...), question: str = Form(...), timestamp: str = Form(...)) -> Response:
    # Format and save the file
    try:
        # Save the file to the specified directory
        timestamp_dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
        formatted_str = timestamp_dt.strftime("%Y%m%d_%H%M%S")
        file_name = list(os.path.splitext(file.filename))[0] + "_" + formatted_str + list(os.path.splitext(file.filename))[1]
        file_location = os.path.join(UPLOAD_DIR, file_name)
        if not (os.path.exists(file_location)):
            with open(file_location, "wb") as file_object:
                file_object.write(file.file.read())
        file_process_obj = FileProcessor()
        query_result = str(file_process_obj.process_file(file_location, question))

        result = f"File saved to {file_location}, question: {question}, timestamp: {timestamp}"
        print(query_result)

        return {"result": query_result}

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

    return {"result": query_result}
