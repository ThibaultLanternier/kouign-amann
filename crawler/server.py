from email.policy import strict
import logging
from contextlib import asynccontextmanager
from math import pi
from os import path
from pathlib import Path
from uuid import uuid4

from fastapi import BackgroundTasks, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.tools.config_file import ConfigFileManager
from app.tools.logger import init_console_log
from app.use_cases import list_pictures
from app.use_cases.backup import BackupUseCase, backup_use_case_factory
from app.workers.list_pictures_worker import ListPicturesJob, ListPictureJobResult
from app.workers.data_store import DataStore
from app.tools.file import FileTools

# Initialize logging
init_console_log()
logger = logging.getLogger("app.api")

# Initialize worker



@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI application"""
    # Startup: Initialize BackupUseCase
    logger.info("Starting application, initializing BackupUseCase...")

    config_manager = ConfigFileManager()

    list_pictures_use_case = list_pictures.list_pictures_use_case_factory()

    backup_use_case = backup_use_case_factory(
        backup_folder_path=config_manager.get_backup_folder_path(),
        sharded_folder_path=config_manager.get_sharded_backup_folder_path()
    )

    # Store in app.state for access in endpoints
    app.state.backup_use_case = backup_use_case
    app.state.list_pictures_use_case = list_pictures_use_case

    results_directory = Path.home() / ".kouign-amann" / "api_results"
    
    app.state.data_store = DataStore[ListPictureJobResult](output_directory=results_directory)

    logger.info("BackupUseCase initialized successfully")

    yield

    # Shutdown: cleanup if needed
    logger.info("Shutting down application...")


# Create FastAPI app
app = FastAPI(
    title="Kouign-Amann API",
    description="API for backup and picture management",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class ListPicturesRequest(BaseModel):
    """Request model for backup folder endpoint"""
    path: str


class ListPictureAsyncResponse(BaseModel):
    """Response model for async backup folder endpoint"""
    picture_list_id: str

class PictureBackupRequest(BaseModel):
    """Request model for picture backup endpoint"""
    path: str
    strict_mode: bool = False

class PictureBackupResponse(BaseModel):
    """Response model for picture backup endpoint"""
    hash: str

class PicturePathResponse(BaseModel):
    """Response model for picture path lookup endpoint"""
    path: str

class DirectoryListRequest(BaseModel):
    """Request model for directory listing endpoint"""
    path: str

class DirectoryListResponse(BaseModel):
    """Response model for directory listing endpoint"""
    directories: list[str]

@app.post("/picture-list", response_model=ListPictureAsyncResponse)
async def create_list_pictures(
    request_body: ListPicturesRequest,
    background_tasks: BackgroundTasks,
    request: Request
    ) -> ListPictureAsyncResponse:
    """
    Asynchronously list pictures in a folder

    This endpoint queues a job and returns immediately with a list_pictures_id.
    
    The job is processed asynchronously and results are saved to disk.
    """
    try:
        # Validate input path
        target_folder_path = Path(request_body.path)
        if not target_folder_path.exists():
            raise HTTPException(
                status_code=400,
                detail=f"Path does not exist: {request_body.path}"
            )

        if not target_folder_path.is_dir():
            raise HTTPException(
                status_code=400,
                detail=f"Path is not a directory: {request_body.path}"
            )

        # Create a job with unique ID
        job_id = uuid4()
        logger.info(f"Creating backup job {job_id} for folder {target_folder_path}")

        list_pictures_job = ListPicturesJob(
            job_id=job_id, 
            list_pictures_use_case=request.app.state.list_pictures_use_case, 
            data_store=request.app.state.data_store
        )

        list_pictures_job.init(target_folder=target_folder_path)
        background_tasks.add_task(list_pictures_job.run)

        logger.info(f"Backup job {job_id} queued for folder {request_body.path}")

        return ListPictureAsyncResponse(picture_list_id=str(job_id))

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error queuing backup job: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.get("/picture-list/{picture_list_id}")
async def get_list_pictures(picture_list_id: str, request: Request) -> ListPictureJobResult:
    """
    Get the result of an async list pictures job.
    """
    try:
        result = request.app.state.data_store.load_data(
            identifier=picture_list_id,
            model_class=ListPictureJobResult
        )
        
        return result

    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Backup job {picture_list_id} not found"
        )
    except Exception as e:
        logger.exception(f"Error retrieving backup result: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.post("/picture")
async def backup_picture(request_body: PictureBackupRequest, request: Request, response: Response) -> PictureBackupResponse:
    try:
        target_picture_path = Path(request_body.path)
        strict_mode = request_body.strict_mode
        logger.info(f"Received request to backup picture {target_picture_path} with strict_mode={strict_mode}")
        backup_use_case: BackupUseCase = request.app.state.backup_use_case
        success, picture_data = backup_use_case.backup_single_picture(picture_path=target_picture_path, strict_mode=strict_mode)

        if picture_data is None:
            raise HTTPException(
                status_code=422,
                detail=f"Failed to backup picture {target_picture_path}"
            )

        if success:
            response.status_code = 201
        else:
            response.status_code = 200
        
        return PictureBackupResponse(hash=picture_data.get_hash())
        
    except Exception as e:
        logger.exception(f"Error retrieving backup result: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/picture/{picture_hash}")
async def get_picture(picture_hash: str, request: Request):
    try:
        backup_use_case: BackupUseCase = request.app.state.backup_use_case

        picture_buffer = backup_use_case.get_picture_by_hash(picture_hash=picture_hash)

        if picture_buffer is None:
            raise HTTPException(
                status_code=404,
                detail=f"Picture with hash {picture_hash} not found"
            )

        return Response(content=picture_buffer, media_type="image/jpeg")
    except Exception as e:
        logger.exception(f"Error retrieving picture by hash: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
    
@app.post("/directories")
async def list_directories(request: DirectoryListRequest) -> DirectoryListResponse:
    """List all directories in the given path"""
    try:
        file_tools = FileTools()
        directory_list = file_tools.list_directories(root_path=Path(request.path))

        return DirectoryListResponse(directories=[str(dir_path) for dir_path in directory_list])

    except ValueError as ve:
        raise HTTPException(
            status_code=404,
            detail=str(ve)
        )
    
    except PermissionError as pe:
        raise HTTPException(
            status_code=403,
            detail=str(pe)
        )   
    
    except Exception as e:
        logger.exception(f"Error listing directories: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
