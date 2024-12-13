# Made open source under the GNU Affero General Public License, Version 3 (AGPL-3.0),
# by digital@work GmbH (2024). This file is part of wekiwi.
# See the LICENSE file in the project root or https://www.gnu.org/licenses/agpl-3.0.html for details.

from fastapi import APIRouter, HTTPException, Request, Body
from typing import List, Union
from pydantic import BaseModel
from loguru import logger
from typing import Annotated

from app.internal.utils.text_splitter import text_splitter

from app.config import BGE_RERANKING_MAX_LENGTH


router = APIRouter()


class PartialContent(BaseModel):
    content_id: int
    text: str

class PartialContentWithScore(PartialContent):
    score: float

class RankingReponse(BaseModel):
    result: Union[List[PartialContentWithScore], List[List[PartialContentWithScore]]]


@router.post(
    "/v1/text/rerank",
    response_model=RankingReponse,
    summary="Re-rank contents according to the relevance to a given query",
)
async def rerank(
    request: Request,
    query: Annotated[str, Body()],
    contents: Annotated[List[PartialContent], Body()]
):
    try:
        processed_contents = []
        content_mapping = {}  # Map split content indices to original content indices

        for i, content in enumerate(contents):
            if len(content.text) > BGE_RERANKING_MAX_LENGTH:
                split_texts = text_splitter(content.text)
                for text in split_texts:
                    processed_contents.append((query, text))  # Add (query, text) tuple
                    content_mapping[len(processed_contents) - 1] = i
            else:
                processed_contents.append((query, content.text))  # Add (query, text) tuple
                content_mapping[len(processed_contents) - 1] = i

        # Process all contents in a single batch
        scores = await request.state.textrerankingProcessor.process_request(
            processed_contents, "rerank" 
        )

        # Aggregate scores for split contents
        aggregated_scores = {}
        for i, score in enumerate(scores):
            original_index = content_mapping[i]
            aggregated_scores.setdefault(original_index, []).append(score)

        results = [
            PartialContentWithScore(
                content=content,
                score=sum(aggregated_scores.get(i, [0])) / len(aggregated_scores.get(i, [1])),
            )
            for i, content in enumerate(contents)
        ]

        return RankingReponse(result=results)

    except Exception as e:
        logger.error(f"Error while re-ranking: {e}")
        raise HTTPException(status_code=500, detail=str(e))