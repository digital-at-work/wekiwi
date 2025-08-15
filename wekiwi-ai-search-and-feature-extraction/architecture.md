## Wekiwi AI Search and Feature Extraction

### Overview
Wekiwi AI Search is an advanced retrieval and feature extraction system designed to process and analyze large volumes of data efficiently. The system integrates multiple AI-driven components to enable high-precision information retrieval, similarity search, and structured feature extraction.

### Core Functionality
- **Search & Retrieval**: The system allows users to perform searches using natural language queries, leveraging embedding-based similarity search and traditional keyword search.
- **Feature Extraction**: Extracts key entities, relations, and structured data from unstructured documents.
- **RAG (Retrieval-Augmented Generation)**: Enhances AI-generated responses by incorporating retrieved data from internal knowledge bases.
- **Vector Database Integration**: Stores and queries dense vector representations of documents for efficient similarity search.
- **Multi-Model AI Processing**: Supports various AI models for embeddings, search optimization, and response generation.

### System Components & Code References
- **Vector Database Storage**: Uses MilvusDB for storing and querying embeddings.
  - *Code Location:* `milvus.yaml`
- **Search Query Processing**: Handles user queries, normalizes inputs, and interfaces with vector and keyword search.
  - *Code Location:* `/app/api/v1/content/search.py`
- **Content Management API**: Handles creation, updating, deletion, and rebuilding of content chunks.
  - *Code Location:* `/app/api/v1/content/content.py`
- **Text Captioning**: Generates German titles for provided text content.
  - *Code Location:* `/app/api/v1/content/text/caption.py`
- **Re-Ranking Service**: Re-ranks content search results based on relevance to a given query.
  - *Code Location:* `/app/api/v1/content/text/rerank.py`
- **Authentication Service**: Implements API authentication using bearer token security.
  - *Code Location:* `/app/api/authentication.py`
- **Directus Integration**: Handles interactions with the Directus CMS for content retrieval and metadata.
  - *Code Location:* `/app/internal/directus/directus.py`
- **Model Implementations**: Handles embeddings and re-ranking models.
  - *Code Location:* `/app/internal/models.py`
- **Processing Pipelines**: Manages request batching and execution for embedding and re-ranking models.
  - *Code Location:* `/app/internal/processor.py`
- **Configuration Management**: Manages environment variables and model settings.
  - *Code Location:* `/app/config.py`
- **Milvus Database Client**: Handles MilvusDB connection, storage, and search operations.
  - *Code Location:* `/app/internal/milvusdb.py`
- **Milvus Database Operations**: Processes content chunk storage, updates, and retrieval in Milvus.
  - *Code Location:* `/app/internal/milvusdb/handle_db_items.py`
- **PostgreSQL Database Client**: Manages connection pooling and query execution for PostgreSQL.
  - *Code Location:* `/app/internal/postgresdb/postgresdb.py`
- **Data Types and Validation**: Defines core data models for search and content management.
  - *Code Location:* `/app/internal/types.py`
- **Title Generation Utility**: Generates German titles for content using an external API.
  - *Code Location:* `/app/internal/utils/generate_title.py`
- **Search Postprocessing**: Builds hierarchical search results and calculates scores.
  - *Code Location:* `/app/internal/utils/search_postprocessing.py`
- **Text Sanitization**: Cleans and processes text data for improved search accuracy.
  - *Code Location:* `/app/internal/utils/sanitize_text.py`
- **Text Splitting Utility**: Splits long text into structured chunks for processing.
  - *Code Location:* `/app/internal/utils/text_splitter.py`
- **Application Entry Point**: FastAPI app initialization and model loading.
  - *Code Location:* `app/main.py`

### Infrastructure and Deployment
Wekiwi AI Search is deployed using Docker and orchestrated via `docker-compose` for production. The core infrastructure components include:

#### **Milvus Vector Database**
- **Service Name**: `milvus`
- **Image**: `milvusdb/milvus:v2.4.5`
- **Dependencies**:
  - Uses `etcd` for metadata storage.
  - Uses `minio` for distributed object storage.
- **Configuration**:
  - Stores vectorized data for efficient similarity searches.
  - Accessible via port `19530`.
  - Healthcheck endpoint: `http://localhost:9091/healthz`.

#### **ETCD Metadata Storage**
- **Service Name**: `etcd`
- **Image**: `quay.io/coreos/etcd:v3.5.5`
- **Functionality**:
  - Manages metadata for MilvusDB.
  - Ensures consistency and high availability of stored indexes.
- **Healthcheck**: `etcdctl endpoint health`.

#### **MinIO Object Storage**
- **Service Name**: `minio`
- **Image**: `minio/minio:RELEASE.2023-03-20T20-16-18Z`
- **Functionality**:
  - Stores and manages large files required by Milvus.
  - Accessible via ports `9000` (API) and `9001` (console UI).
- **Healthcheck**: `http://localhost:9000/minio/health/live`.

#### **Attu Dashboard**
- **Service Name**: `attu`
- **Image**: `zilliz/attu:v2.4.3`
- **Functionality**:
  - Web-based UI for monitoring and managing MilvusDB.
  - Accessible via port `8042`.

### **Application Deployment**
- **Service Name**: `wekiwi-ai-search-and-feature-extraction`
- **Image**: `digitalatwork/wekiwi-ai-search-and-feature-extraction:v1_5-cuda`
- **Environment Variables**:
  - `DIRECTUS_ADMIN_KEY`: API key for Directus integration.
  - `DIRECTUS_URL`: `https://cms.wekiwi.de`
  - `API_SECRET`: Used for securing internal API communications.
  - `MILVUSDB_HOST`: Milvus connection inside the container.
  - `POSTGRES_DB_NAME`: `contents`
  - `POSTGRES_DB_USER`: `admin`
  - `POSTGRES_DB_PASSWORD`: `admin`
- **Healthcheck Endpoint**: `http://localhost:8000/health`
- **Exposed Port**: `8058:8000`

### Integration with Other Systems
- **Directus CMS**: Uses Directus as a structured content management system.
- **PostgreSQL Database**: Stores structured data and query logs.
- **FastAPI Backend**: Provides API interfaces for search and retrieval.
- **Docker Deployment**: Containerized deployment for scalability and ease of management.
- **CI/CD Pipeline**: Automates testing and deployment.