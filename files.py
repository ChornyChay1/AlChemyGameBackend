 
from PIL import Image
from fastapi import UploadFile
import io
import os 
from DB import SessionLocal 

from sqlalchemy.orm import joinedload
from sqlalchemy import select, delete, insert
from fastapi import APIRouter, Depends, HTTPException, status, Request, File

from fastapi.responses import FileResponse 
from PydanticModels  import FileInfo
from DB import FileTable
from fastapi.responses import StreamingResponse
from fastapi import Request
import mimetypes

router = APIRouter()

@router.get("/api/files/video/{id_file}")
def get_file(id_file: int):
    with SessionLocal() as session:
        query = select(FileTable).where(FileTable.id == id_file)
        result = session.execute(query)
        fileinfo = result.scalars().first()

        if fileinfo is None:
            raise HTTPException(404, "File not found")

        file_path = os.path.join("Data", "files", str(id_file))
        mime_type, _ = mimetypes.guess_type(file_path)

        if not mime_type:
            mime_type = 'application/octet-stream'

        def file_iterator(file_path: str):
            with open(file_path, 'rb') as f:
                while chunk := f.read(1024):
                    yield chunk

        return StreamingResponse(file_iterator(file_path), media_type=mime_type)

def make_image(file: UploadFile, name: str = None) -> FileInfo:
    file_buf = io.BytesIO(file.file.read())
    filename = name if name else file.filename
    try:
        with Image.open(file_buf) as img:
            width, height = img.size
            max_side = max(width, height)

            if max_side > 1920:
                aspect_ratio = width / height
                if aspect_ratio > 1:
                    new_height = 1920
                    new_width = int(aspect_ratio * new_height)
                else:
                    new_width = 1920
                    new_height = int(new_width / aspect_ratio)

                resized_img = img.resize((new_width, new_height), Image.ANTIALIAS)
                file_buf.seek(0)
                file_buf.truncate(0)
                resized_img.save(file_buf, format='JPEG')
                resized_img.close()

        with SessionLocal() as session:
            query = insert(FileTable).values(name=filename).returning(FileTable.id)
            result = session.execute(query)
            file_id = result.scalars().first()

            with open(os.path.join("Data", "files", str(file_id)), "wb") as f:
                f.write(file_buf.getbuffer())

            session.commit()
        return FileInfo(id=file_id, name=filename)

    except:
        raise HTTPException(status_code="400", detail="Error loading image")
    finally:
        file_buf.close()

def make_file(file: UploadFile, name: str = None) -> FileInfo:
    filename = name if name else file.filename
    with SessionLocal() as session:
        query = insert(FileTable).values(name=filename).returning(FileTable.id)
        result = session.execute(query)
        file_id = result.scalars().first()

        with open(os.path.join("Data", "files", str(file_id)), "wb") as f:
            f.write(file.file.read())

        session.commit()
        return FileInfo(id=file_id, name=filename)

@router.get("/api/files/{id_file}")
def get_file(id_file: int) -> FileResponse:
    with SessionLocal() as session:
        query = select(FileTable).where(FileTable.id == id_file)
        result = session.execute(query)
        fileinfo = result.scalars().first()

        if fileinfo is None:
            raise HTTPException(404, "File not found")

        return FileResponse(
            path=os.path.join("Data", "files", str(id_file)),
            filename=fileinfo.name,
            media_type='multipart/form-data'
        )

@router.post("/api/files/")
def post_file(file: UploadFile) -> FileInfo:
    return make_file(file=file)

@router.get("/api/files/info/{file_id}", response_model=FileInfo)
def get_file_info(file_id: int):
    with SessionLocal() as session:
        query = select(FileTable).where(FileTable.id == file_id)
        result = session.execute(query)
        file_record = result.scalars().first()

        if not file_record:
            raise HTTPException(status_code=404, detail="File not found")

        return FileInfo(id=file_record.id, name=file_record.name)

@router.delete("/api/files/{id_file}")
def delete_file(id_file: int  ) -> FileInfo:  
    with SessionLocal() as session:
        query = select(FileTable).where(FileTable.id == id_file)
        result = session.execute(query)
        fileinfo = result.scalars().first()

        if fileinfo is None:
            raise HTTPException(404, "File not found")

        session.execute(delete(FileTable).where(FileTable.id == id_file))
        session.commit()
        try:
            os.remove(os.path.join("Data", "files", str(id_file)))
        except:
            pass

        return fileinfo

def get_file_range_response(file_path: str, range_header: str):
    file_size = os.path.getsize(file_path)
    range_start, range_end = 0, file_size - 1

    if range_header:
        range_values = range_header.replace("bytes=", "").split("-")
        range_start = int(range_values[0]) if range_values[0] else 0
        range_end = int(range_values[1]) if range_values[1] else file_size - 1

    range_end = min(range_end, file_size - 1)
    chunk_size = range_end - range_start + 1

    with open(file_path, "rb") as f:
        f.seek(range_start)
        data = f.read(chunk_size)

    content_range = f"bytes {range_start}-{range_end}/{file_size}"
    return data, content_range

@router.get("/api/files/stream/{file_id}")
def stream_file(file_id: int, request: Request):
    file_base_path = os.path.join("Data", "files", str(file_id))
    file_path = f"{file_base_path}.mp4"

    if not os.path.exists(file_path):
        if os.path.exists(file_base_path):
            file_path = file_base_path
        else:
            raise HTTPException(status_code=404, detail="File not found")

    range_header = request.headers.get("Range", None)
    if range_header:
        data, content_range = get_file_range_response(file_path, range_header)
        response = StreamingResponse(io.BytesIO(data), media_type="video/mp4")
        response.headers["Content-Range"] = content_range
        response.headers["Accept-Ranges"] = "bytes"
        response.headers["Content-Length"] = str(len(data))
        response.status_code = 206   
    else:
        with open(file_path, "rb") as video_file:
            response = StreamingResponse(video_file, media_type="video/mp4")
            response.headers["Content-Length"] = str(os.path.getsize(file_path))

    return response

@router.get("/api/files/pdf/{id_file}")
def get_pdf_file(id_file: int):
 
    with SessionLocal() as session:
        query = select(FileTable).where(FileTable.id == id_file)
        result = session.execute(query)
        fileinfo = result.scalars().first()

        if fileinfo is None:
            raise HTTPException(404, detail="File not found")

 
        file_path = os.path.join("Data", "files", str(id_file))

 
        if not fileinfo.name.endswith(".pdf"):
            raise HTTPException(400, detail="The requested file is not a PDF")
 
        return FileResponse(
            path=file_path,
            filename=fileinfo.name,
            media_type='application/pdf'
        )