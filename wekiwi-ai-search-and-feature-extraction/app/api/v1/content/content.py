# Made open source under the GNU Affero General Public License, Version 3 (AGPL-3.0),
# by digital@work GmbH (2024). This file is part of wekiwi.
# See the LICENSE file in the project root or https://www.gnu.org/licenses/agpl-3.0.html for details.

import time

from fastapi import APIRouter, HTTPException, Request, BackgroundTasks, Body
from pydantic import BaseModel
from typing import Annotated, Union, List
from loguru import logger

from app.internal.errors import ContentNotFound
from app.internal.types import ContentValidated, ContentOptional

from app.internal.milvusdb.handle_db_items import (
    create_content_chunks,
    update_content_chunks,
)


router = APIRouter()


class EmbeddingResponse(BaseModel):
    message: str
    
class DeletionResponse(BaseModel):
    message: str


@router.post(
    "/v1/content/create",
    response_model=EmbeddingResponse,
    summary="Creates a content chunk with embeddings and saves it in MilvusDB.",
)
async def create_content(
    request: Request,
    background_tasks: BackgroundTasks,
    content: Annotated[
        ContentValidated,
        Body(description="Content to be embedded"),
    ],
    circle_ids: Annotated[
        List[int],
        Body(
            description="Circle_id(s) that the user has access to and the item(s) should be posted in.",
        ),
    ],
    company_id: Annotated[
        int,
        Body(description="Company_id of the user posting the item(s)."),
    ],
):
    try:

        logger.info(f"Received embedding request with contents {content}")
        
        # TODO: add support for more types of content
        if not content.title and not content.text:
            raise HTTPException(status_code=400, detail="Title or text must be provided.")

        # Create content chunks
        # TODO: make this more efficient by parallelizing and threading
        db_items = await create_content_chunks(request, background_tasks, content, company_id, circle_ids)

        # Insert content chunks into milvusdb
        await request.state.milvusdbclient.insert_data(db_items)

        logger.info("Content(s) have been successfully embedded.")
        return {"message": "Content has been successfully embedded."}

    except Exception as e:
        logger.error(f"Error embedding content: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put(
    "/v1/content/update",
    response_model=EmbeddingResponse,
    summary="Updates content chunks in MilvusDB with new text, title, ... inlcuding embeddings (if needed).",
)
async def update_content(
    request: Request,
    content: Annotated[
        ContentOptional,
        Body(description="Content item to be embedded."),
    ],
    company_id: Annotated[
        Union[int, None],
        Body(description="Company_id of the user posting the content."),
    ] = None,
    circle_ids: Annotated[
        Union[List[int], None],
        Body(
            description="Circle_id(s) that the user has access to and the content is posted in.",
        ),
    ] = None
):
    try:
        
        logger.info(f"Received embedding update request with content: {content}, company_id: {company_id}, circle_ids: {circle_ids}")
        
        all_fields = [field["name"] for field in request.state.milvusdbclient.describe_collection("contents")["fields"]]

        content_chunks = await request.state.milvusdbclient.get_data(
            filter_expr=f"content_id == {content.content_id}",
            output_fields=all_fields
        )
        
        if len(content_chunks) == 0:
            raise ContentNotFound(f"Content with ID {content.content_id} not found in MilvusDB.")

        if content.text:
            # Delete contents from milvusdb
            await request.state.milvusdbclient.delete_data(filter_expr=f"content_id == {content.content_id}")

            # Construct updated db_items (+re-use existing content_chunks)
            # TODO: make this more efficient by parallelizing and threading
            db_items = await update_content_chunks(
                request, content, content_chunks, company_id, circle_ids
            )
            
            # # DEBUG db_items
            # for i, item in enumerate(db_items):
            #     logger.info(f"--- DB Item {i+1} ---")
            #     for key, value in item.items():
            #         logger.info(f"{key} (Type: {type(value)})")

            # Insert updated content
            await request.state.milvusdbclient.insert_data(db_items)

        else:
            # Construct updated db_items (+re-use existing content_chunks)
            db_items = await update_content_chunks(
                request, content, content_chunks, company_id, circle_ids
            )
            
            # # DEBUG db_items
            # for i, item in enumerate(db_items):
            #     logger.info(f"--- DB Item {i+1} ---")
            #     for key, value in item.items():
            #         logger.info(f"{key} (Type: {type(value)})")

            # Upsert updated content
            await request.state.milvusdbclient.upsert_data(db_items)

        logger.info("Content text embeddings have been successfully updated.")
        return {"message": "Content text embeddings have been successfully updated."}

    except Exception as e:
        logger.error(f"Error updating embeddings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/v1/content/rebuild",
    response_model=EmbeddingResponse,
    summary="Deletes and re-creates the content collection, pulls all content from Directus and rebuilds MilvusDB content chunks.",
)
async def rebuild_milvusdb(request: Request, background_tasks: BackgroundTasks):
    
    start_time = time.time()
    
    try:
        logger.warning(f"Received request to rebuild MilvusDB content chunks.")
        
        # Recreate the content collection
        await request.state.milvusdbclient.recreate_collection("contents")
        
        logger.info(f"MilvusDB collection 'contents' has been recreated.")

        # Get all content IDs from Directus
        content_ids = await request.state.directusclient.get_ids_rebuild(collection="contents")
        
        logger.debug(f"{len(content_ids)} Contents ids pulled from Directus.")

        # Get each content, and create MilvusDB items
        db_items = []
        for content_id_dict in content_ids:
            content_list = await request.state.directusclient.get_contents_rebuild(
                [content_id_dict["content_id"]]
            )
            
            logger.debug(f"{len(content_list)} Content items pulled from Directus.")
            
            circle_ids = [circle["circle_id"]["circle_id"] for circle in content_list[0]["circle_contents"]]
            
            if content_list[0]["company_id"]:
                company_id = content_list[0]["company_id"]
            else:
                company_id = 0
                logger.warning(f"Company_id not found for {content_id_dict["content_id"]}. Setting to 0.")
            
            content = ContentValidated(**content_list[0])

            db_items.extend(
                await create_content_chunks(
                    request, background_tasks, content, company_id, circle_ids
                )
            )
        
        # # DEBUG db_items
        # for i, item in enumerate(db_items):
        #     logger.info(f"--- DB Item {i+1} ---")
        #     for key, value in item.items():
        #         logger.info(f"{key}: (Type: {type(value)})")
        
        # Insert items into MilvusDB
        await request.state.milvusdbclient.insert_data(db_items)
        
        time_taken = (time.time() - start_time)/60

        logger.info("MilvusDB content chunks have been successfully rebuilt.")
        return {"message": f"MilvusDB content chunks have been successfully rebuilt. Time taken: {time_taken:.1f} seconds."}

    except Exception as e:
        logger.error(f"Error rebuilding MilvusDB items: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/v1/content/delete",
    response_model=DeletionResponse,
    summary="Deletes all content chunks with matching content_id(s) from MilvusDB.",
)
async def delete_contents(
    request: Request,
    content_ids: Annotated[
        List[int],
        Body(description="List of content_ids of content chunks to be deleted"),
    ],
):
    try:
        logger.info(f"Received deletion request with content_ids: {content_ids}")
        
        deletion_result = await request.state.milvusdbclient.delete_data(filter_expr=f"content_id in {content_ids}")
        
        logger.info(f"Deleted {deletion_result["delete_count"]} entities.")
        return {"message": f"Deleted {deletion_result["delete_count"]} entities."}

    except Exception as e:
        logger.error(f"Error deleting content(s): {e}")
        raise HTTPException(status_code=500, detail=str(e))