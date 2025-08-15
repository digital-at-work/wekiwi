# wekiwi-ai-search-and-feature-extraction/app/api/v1/content/parse_and_reply.py
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
# Remove Pydantic imports from here, they should be in types.py
# from pydantic import BaseModel, Field
from typing import List, Optional, Any # Keep typing imports
from loguru import logger
import asyncio

# Import the actual background task function
# Import the actual background task function
from app.internal.utils.pdf_parser import process_pdf_and_create_reply_task
# Import the payload model from the types file
from app.internal.types import PdfParseTriggerPayload
# Import specific config variables directly
from app.config import DIRECTUS_URL, DIRECTUS_ADMIN_KEY
# Import the throttling utility
from app.internal.utils.throttle import throttled_task


# Remove the local class definition
# class PdfParseTriggerPayload(BaseModel):
#     ... (definition removed) ...

router = APIRouter(
    prefix="/pdf", # Added prefix for clarity within content routes
    tags=["PDF Parsing"],
)

@router.post(
    "/trigger-parse",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Triggers the asynchronous parsing of a PDF and creation of a reply. Only to be used by Directus Flow.",
)
async def trigger_pdf_parse_and_reply(
    payload: PdfParseTriggerPayload,
    request: Request,
    background_tasks: BackgroundTasks,
    # Add API Key dependency if needed for this specific backend
    # api_key: str = Depends(get_api_key) # Assuming check_authentication in main.py covers this router
):
    """
    Receives a trigger from Directus Flow when a PDF document content item is created.
    Schedules a background task to fetch the PDF, call the external conversion service,
    poll for results, and create a reply content item in Directus.
    """
    logger.info(f"Received trigger to parse PDF for file_id: {payload.directus_file_id}, parent_id: {payload.parent_content_id}")

    # Use the directly imported config variables
    directus_url = DIRECTUS_URL
    directus_token = DIRECTUS_ADMIN_KEY

    # Validate necessary config is present
    if not directus_url or not directus_token:
        logger.error("DIRECTUS_URL or DIRECTUS_ADMIN_KEY not configured in environment/config.")
        raise HTTPException(status_code=500, detail="Backend configuration error: Directus config missing.")

    # Schedule the background task with throttling
    try:
        background_tasks.add_task(
            throttled_task,
            process_pdf_and_create_reply_task, # The function to be throttled
            payload=payload,
            # Pass necessary config/auth
            directus_url=directus_url,
            directus_token=directus_token
        )
        logger.info(f"Scheduled throttled background task for file_id: {payload.directus_file_id}")
    # Remove the ImportError fallback block
    except Exception as e:
        logger.error(f"Failed to schedule background task: {e}")
        raise HTTPException(status_code=500, detail="Failed to schedule PDF processing task.")

    return {"status": "PDF processing initiated", "file_id": payload.directus_file_id}
