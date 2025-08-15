# Made open source under the GNU Affero General Public License, Version 3 (AGPL-3.0),
# by digital@work GmbH (2024). This file is part of wekiwi.
# See the LICENSE file in the project root or https://www.gnu.org/licenses/agpl-3.0.html for details.

from fastapi import APIRouter, HTTPException, Request, Body
from typing import Annotated, List, Union
from loguru import logger

from fastapi_cache.decorator import cache

from starlette.concurrency import run_in_threadpool

import polars as pl
import asyncio

from app.internal.utils.search_postprocessing import calculate_combined_df, build_hierarchy


router = APIRouter()


@router.post(
    "/v1/content/search",
    #response_model=Union[List[ContentResponse], List],
    summary="Receives a query and responds with a hierarchy of content items."
)
async def search(
    request: Request,
    query: Annotated[str, Body(min_length=1, max_length=256, description="Text query")],
    company_id: Annotated[
        int, Body(ge=0, description="Company_id of the user making the search.")
    ],
    circle_ids: Annotated[List[int], Body(description="Circle_id(s) that the user has access to.")],
    rerank: Annotated[
        bool, Body(description="Whether to re-rank the search results. Defaults to True.")
    ] = True,
    offset: Annotated[int | None, Body(description="Offset content number. Defaults to 0.")] = 0,
    page_size: Annotated[
        int, Body(ge=1, description="Number of results per page. Defaults to value in config.")
    ] = 20,
    filter: Annotated[
        Union[None, str],
        Body(
            examples=[None],
            description="MilvusDB filter expressions, see https://milvus.io/docs/boolean.md"
        ),
    ] = None,
    k_avg: Annotated[
        int,
        Body(
            gt=0,
            description="Number of highest scoring chunks with duplicate ids to average. Defaults to 2."
        ),
    ] = 2,
):
    logger.info(f"Entering search function for query: {query}") # Log entry
    try:
        logger.info(f"Received search request with query: {query}")

        # Embed search query with multiple models (Caching disabled due to type errors)
        async def get_embedded_query(query):
            # No internal logging needed now
            try:
                embedded_query_dense_future, embedded_query_sparse_future = await asyncio.gather(
                    request.state.textrequestProcessor.process_request(query, "embed"),
                    request.state.textrequestProcessor1.process_request(query, "embed"),
                )
                # Extract and return the actual vector values
                dense_vector = embedded_query_dense_future.result() if hasattr(embedded_query_dense_future, 'result') and callable(embedded_query_dense_future.result) else embedded_query_dense_future
                dense_vector = dense_vector.result() if hasattr(dense_vector, 'result') and callable(dense_vector.result) else dense_vector

                sparse_vector = embedded_query_sparse_future.result() if hasattr(embedded_query_sparse_future, 'result') and callable(embedded_query_sparse_future.result) else embedded_query_sparse_future
                sparse_vector = sparse_vector.result() if hasattr(sparse_vector, 'result') and callable(sparse_vector.result) else sparse_vector

                return dense_vector, sparse_vector
            except Exception as embed_e:
                # Log error if embedding fails
                logger.error(f"Error during query embedding: Type={type(embed_e).__name__}, Message={str(embed_e)}")
                raise # Re-raise the exception

        dense_vector, sparse_vector = await get_embedded_query(query)
        # Removed debug logs about return types and preparation

        # Get vector search result
        # TODO: add support for multiple queries, once directus supports it, also see zero index below
        # Removed specific try/except around this call, outer one is sufficient
        search_result = await request.state.milvusdbclient.multi_vector_search(
            vectors=[
                dense_vector,
                dense_vector, # Corrected indentation
                sparse_vector
            ],
            field_names=[
                "title_embedding_dense",
                "text_embedding_dense",
                "text_embedding_sparse"
            ],
            filter_expr=f"company_id == {company_id} and ARRAY_CONTAINS_ANY(circle_ids, {circle_ids}) {f'and {filter}' if filter else ''}",
            offset=offset, # Corrected indentation
        )
        logger.debug(f"multi_vector_search completed.") # Corrected indentation

        # Removed specific try/except block
        # Removed logs about result types

        # If no search results, return empty list
        if len(search_result[0]) == 0:
            return []

        query_chunk_pairs = [] # Chunk pairs for possible re-rank and get ids for directus request
        search_distances = [] # Distances are used later if re-ranking is not enabled
        ids = [] # IDs to get additional content from Directus

        for hit in search_result[0]: # zero index for zeroth query
            query_chunk_pairs.append((query, hit.fields["text"]))
            ids.append(hit.fields["content_id"])
            search_distances.append(hit.distance)
        
        if rerank:
            # Re-rank chunks (optional) and get additional contents from Directus
            rerank_tasks = [
                request.state.textrerankingProcessor.process_request(pair, "rerank")
                for pair in query_chunk_pairs
            ]

            contents, *rerank_futures = await asyncio.gather(
                request.state.directusclient.get_contents(content_ids=ids, company_id=company_id),
                *rerank_tasks
            )
        else:
            # Only get additional contents from Directus (without re-ranking)
            contents = await request.state.directusclient.get_contents(content_ids=ids, company_id=company_id)
        
        if rerank:
            # Convert results to float to ensure compatibility with Polars
            # Note: If future.result() can return None, float() will raise an error.
            # Consider adding error handling/filtering if None is a possible valid result.
            try:
                rerank_results_float = [float(future.result()) for future in rerank_futures]
            except TypeError as e:
                logger.error(f"TypeError converting rerank_results to float: {e}. Original results: {rerank_futures}")
                raise # Re-raise the error to stop processing
            # Removed debug logs
            # logger.debug(f"ids: {ids}")
            # logger.debug(f"rerank_results (float): {rerank_results_float}")

            # Use rerank_results
            score_lf = pl.LazyFrame({
                "content_id": ids,
                "score": rerank_results_float # Use the converted float list
                })
        else:
            # Removed debug logs
            # logger.debug(f"ids: {ids}")
            # logger.debug(f"search_distances: {search_distances}")

            # Convert distances to float and use correct key for LazyFrame
            # Note: If hit.distance can be None, float() will raise an error.
            try:
                search_distances_float = [float(dist) for dist in search_distances]
            except TypeError as e:
                 logger.error(f"TypeError converting search_distances to float: {e}. Original distances: {search_distances}")
                 raise # Re-raise the error to stop processing
            # logger.debug(f"search_distances (float): {search_distances_float}") # Removed debug log

            # Use search_result with corrected key and float types
            score_lf = pl.LazyFrame({
                "content_id": ids, # Corrected key from "score_lf"
                "score": search_distances_float # Use the converted float list
                 })

        # Removed schema log that caused PerformanceWarning
        # logger.debug(f"Schema of score_lf before post-processing: {score_lf.schema}")

        combined_df = await run_in_threadpool(calculate_combined_df, score_lf, contents, k_avg)
        hierarchy = await run_in_threadpool(build_hierarchy, combined_df)

        return hierarchy

    except Exception as e:
        # Log type and message separately for safer handling
        logger.error(f"Error in search: Type={type(e).__name__}, Message={str(e)}")
        # Optionally include traceback for more debugging info (if needed)
        # import traceback
        # logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
