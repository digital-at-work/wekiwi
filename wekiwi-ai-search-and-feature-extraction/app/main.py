# Made open source under the GNU Affero General Public License, Version 3 (AGPL-3.0),
# by digital@work GmbH (2024). This file is part of wekiwi.
# See the LICENSE file in the project root or https://www.gnu.org/licenses/agpl-3.0.html for details.

import uvicorn
import contextlib

from concurrent.futures import ProcessPoolExecutor

from fastapi import FastAPI, APIRouter, Depends

from .api.v1.content import content, search
from .api.v1.content.text import rerank, caption

from .internal.utils.logging import init_logging, log_requests_and_responses
from .internal.errors import (
    CircleNotFound,
    CompanyNotFound,
    ContentNotFound,
    UserNotFound,
)

from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend

from .internal.utils.logging import logger

from .config import DEBUG, HOST, PORT, LOG_LEVEL

from .api.authentication import check_authentication

# from .internal.postgresdb import PostgresClientPool
# from .config import POSTGRES_DB_NAME, POSTGRES_DB_HOST, POSTGRES_DB_PORT

from .internal.milvusdb import MilvusClient
from .config import (
    # MILVUS_DB_NAME,
    MILVUS_DB_HOST,
    MILVUS_DB_PORT,
)

from .internal.directus import DirectusClient
from .config import DIRECTUS_URL, DIRECTUS_ADMIN_KEY

from .internal.processor import TextRequestProcessor
from .config import REQUEST_FLUSH_TIMEOUT, ACCUMLATION_TIMEOUT

from .internal.models import BGEM3Wrapper
from .config import (
    BGEM3_EMBEDDING_MODEL,
    BGEM3_EMBEDDING_DEVICE,
    BGEM3_EMBEDDING_FP16,
    BGEM3_EMBEDDING_MAX_LENGTH,
    BGEM3_EMBEDDING_MAX_QUERY_LENGTH,
    BGEM3_EMBEDDING_BATCH_SIZE,
    BGEM3_RERAANK_WEIGHTS,
)

from .internal.models import BGEReRankWrapper
from .config import (
    BGE_RERANKING_MODEL,
    RERANKING_DEVICE,
    BGE_RERANKING_FP16,
)

from .internal.models import SentenceTransformerWrapper
from .config import (
    SENTENCE_TRANSFORMERS_EMBEDDING_MODEL,
    SENTENCE_TRANSFORMERS_DEVICE,
    SENTENCE_TRANSFORMERS_FP16,
    SENTENCE_TRANSFORMERS_BATCH_SIZE,
)


