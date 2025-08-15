# wekiwi-ai-search-and-feature-extraction/app/internal/utils/pdf_parser.py
from io import BytesIO
from unittest import result
import httpx
import asyncio
import base64 # Needed if we fetch asset data as base64
from typing import Any, Dict, Optional, List
from loguru import logger
# Import the custom DirectusClient implementation
from app.internal.directus import DirectusClient, UserDirectusClient

# Import the payload model from the types file
from app.internal.types import PdfParseTriggerPayload
# Import config to get URLs and Keys
from app.config import DAW_API_HUB_URL, DAW_HUB_KEY
from markitdown import MarkItDown
import html

# --- Helper Function to Get Asset Data ---
# Consider moving this to app/internal/directus/directus.py if reusable
# Add directus_base_url and directus_token as arguments
async def get_directus_asset_data(file_id: str, directus_base_url: str, directus_token: str) -> Optional[bytes]:
    """Fetches raw asset data from Directus using provided URL and token."""
    # Note: directus_client object is no longer needed here
    try:
        # Construct URL using the passed base URL
        asset_url = f"{directus_base_url.rstrip('/')}/assets/{file_id}"
        # Use the passed token directly for the Authorization header
        headers = {"Authorization": f"Bearer {directus_token}"}

        async with httpx.AsyncClient(timeout=300.0) as client: # Added timeout
            response = await client.get(asset_url, headers=headers, follow_redirects=True)
            response.raise_for_status() # Raise exception for 4xx/5xx errors
            logger.info(f"Successfully fetched asset data for file_id: {file_id}")
            return response.content
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error fetching asset {file_id} from Directus: {e.response.status_code} - {e.response.text}")
        return None
    except Exception as e:
        logger.error(f"Error fetching asset {file_id} from Directus: {e}")
        return None

