from fastapi import FastAPI, UploadFile, File, HTTPException
from minio import Minio
from minio.error import S3Error
import os

app = FastAPI()

minio_client = Minio(
    "minio:9000",
    access_key=os.getenv("MINIO_ACCESS_KEY"),
    secret_key=os.getenv("MINIO_SECRET_KEY"),
    secure=False
)

bucket_name = "memes"
if not minio_client.bucket_exists(bucket_name):
    minio_client.make_bucket(bucket_name)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        minio_client.put_object(
            bucket_name, file.filename, file.file, length=-1, part_size=10*1024*1024
        )
        return {"filename": file.filename}
    except S3Error as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@app.get("/files/{filename}")
async def get_file(filename: str):
    try:
        response = minio_client.get_object(bucket_name, filename)
        return StreamingResponse(response, media_type="application/octet-stream")
    except S3Error as exc:
        raise HTTPException(status_code=404, detail="File not found")
