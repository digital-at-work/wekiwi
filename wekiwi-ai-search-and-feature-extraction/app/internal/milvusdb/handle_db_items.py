# Made open source under the GNU Affero General Public License, Version 3 (AGPL-3.0),
# by digital@work GmbH (2024). This file is part of wekiwi.
# See the LICENSE file in the project root or https://www.gnu.org/licenses/agpl-3.0.html for details.

import httpx

import asyncio
import re

from fastapi import Request, BackgroundTasks
from typing import List
from loguru import logger

from app.internal.types import ContentValidated, ContentOptional
from app.internal.utils.text_splitter import text_splitter
from app.internal.utils.sanitize_text import sanitize_text

from app.internal.utils.generate_title import generate_german_title


async def create_content_chunks(
    request: Request,
    background_tasks: BackgroundTasks,
    content: ContentValidated,
    company_id: str = None,
    circle_ids: List[str] = None    
) -> list[dict]:
    """Creates or updates database items with optional text and title embeddings."""
    
    # Split text into chunks
    if re.match(r'^\s*$', content.text):
        text_chunks = [""]
    else:
        document_chunks = text_splitter(sanitize_text(content.text))
        text_chunks = [doc.page_content for doc in document_chunks]      
        
    # Generate title if not provided
    # TODO: perform this step in parallel with text embedding
    if re.match(r'^\s*$', content.title):
        title = content.title  
    else:
        try: 
            title = await generate_german_title(content.text)
        except httpx.HTTPError as e:
            logger.error(f"Error generating title for content ID {content.content_id}: {e}")
            title = ""  # fallback title
        background_tasks.add_task(request.state.directusclient.update_item, "contents", content.content_id, {"title": title}) 

    logger.info(f"Processing content_id: {content.content_id} text chunks: {len(text_chunks)}, title: {title}") 

    # Create embedding tasks
    embedding_tasks = [
        request.state.textrequestProcessor.process_request(title, "embed"),  # Title embedding
    ]
    
    for chunk in text_chunks:
        embedding_tasks.append(request.state.textrequestProcessor.process_request(chunk, "embed"))  # Dense
        embedding_tasks.append(request.state.textrequestProcessor1.process_request(chunk, "embed"))  # Sparse

    # Gather and process ALL embedding results using a single asyncio.gather
    embedding_results = await asyncio.gather(*embedding_tasks)

    title_embedding_dense = embedding_results[0]  # First result is title embedding

    # Separate dense and sparse embeddings
    text_embeddings_dense = embedding_results[1::2]  # Every other result starting from the second
    text_embeddings_sparse = embedding_results[2::2]  # Every other result starting from the third

    # Create list of content chunks
    items = []
    for index, chunk in enumerate(text_chunks):
        item = {
            **content.model_dump(),
            "text": chunk,
            "company_id": company_id,
            "circle_ids": circle_ids,
            "title_embedding_dense": title_embedding_dense.result(),
            "text_embedding_dense": text_embeddings_dense[index].result(), 
            "text_embedding_sparse": text_embeddings_sparse[index].result() or {0:0.0},  
        }
        items.append(item)

    return items
    
async def update_content_chunks(
    request: Request,
    content: ContentOptional,
    content_chunks: List[dict],
    company_id: str | None = None,
    circle_ids: List[str] | None = None,
) -> list[dict]:
    """Updates database items with optional text and title embeddings."""

    embedding_tasks = []
    text_embeddings_dense = []
    text_embeddings_sparse = []

    if not content.text or re.match(r'^\s*$', content.text):
        # Reuse existing text chunks and extract embeddings with a single loop
        text_chunks = []
        for chunk in content_chunks:
            text_chunks.append(chunk["text"])
            text_embeddings_dense.append(chunk.get("text_embedding_dense"))
            text_embeddings_sparse.append(chunk.get("text_embedding_sparse"))
    else:
        # Text chunks need to be re-created and embedded
        document_chunks = text_splitter(sanitize_text(content.text))
        text_chunks = [doc.page_content for doc in document_chunks] 
        
        logger.info(f"Re-creating and processing text chunks.")

        # Create dense and sparse embedding tasks
        for chunk in text_chunks:
            embedding_tasks.append(request.state.textrequestProcessor.process_request(chunk, "embed"))
            embedding_tasks.append(request.state.textrequestProcessor1.process_request(chunk, "embed"))


    # Create title embedding task only if content.title is provided
    if content.title:
        embedding_tasks.append(request.state.textrequestProcessor.process_request(content.title, "embed"))

    # Execute all gathered embedding tasks concurrently
    embedding_results = await asyncio.gather(*embedding_tasks)

    # Extract title embedding (if generated)
    title_embedding = embedding_results.pop(0).result() if content.title else content_chunks[0].get("title_embedding_dense")

    # If text embedding were generated, extract them
    if content.text:
        text_embeddings_dense = [res.result() for res in embedding_results[1::2]]
        text_embeddings_sparse = [res.result() for res in embedding_results[::2]]

    # Create list of content chunks
    items = []
    for index, chunk in enumerate(text_chunks):
        item = {
            **content_chunks[index],
            **content.model_dump(exclude_none=True), #, exclude=["company_id", "circle_ids"]
            "text": chunk,
            "title_embedding_dense": title_embedding,
            "text_embedding_dense": text_embeddings_dense[index],
            "text_embedding_sparse": text_embeddings_sparse[index] or {0:0.0},
        }
        item.pop("id", None) # Remove id (auto-generated by MilvusDB)
        
        if company_id:
            item["company_id"] = company_id
        if circle_ids:
            item["circle_ids"] = circle_ids
        
        items.append(item)

    return items
    