# --- Background Task Function ---
async def process_pdf_and_create_reply_task(
    payload: PdfParseTriggerPayload,
    directus_url: str, # Keep this argument
    directus_token: str # This is the admin token
):
    """
    Background task to process PDF and create reply.
    1. Initializes Directus client.
    2. Fetches PDF data from Directus.
    3. Calls external conversion service (daw-api-hub).
    4. Polls for conversion completion.
    5. Downloads converted text.
    6. Creates reply content item in Directus.
    """
    logger.info(f"Starting PDF processing task for file_id: {payload.directus_file_id}")

    # 1. Initialize Directus Client
    try:
        # Use the custom DirectusClient implementation from app.internal.directus
        # Do NOT switch to UserDirectusClient, as it will not work for the parsing that is triggered by the 'Trigger Parse' directus flow.
        directus_client = DirectusClient(directus_url, directus_token)
        logger.info("Directus client initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize Directus client: {e}")
        return  # Cannot proceed without Directus client

    # 2. Fetch PDF Data
    # Pass file_id, url, and token to the helper function
    pdf_data = await get_directus_asset_data(payload.directus_file_id, directus_url, directus_token)
    if not pdf_data:
        logger.error(f"Failed to fetch PDF data for file_id: {payload.directus_file_id}. Aborting task.")
        return

    logger.info("DEBUG: After fetching PDF data, before checking external service config")
    
    # Debug logging for configuration values
    try:
        logger.info(f"DEBUG: DAW_API_HUB_URL value: {DAW_API_HUB_URL}")
        logger.info(f"DEBUG: DAW_HUB_KEY exists: {bool(DAW_HUB_KEY)}")
    except Exception as e:
        logger.error(f"ERROR inspecting config variables: {e}")
    
    # 3. Call External Conversion Service (daw-api-hub)
    try:
        external_service_url = DAW_API_HUB_URL
        logger.info(f"DEBUG: Successfully got external_service_url: {external_service_url}")
    except Exception as e:
        logger.error(f"ERROR accessing DAW_API_HUB_URL: {e}")
        return
        
    try:
        external_service_key = DAW_HUB_KEY
        logger.info(f"DEBUG: Successfully got external_service_key: {bool(external_service_key)}")
    except Exception as e:
        logger.error(f"ERROR accessing DAW_HUB_KEY: {e}")
        return

    logger.info(f"DEBUG: External service URL: {external_service_url}")
    logger.info(f"DEBUG: External service key exists: {bool(external_service_key)}")

    # Ensure config values are loaded
    if not external_service_url or not external_service_key:
        logger.error("DAW_API_HUB_URL or DAW_HUB_KEY not configured. Aborting task.")
        return

    # Use the correct endpoint that expects multipart/form-data
    conversion_endpoint = f"{external_service_url.rstrip('/')}/docling/docling/convert-pdf?use_background=true"
    task_id: Optional[str] = None

    try:
        async with httpx.AsyncClient(timeout=300.0) as client: # Increased timeout
            # Prepare multipart/form-data
            files = {'file': (f"{payload.directus_file_id}.pdf", pdf_data, 'application/pdf')}
            headers = {
                'accept': 'application/json',
                'DAW-Hub-Key': external_service_key
                # Content-Type is set automatically by httpx for multipart/form-data
            }
            logger.info(f"Calling external conversion service: {conversion_endpoint}")
            logger.info(f"PDF data size: {len(pdf_data)} bytes")
            logger.info(f"Request headers: {headers}")
            logger.info(f"File name in request: {payload.directus_file_id}.pdf")
            
            try:
                response = await client.post(conversion_endpoint, files=files, headers=headers)
                logger.info(f"Conversion service response status: {response.status_code}")
                logger.info(f"Conversion service response headers: {dict(response.headers)}")
                logger.info(f"Conversion service response content: {response.content[:500]}...")  # Log first 500 chars to avoid huge logs
                response.raise_for_status()
                response_data = response.json()
                logger.info(f"Conversion service response data: {response_data}")
                task_id = response_data.get("task_id")
                if not task_id:
                    # Handle potential synchronous response from daw-api-hub if file is small
                    if response_data.get("text") is not None:
                         logger.info("Conversion service returned synchronous result.")
                         # Skip polling and downloading, go directly to creating reply
                         parsed_text = response_data.get("text")
                         # Proceed to step 6
                    else:
                         logger.error(f"Conversion service did not return task_id or text. Response: {response_data}")
                         return
                else:
                     logger.info(f"Conversion task initiated with task_id: {task_id}")
                     parsed_text = None # Needs polling

            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error calling conversion service: {e.response.status_code} - {e.response.text}")
                return
            except Exception as e:
                logger.error(f"Error calling conversion service: {e}")
                return

    except Exception as e:
        logger.error(f"Error calling conversion service: {e}")
        return

    # 4. Poll for Completion (only if task_id was received)
    if task_id:
        status_endpoint = f"{external_service_url.rstrip('/')}/docling/docling/task-status/{task_id}"
        polling_interval = 10 # seconds
        max_polling_attempts = 36 # 36 * 10s = 6 minutes timeout

        logger.info(f"Polling status endpoint: {status_endpoint}")
        for attempt in range(max_polling_attempts):
            await asyncio.sleep(polling_interval) # Wait *before* polling (gives task time to start)
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    headers = {'accept': 'application/json', 'DAW-Hub-Key': external_service_key}
                    logger.info(f"Polling attempt {attempt+1}/{max_polling_attempts} - Sending request to: {status_endpoint}")
                    logger.info(f"Polling request headers: {headers}")
                    
                    response = await client.get(status_endpoint, headers=headers)
                    logger.info(f"Polling response status: {response.status_code}")
                    logger.info(f"Polling response headers: {dict(response.headers)}")
                    logger.info(f"Polling response content: {response.content[:500]}...")  # Log first 500 chars
                    
                    response.raise_for_status()
                    status_data = response.json()
                    current_status = status_data.get("status")
                    logger.info(f"Polling attempt {attempt+1}/{max_polling_attempts}: Status = {current_status}")
                    if current_status == "completed":
                        logger.info(f"Task {task_id} completed.")
                        # Text should be included in status response now due to previous change
                        parsed_text = status_data.get("result_text")
                        if parsed_text is None:
                             logger.warning(f"Task {task_id} completed but result_text missing in status response. Will attempt download.")
                             # Fallback to download if text not in status
                        break # Exit polling loop
                    elif current_status == "failed":
                        error_message = status_data.get("error", "Unknown error")
                        logger.error(f"Conversion task {task_id} failed: {error_message}")
                        return # Stop processing

                # Wait is now at the beginning of the loop

            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error polling task status: {e.response.status_code} - {e.response.text}")
                # Continue polling
            except Exception as e:
                logger.error(f"Error polling task status: {e}")
                # Continue polling
        else: # Loop finished without breaking (timeout)
            logger.error(f"Polling timeout for task {task_id} after {max_polling_attempts} attempts.")
            return

    # 5. Download Text (Fallback if not included in status)
    if task_id and parsed_text is None: # Only download if polling finished but text wasn't in status
        download_endpoint = f"{external_service_url.rstrip('/')}/docling/docling/download-converted/{task_id}"
        logger.info(f"Attempting fallback download from: {download_endpoint}")
        try:
            async with httpx.AsyncClient(timeout=300.0) as client:
                headers = {'accept': 'text/plain', 'DAW-Hub-Key': external_service_key} # Expect plain text
                logger.info(f"Download fallback request headers: {headers}")
                
                response = await client.get(download_endpoint, headers=headers)
                logger.info(f"Download fallback response status: {response.status_code}")
                logger.info(f"Download fallback response headers: {dict(response.headers)}")
                logger.info(f"Download fallback response content (first 500 chars): {response.text[:500]}...")
                
                response.raise_for_status()
                parsed_text = response.text
                logger.info(f"Successfully downloaded converted text via fallback (length: {len(parsed_text)}).")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error during fallback download: {e.response.status_code} - {e.response.text}")
            return
        except Exception as e:
            logger.error(f"Error during fallback download: {e}")
            return

    if parsed_text is None: # Check if text is still None after polling/downloading
        logger.error("Failed to retrieve parsed text. Aborting reply creation.")
        return

    # 6. Create Reply in Directus
    logger.info(f"Creating reply content item in Directus for parent_id: {payload.parent_content_id}")
    try:
        # Ensure circle_ids is a list of dicts for Directus
        circle_contents_payload = [{'circle_id': cid} for cid in payload.circle_ids]

        # Include user_created in the payload - DirectusClient.create_item will handle this properly
        reply_payload = {
            "text": parsed_text,
            "parent_id": payload.parent_content_id,
            "company_id": payload.company_id,
            "circle_contents": circle_contents_payload,
            "content_type": 'text',
            # Use the title from the payload if available
            "title": payload.title if payload.title else "",
            # Include user_created for proper attribution - DirectusClient will handle this
            "user_created": payload.user_created_id if payload.user_created_id else None
        }
        
        # The DirectusClient.create_item method will handle user attribution automatically
        created_item = directus_client.create_item("contents", reply_payload)
        logger.info(f"Successfully created reply content item with ID: {created_item.get('content_id')}")

    except Exception as e:
        # Log the payload for debugging if creation fails
        logger.error(f"Payload for failed Directus create: {reply_payload}")
        logger.error(f"Failed to create reply content item in Directus: {e}")
        # Consider adding retry logic or specific error handling

    logger.info(f"Finished PDF processing task for file_id: {payload.directus_file_id}")