@contextlib.asynccontextmanager
async def lifespan(application: FastAPI):
    init_logging(LOG_LEVEL)

    # Create connections

    # postgrespool = await PostgresClientPool() # Not used for now
    
    FastAPICache.init(InMemoryBackend())

    milvusdbclient = await MilvusClient(
        MILVUS_DB_HOST, MILVUS_DB_PORT,  # , MILVUS_DB_NAME
    )

    directusclient = DirectusClient(DIRECTUS_URL, DIRECTUS_ADMIN_KEY)

    # Load models
    txt_emb_model = SentenceTransformerWrapper(
        SENTENCE_TRANSFORMERS_EMBEDDING_MODEL,
        SENTENCE_TRANSFORMERS_DEVICE,
        SENTENCE_TRANSFORMERS_FP16,
        SENTENCE_TRANSFORMERS_BATCH_SIZE,
    )
    logger.info(f"SentenceTransformerWrapper loaded")

    txt_emb_model1 = BGEM3Wrapper(
        BGEM3_EMBEDDING_MODEL,
        BGEM3_EMBEDDING_DEVICE,
        BGEM3_EMBEDDING_FP16,
        BGEM3_EMBEDDING_BATCH_SIZE,
        BGEM3_EMBEDDING_MAX_LENGTH,
        BGEM3_EMBEDDING_MAX_QUERY_LENGTH,
        BGEM3_RERAANK_WEIGHTS,
    )
    logger.info(f"BGEM3Wrapper loaded")

    txt_reranker_model = BGEReRankWrapper(
        BGE_RERANKING_MODEL,
        RERANKING_DEVICE,
        BGE_RERANKING_FP16,
        BGEM3_EMBEDDING_BATCH_SIZE,
        BGEM3_EMBEDDING_MAX_LENGTH,
    )
    logger.info(f"BGEReRankWrapper loaded")
    
    # Create and start request processors for each model
    textrequestProcessor = await TextRequestProcessor(
        txt_emb_model, REQUEST_FLUSH_TIMEOUT, ACCUMLATION_TIMEOUT
    )

    textrequestProcessor1 = await TextRequestProcessor(
        txt_emb_model1, REQUEST_FLUSH_TIMEOUT, ACCUMLATION_TIMEOUT
    )

    textrerankingProcessor = await TextRequestProcessor(
        txt_reranker_model, REQUEST_FLUSH_TIMEOUT, ACCUMLATION_TIMEOUT
    )

    yield {
        # "postgrespool": postgrespool,
        "milvusdbclient": milvusdbclient,
        "directusclient": directusclient,
        "txt_emb_model": txt_emb_model,
        "txt_emb_model1": txt_emb_model1,
        "textrequestProcessor": textrequestProcessor,
        "textrequestProcessor1": textrequestProcessor1,
        "textrerankingProcessor": textrerankingProcessor,
    }
    
    # with ProcessPoolExecutor(max_workers=3) as executor:

    #     # Create and start request processors for each model
    #     textrequestProcessor = TextRequestProcessor(
    #         txt_emb_model, REQUEST_FLUSH_TIMEOUT, ACCUMLATION_TIMEOUT
    #     )
    #     executor.submit(textrequestProcessor.run)

    #     textrequestProcessor1 = TextRequestProcessor(
    #         txt_emb_model1, REQUEST_FLUSH_TIMEOUT, ACCUMLATION_TIMEOUT
    #     )
    #     executor.submit(textrequestProcessor1.run)

    #     textrerankingProcessor = TextRequestProcessor(
    #         txt_reranker_model, REQUEST_FLUSH_TIMEOUT, ACCUMLATION_TIMEOUT
    #     )
    #     executor.submit(textrerankingProcessor.run)

    #     yield {
    #         # "postgrespool": postgrespool,
    #         "milvusdbclient": milvusdbclient,
    #         "directusclient": directusclient,
    #         "txt_emb_model": txt_emb_model,
    #         "txt_emb_model1": txt_emb_model1,
    #         "textrequestProcessor": textrequestProcessor,
    #         "textrequestProcessor1": textrequestProcessor1,
    #         "textrerankingProcessor": textrerankingProcessor,
    #     }

    # Close connections
    # await postgrespool.close_pool()
    await milvusdbclient.disconnect()


title = """Wekiwi API - search and feature extraction"""

description = """This is the Wekiwi API, which provides endpoints for embeddings, vector search content and re-ranking text."""


app = FastAPI(lifespan=lifespan, version="0.0.1", title=title, description=description)

app.middleware("http")(log_requests_and_responses)

@app.get("/health")
def health_check():
    logger.info("Health check")
    return {"status": "healthy"}


app.include_router(
    content.router,
    tags=["Manage embeddings and content"],
    dependencies=[Depends(check_authentication)],
)

app.include_router(
    search.router,
    tags=["Search"],
    dependencies=[Depends(check_authentication)],
)

app.include_router(
    caption.router,
    tags=["Text"],
    dependencies=[Depends(check_authentication)],
)

app.include_router(
    rerank.router,
    tags=["Text"],
    dependencies=[Depends(check_authentication)],
)

router = APIRouter()


def main():
    logger.info(f"Starting server on {HOST}:{PORT} {__name__}:app")
    uvicorn.run(app=__name__ + ":app", reload=DEBUG, host=HOST, port=PORT)
    
    ## this logs: "Starting server on 0.0.0.0:8000 app.main:app"
    ## this file is /app/main.py


if __name__ == "__main__":
    main()
