# Made open source under the GNU Affero General Public License, Version 3 (AGPL-3.0),
# by digital@work GmbH (2024). This file is part of wekiwi.
# See the LICENSE file in the project root or https://www.gnu.org/licenses/agpl-3.0.html for details.

from pymilvus import (
    MilvusClient as BaseMilvusClient,
    AnnSearchRequest,
    WeightedRanker,
    RRFRanker,
    CollectionSchema,
    FieldSchema,
    DataType,
    connections,
    Collection
)
from loguru import logger

_MAX_LENGTH_TEXT = 20480
_MAX_LENGTH_TITLE = 368

_CONTENT_COLLECTION_NAME = "contents"

_COLLECTION_SCHEMA = CollectionSchema(
    auto_id=True,
    enable_dynamic_field=False,
    fields=[
        FieldSchema(name="company_id", dtype=DataType.INT64, is_partition_key=True),
        FieldSchema(
            name="id",
            dtype=DataType.INT64,
            is_primary=True,  # milvus primary key
            auto_id=True,
        ),
        FieldSchema(
            name="content_id",##
            dtype=DataType.INT32,
        ),
        FieldSchema(name="content_type", dtype=DataType.VARCHAR, max_length=24),
        FieldSchema(
            name="title",##
            dtype=DataType.VARCHAR,
            max_length=_MAX_LENGTH_TITLE,
        ),
        FieldSchema(
            name="text",##
            dtype=DataType.VARCHAR,
            max_length=_MAX_LENGTH_TEXT,
        ),
        FieldSchema(
            name="summary",##
            dtype=DataType.VARCHAR,
            max_length=_MAX_LENGTH_TEXT,
        ),
        FieldSchema(name="file_id", dtype=DataType.VARCHAR, max_length=36),#
        FieldSchema(
            name="circle_ids",
            dtype=DataType.ARRAY,
            element_type=DataType.INT32,
            max_capacity=8,
        ),##
        FieldSchema(
            name="topics",
            dtype=DataType.ARRAY,
            element_type=DataType.VARCHAR,
            max_capacity=8,
            max_length=32,
        ),#
        FieldSchema(
            name="keywords",
            dtype=DataType.ARRAY,
            element_type=DataType.VARCHAR,
            max_capacity=8,
            max_length=32,
        ),#
        FieldSchema(name="parent_id", dtype=DataType.INT32),##
        FieldSchema(name="date_created", dtype=DataType.INT32),##
        FieldSchema(name="date_updated", dtype=DataType.INT32),##
        FieldSchema(name="user_created", dtype=DataType.VARCHAR, max_length=36),##
        FieldSchema(name="user_updated", dtype=DataType.VARCHAR, max_length=36),##
        FieldSchema(
            name="title_embedding_dense",
            dtype=DataType.FLOAT_VECTOR,
            dim=768,
        ),##
        FieldSchema(
            name="text_embedding_dense",
            dtype=DataType.FLOAT_VECTOR,
            dim=768,
        ),##
        FieldSchema(
            name="text_embedding_sparse",
            dtype=DataType.SPARSE_FLOAT_VECTOR,
        ),##
        #FieldSchema(name="image_embedding", dtype=DataType.FLOAT_VECTOR, dim=768),
        #FieldSchema(name="audio_embedding", dtype=DataType.FLOAT_VECTOR, dim=768),
        # FieldSchema(
        #     name="time_embedding", dtype=DataType.FLOAT_VECTOR, dim=2
        # ),  # a scalar that is recalculated each day based on a sigmoid schedule
    ],
    partition_key_field="company_id",
)

