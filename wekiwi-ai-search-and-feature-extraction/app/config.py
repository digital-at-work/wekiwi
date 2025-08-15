# Made open source under the GNU Affero General Public License, Version 3 (AGPL-3.0),
# by digital@work GmbH (2024). This file is part of wekiwi.
# See the LICENSE file in the project root or https://www.gnu.org/licenses/agpl-3.0.html for details.

from pathlib import Path
from starlette.config import Config


### Configuration ###
## See Dockerfile for ENV variables ##

try:
    config = Config(Path("./").parent / ".env")
except FileNotFoundError:
    config = Config()

# General
DEBUG = config.get("DEBUG", cast=bool, default=False)
HOST = config.get("HOST", default="0.0.0.0")
PORT = config.get("PORT", cast=int, default="8000")
ENV = config.get("ENV", default="dev")
API_SECRET = config.get("API_SECRET")
LOG_LEVEL = config.get("LOG_LEVEL", default="INFO")

REQUEST_FLUSH_TIMEOUT = config.get("REQUEST_FLUSH_TIMEOUT", default=0.15)
ACCUMLATION_TIMEOUT = config.get("ACCUMLATION_TIMEOUT", default=0.15)

POSTGRES_DB_NAME = config.get("POSTGRES_DB_NAME", default="app")
POSTGRES_DB_USER = config.get("POSTGRES_DB_USER")
POSTGRES_DB_PASSWORD = config.get("POSTGRES_DB_PASSWORD")
POSTGRES_DB_HOST = config.get("POSTGRES_DB_HOST", default="db")
POSTGRES_DB_PORT = config.get("POSTGRES_DB_PORT", default=5432)

MILVUS_DB_NAME = config.get("MILVUS_DB_NAME", default="default")
MILVUS_DB_HOST = config.get("MILVUSDB_HOST", default="localhost")
MILVUS_DB_PORT = config.get("MILVUSDB_PORT", default=19530)

# Sentence Transformers model (Huggingface integration)
SENTENCE_TRANSFORMERS_EMBEDDING_MODEL = config.get("SENTENCE_TRANSFORMERS_EMBEDDING_MODEL", default="jinaai/jina-embeddings-v2-base-de")
SENTENCE_TRANSFORMERS_DEVICE = config.get("SENTENCE_TRANSFORMERS_EMBEDDING_DEVICE", default="cpu")
SENTENCE_TRANSFORMERS_BATCH_SIZE = config.get("SENTENCE_TRANSFORMERS_EMBEDDING_BATCH_SIZE", default=2)
SENTENCE_TRANSFORMERS_FP16 = config.get("SENTENCE_TRANSFORMERS_EMBEDDING_PRECISION", default=False)
SENTENCE_TRANSFORMERS_MAX_LENGTH = config.get("SENTENCE_TRANSFORMERS_MAX_LENGTH", default=512)
SENTENCE_TRANSFORMERS_MAX_QUERY_LENGTH = config.get("SENTENCE_TRANSFORMERS_MAXQ_LENGTH", default=256)

# BGEM3 model (BGEM3FlagModel integration)
BGEM3_EMBEDDING_MODEL = config.get("BGEM3_EMBEDDING_MODEL", default="BAAI/bge-m3")
BGEM3_EMBEDDING_DEVICE = config.get("BGEM3_EMBEDDING_DEVICE", default="cpu")
BGEM3_EMBEDDING_BATCH_SIZE = config.get("BGEM3_EMBEDDING_BATCH_SIZE", default=2)
BGEM3_EMBEDDING_FP16 = config.get("BGEM3_EMBEDDING_PRECISION", default=False)
BGEM3_EMBEDDING_MAX_LENGTH = config.get("BGEM3_EMBEDDING_MAXQ_LENGTH", default=512)
BGEM3_EMBEDDING_MAX_QUERY_LENGTH = config.get("BGEM3_EMBEDDING_MAXQ_LENGTH", default=256)
BGEM3_RERAANK_WEIGHTS = config.get("BGEM3_RERANK_WEIGHTS", default=[0.4, 0.2, 0.4])

# BGEM3 model (FlagReranker integration)
BGE_RERANKING_MODEL = config.get("BGE_RERANKING_MODEL", default="BAAI/bge-reranker-v2-m3")
RERANKING_DEVICE = config.get("RERANKING_DEVICE", default="cpu")
BGE_RERANKING_FP16 = config.get("BGE_RERANKING_FP16", default=False)
BGE_RERANKING_BATCH_SIZE = config.get("BGE_RERANKING_BATCH_SIZE", default=2)
BGE_RERANKING_MAX_LENGTH = config.get("BGE_RERANKING_MAX_LENGTH", default=1024)

# General model configuration
BATCH_SIZE = config.get("BATCH_SIZE", default=2)
MAX_REQUEST = config.get("MAX_REQUEST", default=10)
MAX_LENGTH = config.get("MAX_LENGTH", default=5000)
REQUEST_TIME_OUT = config.get("REQUEST_TIME_OUT", default=30)

# Re-ranker model (ColBERT)
RERANKER_MODEL = config.get("RERANKER_MODEL", default="bert-base-uncased")
RERANKER_DEVICE = config.get("RERANKER_DEVICE", default="cpu")
RERANKER_FP16 = config.get("RERANKER_FP16", default=False)
RERANKER_MODE = config.get("RERANKER_MODE", default="query")
RERANKER_WEIGHTS = config.get("RERANKER_WEIGHTS", default=[0.4, 0.2, 0.4])
RERANKER_MAXQ_LENGTH = config.get("RERANKER_MAXQ_LENGTH", default=256)
RERANKER_REQUEST_FLUSH_TIMEOUT = config.get("RERANKER_REQUEST_FLUSH_TIMEOUT", default=0.1)

# Directus API Configuration
DIRECTUS_URL = config.get("DIRECTUS_URL", default="https://your-default.de")
DIRECTUS_ADMIN_KEY = config.get("DIRECTUS_ADMIN_KEY")

# Ollama API Configuration
OLLAMA_API_URL = config.get("OLLAMA_API_URL", default="http://ollama:11434/api/generate")
OLLAMA_TITLE_MODEL = config.get("OLLAMA_TITLE_MODEL", default="gemma3")

# DAW API Hub (External PDF Conversion Service) Configuration
DAW_API_HUB_URL = config.get("DAW_API_HUB_URL", default="http://daw-api-hub:6100") # Default from your compose override
DAW_HUB_KEY = config.get("DAW_HUB_KEY") # No default, should be set in docker-compose.override.yml

# Swagger UI Direct Upload Service API Key
SWAGGERSERVICE_API_KEY = config.get("SWAGGERSERVICE_API_KEY") # No default, should be set in docker-compose.override.yml
