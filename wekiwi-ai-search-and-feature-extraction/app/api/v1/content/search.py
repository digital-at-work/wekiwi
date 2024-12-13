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
    try:
        logger.info(f"Received search request with query: {query}")

        # Embed search query with multiple models (cache for 5 Minutes)
        @cache(expire=300)
        async def get_embedded_query(query):
            embedded_query_dense, embedded_query_sparse = await asyncio.gather(
                request.state.textrequestProcessor.process_request(query, "embed"),
                request.state.textrequestProcessor1.process_request(query, "embed"),
            )
            return embedded_query_dense, embedded_query_sparse

        embedded_query_dense, embedded_query_sparse = await get_embedded_query(query)

        # Get vector search result
        # TODO: add support for multiple queries, once directus supports it, also see zero index below
        search_result = await request.state.milvusdbclient.multi_vector_search(
            vectors=[embedded_query_dense.result(), embedded_query_dense.result(), embedded_query_sparse.result()],
            field_names=[
                "title_embedding_dense",
                "text_embedding_dense",
                "text_embedding_sparse"
            ],
            filter_expr=f"company_id == {company_id} and ARRAY_CONTAINS_ANY(circle_ids, {circle_ids}) {f"and {filter}" if filter else ''}",
            offset=offset,
            page_size=page_size
        )
        
        logger.debug(f"search_results: {search_result}")
        
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
            rerank_results = [future.result() for future in rerank_futures]
            # Use rerank_results
            score_lf = pl.LazyFrame({
                "content_id": ids,
                "score": rerank_results # assumes that re-ranking scores are allways more accurate
                })
        else:
            # Use search_result
            score_lf = pl.LazyFrame({
                "score_lf": ids,
                "score": search_distances})
            
        combined_df = await run_in_threadpool(calculate_combined_df, score_lf, contents, k_avg)
        hierarchy = await run_in_threadpool(build_hierarchy, combined_df)
        
        return hierarchy

    except Exception as e:
        logger.error(f"Error in search: {e}")
        raise HTTPException(status_code=500, detail=str(e))