# --- Added for Direct PDF Upload Processing ---
async def process_pdf_and_create_content_task(
    document_data: bytes,
    filename: str,
    directus_url: str,
    directus_token: str,
    company_id: Optional[int] = None,
    circle_ids: Optional[List[int]] = None
):
    """
    Background task to process a directly uploaded PDF or DOCX file and create content.
    1. Initializes Directus client with the user's token.
    2. Calls external conversion service (daw-api-hub) for PDFs or processes DOCX directly.
    3. Polls for conversion completion if PDF.
    4. Downloads converted text.
    5. Creates text content item in Directus using the authenticated user.
    6. Uploads the document to Directus.
    7. Creates document content item with parent_id pointing to text content.
    """
    logger.info(f"Starting direct PDF processing task for file: {filename}")

    # 1. Initialize Directus Client with user's token
    try:
        # Use the UserDirectusClient to authenticate with the user's token directly
        directus_client = UserDirectusClient(directus_url, directus_token)
        logger.info("UserDirectusClient initialized successfully with user token.")
    except Exception as e:
        logger.error(f"Failed to initialize UserDirectusClient: {e}")
        return  # Cannot proceed without Directus client
        
    # Validate that company_id and circle_ids are provided
    if not company_id or not circle_ids:
        logger.error("Missing required company_id or circle_ids for content creation")
        return  # Cannot proceed without company_id and circle_ids
    
        
    logger.info(f"Processing document for company_id: {company_id}, circle_ids: {circle_ids}")

    # 3. Call External Conversion Service (daw-api-hub)
    external_service_url = DAW_API_HUB_URL
    external_service_key = DAW_HUB_KEY
    task_id = None
    parsed_text = None

    #Determine the type of document
    is_pdf = filename.endswith(".pdf")
    is_docx = filename.endswith(".docx")

    # If the file is a PDF, send it to the external service for conversion
    if is_pdf:
        # Validation for external service configuration
        if not external_service_url or not external_service_key:
            logger.error("External conversion service not properly configured. Missing URL or API key.")
            return
        
        try:
            # Endpoint for uploading PDF to conversion service
            upload_endpoint = f"{external_service_url.rstrip('/')}/docling/docling/convert-pdf?use_background=true"
            
            # Prepare the file for upload
            files = {"file": (filename, document_data, "application/pdf")}
            headers = {"Accept": "application/json", "DAW-Hub-Key": external_service_key}
            
            async with httpx.AsyncClient(timeout=300.0) as client:
                logger.info(f"Sending PDF to conversion service at: {upload_endpoint}")
                response = await client.post(upload_endpoint, files=files, headers=headers)
                response.raise_for_status()
                
                # Extract task ID from response
                response_data = response.json()
                task_id = response_data.get("task_id")
                if not task_id:
                    logger.error("No task_id received from conversion service")
                    return
                
                logger.info(f"Conversion task created with ID: {task_id}")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error calling conversion service: {e.response.status_code} - {e.response.text}")
            return
        except Exception as e:
            logger.error(f"Error calling conversion service: {e}")
            return
        # Continue processing - no return here
    # If the file is a DOCX, parse it locally using MarkItDown    
    elif is_docx:
        # Handle DOCX processing
        try:
            # Extract text with preserved formatting
            parsed_text = await extract_markdown_form_docx(document_data)
            content_type = "text"
            logger.info(f"Parsed text: {parsed_text}")
        except Exception as e:
            logger.error(f"Error extracting text from DOCX: {e}")
            return
            
            
    # 4. Poll for Conversion Completion
    if is_pdf and task_id:
        status_endpoint = f"{external_service_url.rstrip('/')}/docling/docling/task-status/{task_id}"
        headers = {"Accept": "application/json", "DAW-Hub-Key": external_service_key}
        
        max_polling_attempts = 12  # 1 minute total (5s intervals)
        polling_interval = 5      # seconds
        
        # Poll the external conversion service until the task is completed or timeout
        for attempt in range(max_polling_attempts):
            await asyncio.sleep(polling_interval)  # Wait first, then poll
            
            try:
                logger.info(f"Polling conversion status, attempt {attempt + 1}/{max_polling_attempts}")
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.get(status_endpoint, headers=headers)
                    response.raise_for_status()
                    
                    status_data = response.json()
                    current_status = status_data.get("status")
                    logger.info(f"Current status: {current_status}")
                    
                    if current_status == "completed":
                        # Check if text is included in the status response
                        parsed_text = status_data.get("text")
                        if parsed_text:
                            logger.info(f"Received parsed text in status response (length: {len(parsed_text)})")
                        else:
                            logger.info("Parsed text not included in status, will use fallback download")
                        break  # Exit polling loop
                    elif current_status == "failed":
                        error_message = status_data.get("error", "Unknown error")
                        logger.error(f"Conversion task {task_id} failed: {error_message}")
                        return  # Stop processing
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error polling task status: {e.response.status_code} - {e.response.text}")
                # Continue polling
            except Exception as e:
                logger.error(f"Error polling task status: {e}")
                # Continue polling
        else:  # Loop finished without breaking (timeout)
            logger.error(f"Polling timeout for task {task_id} after {max_polling_attempts} attempts.")
            return

    # 5. Download Text (Fallback if not included in status)
    if task_id and parsed_text is None:  # Only download if polling finished but text wasn't in status
        download_endpoint = f"{external_service_url.rstrip('/')}/docling/docling/download-converted/{task_id}"
        logger.info(f"Attempting fallback download from: {download_endpoint}")
        try:
            async with httpx.AsyncClient(timeout=300.0) as client:
                headers = {'accept': 'text/plain', 'DAW-Hub-Key': external_service_key}
                
                response = await client.get(download_endpoint, headers=headers)
                response.raise_for_status()
                parsed_text = response.text
                logger.info(f"Successfully downloaded converted text via fallback (length: {len(parsed_text)})")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error during fallback download: {e.response.status_code} - {e.response.text}")
            return
        except Exception as e:
            logger.error(f"Error during fallback download: {e}")
            return

    if parsed_text is None:
        logger.error("Failed to retrieve parsed text. Aborting content creation.")
        return

    # 6. Create Text Content in Directus (this will be the parent)
    text_content_id = None
    logger.info(f"Creating text content item in Directus using authenticated user token")
    try:
        # Ensure circle_ids is a list of dicts for Directus
        circle_contents_payload = [{'circle_id': cid} for cid in circle_ids] if circle_ids else []

        # Extract title from filename (remove extension)
        title = filename
        if "." in filename:
            title = filename.rsplit(".", 1)[0]

        text_content_payload = {
            "text": parsed_text,
            "company_id": company_id,
            "circle_contents": circle_contents_payload,
            "content_type": 'text',
            "title": title
        }
        
        # Create the text content item
        text_content_item = directus_client.create_item("contents", text_content_payload)
        text_content_id = text_content_item.get('content_id')
        logger.info(f"Successfully created text content item with ID: {text_content_id}")
        
        if not text_content_id:
            logger.error("Failed to get text content ID. Cannot create document content.")
            return text_content_item
            
    except Exception as e:
        # Log the payload for debugging if creation fails
        logger.error(f"Payload for failed Directus text content create: {text_content_payload}")
        logger.error(f"Failed to create text content item in Directus: {e}")
        return None

    # 7. Upload PDF to Directus (in the content folder)
    try:
        file_id = directus_client.upload_file(document_data, filename)
        if not file_id:
            logger.error("Failed to upload PDF file to Directus. Document content will not be created.")
            return text_content_item  # Return the text content item anyway
            
        logger.info(f"Successfully uploaded PDF to Directus with file_id: {file_id}")
        
        # 8. Create a document content item in Directus as a child of the text content
        document_payload = {
            "title": None,  # title is null as specified
            "text": None,  # text is null as specified
            "company_id": company_id,
            "circle_contents": circle_contents_payload,
            "content_type": 'document',
            "file_id": file_id,
            "parent_id": text_content_id,  # This is the critical part - set parent to text content
            "to_be_parsed_by_directus_flow": False  # Flag to exclude from post-as-reply flow
        }
        
        document_item = directus_client.create_item("contents", document_payload)
        document_content_id = document_item.get('content_id')
        logger.info(f"Successfully created document content item with ID: {document_content_id}")
        
    except Exception as e:
        logger.error(f"Failed to create document content: {e}")
        # Return the text content item even if document creation failed
        return text_content_item

    logger.info(f"Finished direct PDF processing task for file: {filename}")
    return text_content_item  # Return the text content item (the parent)


async def extract_markdown_form_docx(docx_data: bytes) -> str:
    """
    convert docx file(as bytes) to markdown using Markitdown in memory
    """
    markdown = MarkItDown()
    md_result = markdown.convert(BytesIO(docx_data))
    return md_result.text_content
    
    