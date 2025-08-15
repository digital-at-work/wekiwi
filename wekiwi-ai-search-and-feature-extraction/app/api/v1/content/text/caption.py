# Made open source under the GNU Affero General Public License, Version 3 (AGPL-3.0),
# by digital@work GmbH (2024). This file is part of wekiwi.
# See the LICENSE file in the project root or https://www.gnu.org/licenses/agpl-3.0.html for details.

from fastapi import APIRouter, HTTPException, Body
from loguru import logger
from typing import Annotated

from app.internal.utils.text_splitter import text_splitter
from app.internal.utils.generate_title import generate_german_title



router = APIRouter()

@router.post(
    "/v1/text/caption",
    response_model=str,
    summary="Generates a german caption / title for a given text.",
)
async def rerank(
    text: Annotated[str, Body()],
):
    try:
        return await generate_german_title(text)

    except Exception as e:
        logger.error(f"Error when generating title: {e}")
        raise HTTPException(status_code=500, detail=str(e))