class MilvusClient(BaseMilvusClient):
    """A class to manage the connection to a Milvus server, perform vector operations and edit content fields."""

    def __init__(
        self, host: str, port: str,
    ):  # db_name: str = "milvus"):
        self.host = host
        self.port = port
        super().__init__(
            uri=f"http://{self.host}:{self.port}"
        )  # , db_name=self.db_name
        connections.connect(host=self.host, port=self.port)

    def __await__(self):
        return self._setup().__await__()

    async def _setup(self):
        """Connects to the Milvus server and sets up the collections with indexes if not already existing."""
        try:

            if not self.has_collection(_CONTENT_COLLECTION_NAME):
                
                # Create HNSW indexes on vector fields
                index_params = self.prepare_index_params()

                # Add indexes for different fields
                index_params.add_index(
                    field_name="title_embedding_dense",
                    index_type="HNSW",
                    index_name="title_embedding_dense",
                    M=16, 
                    efConstruction=200,
                    metric_type="IP"  # COSINE
                )

                index_params.add_index(
                    field_name="text_embedding_dense",
                    index_type="HNSW",
                    index_name="text_embedding_dense",
                    M=16,
                    efConstruction=200,
                    metric_type="IP"  # COSINE
                )

                index_params.add_index(
                    field_name="text_embedding_sparse",
                    index_type="SPARSE_INVERTED_INDEX",
                    index_name="text_embedding_sparse",
                    metric_type="IP"  # COSINE
                )
                
                # TODO: Add time embedings
                # index_params.add_index(
                #     field_name="time_embedding",
                #     index_type="HNSW",
                #     index_name="time_embedding",
                #     M=16,
                #     efConstruction=200,
                #     metric_type="IP"  # COSINE
                # )

                self.create_collection(
                    _CONTENT_COLLECTION_NAME, schema=_COLLECTION_SCHEMA, index_params=index_params, consistency_level="Strong"
                )

            # Load the collection
            self.load_collection(collection_name=_CONTENT_COLLECTION_NAME, replica_number=1)

            logger.info(f"Connected to Milvus server at {self.host}:{self.port}")
            return self
        except Exception as e:
            logger.error(f"Error connecting to Milvus: {e}")
            raise e

    async def recreate_collection(self, collection_name: str = _CONTENT_COLLECTION_NAME):
        """Recreates the collection and indexes."""
        try:
            if self.has_collection(collection_name):
                self.drop_collection(collection_name)
            await self._setup()
            logger.info("Recreated collection and indexes.")
        except Exception as e:
            logger.error(f"Error recreating collection: {e}")
            raise e

    async def disconnect(self):
        """Disconnects from the Milvus server."""
        try:
            self.release_collection(collection_name=_CONTENT_COLLECTION_NAME)
            self.close()
            logger.info("Disconnected from Milvus server")
        except Exception as e:
            logger.error(f"Error disconnecting from Milvus: {e}")
            raise e

    async def insert_data(self, data: list[dict], collection_name=_CONTENT_COLLECTION_NAME, partition_name: str = None):
        """Inserts data into the collection or a specific partition."""
        try:
            insert_result = self.insert(
                collection_name=collection_name, data=data, partition_name=partition_name
            )
            logger.info(
                f"Inserted {insert_result["insert_count"]} entities."
            )
            return insert_result
        except Exception as e:
            logger.error(f"Error during insert: {e}")
            raise e

    async def upsert_data(self, data: list[dict], collection_name=_CONTENT_COLLECTION_NAME, partition_name: str = None):
        """Upserts a list of data into the collection or a specific partition for a primary key."""
        try:
            upsert_result = self.upsert(
                collection_name=collection_name, data=data, partition_name=partition_name
            )
            logger.info(f"Upserted {upsert_result["upsert_count"]} entities.")
            return upsert_result
        except Exception as e:
            logger.error(f"Error during upsert: {e}")
            raise e

    async def delete_data(
        self,
        filter_expr: str = None,
        primary_ids: list = None,
        partition_name: str = None,
        collection_name: str = _CONTENT_COLLECTION_NAME,
    ):
        """Deletes entities based on filter expression or primary ids, optionally within a specific partition."""
        
        if filter_expr and primary_ids:
            raise ValueError(
                "Only one of 'filter_expr' or 'primary_ids' can be provided."
            )
            
        try:
            if filter_expr:
                delete_result = self.delete(
                    collection_name=collection_name,
                    filter=filter_expr,
                    partition_name=partition_name,
                )
            elif primary_ids:
                delete_result = self.delete(
                    collection_name=collection_name,
                    ids=primary_ids,
                    partition_name=partition_name,
                )
            else:
                raise ValueError(
                    "Either 'filter_expr' or 'primary_ids' must be provided."
                )
            return delete_result
        except Exception as e:
            logger.error(f"Error during delete: {e}")
            raise e

    async def get_data(
        self,
        collection_name: str = _CONTENT_COLLECTION_NAME,
        filter_expr: str = None,
        primary_ids: list = None,
        output_fields: list[str] = None,
        partition_names: list[str] = None,
    ):
        """Queries the collection for entities based on IDs."""
        
        if filter_expr and primary_ids:
            raise ValueError(
                "Only one of 'filter_expr' or 'primary_ids' can be provided."
            )
            
        try:
            if filter_expr:
                query_result = self.query(
                    collection_name=collection_name,
                    filter=filter_expr,
                    output_fields=output_fields,
                    partition_names=partition_names,
                )
            elif primary_ids:
                query_result = self.get(
                    collection_name=collection_name,
                    ids=primary_ids,
                    output_fields=output_fields,
                    partition_names=partition_names,
                )
            else:
                raise ValueError(
                    "Either 'filter_expr' or 'primary_ids' must be provided."
                )
            logger.info(f"Queried {len(query_result)} entities.")
            return query_result
        except Exception as e:
            logger.error(f"Error during query: {e}")
            raise e

    async def multi_vector_search(
        self,
        vectors: list[float],  # [...]
        field_names: list[str],  # [field_name1, field_name2, ...]
        offset: int = None,
        search_params: dict = None,
        filter_expr: str = None,
        output_fields: list = ["content_id", "text", "title"],
        ranking_strategy: str = "rrf",  # "weighted" or "rrf"
        weights: list = None,  # weights for weighted ranking
        page_size: int | None = 20,
    ):
        """Performs a multi-vector paginated search with optional filtering and specified ranking strategy."""
        try:
            search_params = search_params or {}

            limit = page_size

            # Create AnnSearchRequest objects for each vector field
            req_list = []

            for vector, field_name in zip(vectors, field_names):
                
                param = {
                    "metric_type": "IP",
                    "params": { "offset": offset },
                }
                
                param.update(search_params.get(field_name, {}))
                
                req = AnnSearchRequest(
                    data=[vector],
                    anns_field=field_name,
                    param=param,
                    expr=filter_expr,
                    limit=limit*3
                )
                req_list.append(req)

            # Choose ranking strategy
            if ranking_strategy == "weighted":
                if len(weights) != len(req_list):
                    raise ValueError(
                        "Weights must have the same length as the number of vector fields."
                    )
                if not weights:
                    raise ValueError("Weights must be provided for weighted ranking.")
                ranker = WeightedRanker(*weights)
            elif ranking_strategy == "rrf":
                ranker = RRFRanker()
            else:
                raise ValueError(
                    "Invalid ranking strategy. Choose 'weighted' or 'rrf'."
                )
            
            content_collection = Collection(_CONTENT_COLLECTION_NAME)

            search_result = content_collection.hybrid_search(
                req_list,
                ranker,
                offset=offset, # Number of initial search results to skip
                limit=page_size,  # Number of final search results to return
                output_fields=output_fields,
            )
            return search_result
        except Exception as e:
            logger.error(f"Error during multi-vector search: {e}")
            raise e
