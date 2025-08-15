# Made open source under the GNU Affero General Public License, Version 3 (AGPL-3.0),
# by digital@work GmbH (2024). This file is part of wekiwi.
# See the LICENSE file in the project root or https://www.gnu.org/licenses/agpl-3.0.html for details.

from ast import alias
from fastapi import APIRouter, BackgroundTasks, UploadFile, Form, HTTPException, status
from fastapi import File, Query, Depends
from typing import List, Optional, Union
from loguru import logger
import asyncio
# Removed unused import: from pydantic import conlist

from app.internal.utils.pdf_parser import process_pdf_and_create_content_task
from app.config import DIRECTUS_URL, DIRECTUS_ADMIN_KEY
from app.internal.types import DirectPdfUploadRequest
from app.internal.directus import UserDirectusClient
from app.internal.utils.throttle import throttled_task

from fastapi import Request
from fastapi import Header
from fastapi.responses import JSONResponse
import zipfile
from io import BytesIO

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

router = APIRouter(
    prefix="/pdf",  # Use the same prefix as parse_and_reply.py
    tags=["PDF Parsing"],
)
limiter = Limiter(key_func=lambda request:getattr(request.state,"user_id","anonymous"))
@router.post(
    "/direct-upload",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Upload documents directly and create content items using your Directus token",
    description="""
    Directly upload a PDF or DOCX file to process and create content in wekiwi.
    This endpoint requires your static Directus token for authentication.
    
    You must provide the circle_ids and access_token in the form data.
    At least one file (PDF or DOCX) must be provided.
    
    The uploaded file will be processed and a content item will be created in wekiwi 
    for the authenticated user.
    
    **Authentication**: Provide your static Directus token in the access_token form field.
    """,
    responses={
        401: {"description": "Unauthorized: Missing or invalid token"},
        400: {"description": "Bad Request: Missing required parameters or files"},
        500: {"description": "Server Error: Failed to process files"}
    },
)
@limiter.limit("1000/day")
# @limiter.limit("1/10seconds")
# async def direct_pdf_upload
async def direct_document_upload(
    request: Request,
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(..., description="PDF files to upload and process"),
    circle_ids: Optional[str] = Form(
        default=None,
        description="Comma-separated list of circle IDs for the content (e.g., '1,2,3').\n"
        "Leave empty to automatically use the user's assigned circles from Directus.",
        example="1,2,3"),
    access_token: str = Form(..., description="Your static Directus token for authentication"),
):
    """
    Endpoint for direct document upload via Swagger UI.
    Requires user's static Directus token for authentication.
    Creates content in Directus after processing PDFs/DOCX files.
    """
    MAX_SIZE = 10 * 1024 * 1024  # 10 MB

    def validate_file_size(file_data: bytes, filename: str, max_size: int = MAX_SIZE):
        actual_size = len(file_data)
        logger.info(f"File size: {actual_size} bytes ({actual_size / (1024 * 1024):.2f} MB)")
        
        if not file_data or actual_size == 0:
            raise HTTPException(status_code=400, detail=f"Empty file: {filename}")
        if actual_size > max_size:
            raise HTTPException(status_code=413, detail=f"File too large: {filename} is {(actual_size / (1024 * 1024)):.2f}MB, max allowed is {max_size // (1024*1024)}MB")

    pdf_files = []
    docx_files = []


    if not files:
        raise HTTPException(status_code=400, detail="No files provided")


    for file in files:
        file_data = await file.read()
        validate_file_size(file_data, file.filename)

        if file_data.startswith(b"%PDF-"):
            pdf_files.append((file, file_data))
        elif zipfile.is_zipfile(BytesIO(file_data)):
            docx_files.append((file, file_data))
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.filename}")

    # Process circle_ids from comma-separated string to list of integers
    # try:
    #     circle_ids_list = [int(cid.strip()) for cid in circle_ids.split(",") if cid.strip()]
    #     if not circle_ids_list:
    #         raise ValueError("No valid circle IDs provided")
    # except ValueError as e:
    #     raise HTTPException(status_code=400, detail=f"Invalid circle_ids format: {str(e)}")

    # Validate token
    if not access_token:
        raise HTTPException(status_code=401, detail="Unauthorized: Missing access token")

    # Validate necessary config is present
    if not DIRECTUS_URL:
        logger.error("DIRECTUS_URL not configured in environment/config.")
        raise HTTPException(status_code=500, detail="Backend configuration error: Directus URL missing.")
    
    directus_client = UserDirectusClient(DIRECTUS_URL, access_token)
    try:
        # Fetch the current user's data using the provided access token
        user_info = await directus_client.get_user_info()
        request.state.user_id = str(user_info.get("id","anonymous"))
    except Exception as e:    
        logger.error(f"Error getting user info: {str(e)}")
        raise HTTPException(status_code=500, detail="Backend error: Failed to get user info.")

    try:
        # Get company_id from user info
        company_id = user_info.get("company_id")
        logger.info(f"Using company_id {company_id} from user info.")
        
        # If no circle_ids provided, extract them from the user's associated circles
        if circle_ids:
            circle_ids_list = [int(cid.strip()) for cid in circle_ids.split(",") if cid.strip()]
        else:
            user_circles=user_info.get("user_circles",[])
            circle_ids_list = [circle["circle_id"] for circle in user_circles if "circle_id" in circle]
            logger.info(f"Using circle_ids {circle_ids_list} from user info.")
    except Exception as e:
        logger.error(f"Error processing circle_ids or company_id: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid circle_ids or company_id format: {str(e)}")
    processed_files = []

    # Process PDF file if provided
    for pdf_file, pdf_data in pdf_files:
        try:
            # Read the file data
            # pdf_data = await pdf_file.read()
            # validate_file_size(pdf_data, pdf_file.filename)
            # if not pdf_data or len(pdf_data) == 0:
            #     logger.warning(f"Empty file: {pdf_file.filename}. Skipping.")
            # else:
                # Schedule the background task for this file with throttling
                background_tasks.add_task(
                    throttled_task,
                    process_pdf_and_create_content_task,
                    document_data=pdf_data,
                    filename=pdf_file.filename,
                    directus_url=DIRECTUS_URL,
                    directus_token=access_token,
                    company_id=company_id,
                    circle_ids=circle_ids_list
                )
                
                # Append the filename to processed_files list
                processed_files.append(pdf_file.filename)
                logger.info(f"Scheduled throttled processing for file: {pdf_file.filename}")
        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error(f"Error processing file {pdf_files.filename}: {str(e)}")
    
    # Process DOCX file if provided
    for docx_file, docx_data in docx_files:
        try:
            # Read the file data
            # docx_data = await docx_file.read()
            # validate_file_size(docx_data, docx_file.filename)
            # if not docx_data or len(docx_data) == 0:
            #     logger.warning(f"Empty file: {docx_file.filename}. Skipping.")
            # if not zipfile.is_zipfile(BytesIO(docx_data)):
            #     raise HTTPException(status_code=400, detail="Invalid file format: DOCX(not a ZIP archive)")
            # else:
                # Schedule the background task for this file with throttling
                background_tasks.add_task(
                    throttled_task,
                    process_pdf_and_create_content_task,
                    document_data=docx_data,
                    filename=docx_file.filename,
                    directus_url=DIRECTUS_URL,
                    directus_token=access_token,
                    company_id=company_id,
                    circle_ids=circle_ids_list
                )
                
                # Append the filename to processed_files list
                processed_files.append(docx_file.filename)
                logger.info(f"Scheduled throttled processing for file: {docx_file.filename}")
        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error(f"Error processing file {docx_file.filename}: {str(e)}")

    # If no files were processed, raise an error
    if not processed_files:
        raise HTTPException(status_code=500, detail="Failed to process any of the provided files(PDF/DOCX)")

    # Return the status and the list of processed files
    return {
        "status": "Document processing initiated",
        "files": processed_files,
        "message": "The documents(PDF/DOCX) are being processed and content will be created in Directus"
    }

# @router.middleware("http")
# async def rate_limiter(request: Request, call_next):
#     try:
#         response = await call_next(request)
#         return response
#     except RateLimitExceeded as e:
#         logger.warning(f"Rate limit exceeded for user: {str(e)}")
#         return JSONResponse(status_code=status.HTTP_429_TOO_MANY_REQUESTS, content={"detail":"Rate limit exceeded:Max 1000 uploads/day"})
    