# Made open source under the GNU Affero General Public License, Version 3 (AGPL-3.0),
# by digital@work GmbH (2024). This file is part of wekiwi.
# See the LICENSE file in the project root or https://www.gnu.org/licenses/agpl-3.0.html for details.

from typing import List, Any, Callable
import asyncio
from pydantic import BaseModel

from loguru import logger

from time import time
    

class TextRequestProcessor:
    """
    Processes embedding and reranking requests using a provided model.
    Manages request batching and resource locking for efficient processing.
    """

    def __init__(self, model: Any, max_request_to_flush: int = 1, accumulation_timeout: float = 0.1):
        self.model = model
        self.max_batch_size = max_request_to_flush
        self.accumulation_timeout = accumulation_timeout
        self.embed_queue = asyncio.Queue()
        self.rerank_queue = asyncio.Queue()
        self.gpu_lock = asyncio.Semaphore(1)
        
    def __await__(self):
        return self._start_processing_loops().__await__()

    async def _start_processing_loops(self):
        """Starts the processing loops for embedding and reranking."""
        if not hasattr(self.model, 'embed') and not hasattr(self.model, 'rerank'):
            raise ValueError("Model must have 'embed' and/or 'rerank' methods.")
        if hasattr(self.model, 'embed'):
            asyncio.create_task(self._processing_loop(self.embed_queue, self.model.embed, 'embeddings'))
        if hasattr(self.model, 'rerank'):
            asyncio.create_task(self._processing_loop(self.rerank_queue, self.model.rerank, 'rerank'))
        return self

    async def _processing_loop(self, queue: asyncio.Queue, process_func: Callable, response_key: str):
        """Handles the processing of batched requests."""
        while True:
            requests, futures = [], []
            start_time = time()
            while len(requests) < self.max_batch_size and time() - start_time < self.accumulation_timeout:
                try:
                    data, future = await asyncio.wait_for(queue.get(), timeout=0.01)
                    requests.append(data)
                    futures.append(future)
                except asyncio.TimeoutError:
                    continue

            if requests:
                async with self.gpu_lock:  # Ensure exclusive GPU/CPU access (acquire + release)
                    try:
                        # Process batched requests and return results
                        results = process_func(requests)
                        self._set_results(futures, results, response_key)
                    except Exception as e:
                        logger.error(f"Processing error: {e}")
                        for future in futures:
                            future.set_exception(e)

    @staticmethod
    def _set_results(futures: List[asyncio.Future], results: List, response_key: str):
        """Sets the results to the corresponding futures."""
        if response_key == 'embeddings':
            for future, result in zip(futures, results):
                future.set_result(result)
        elif response_key == 'rerank':
            for future, result in zip(futures, results):
                future.set_result(result)

    async def process_request(self, request_data: BaseModel, queue_name: str) -> BaseModel:
        """Submits a request to the specified queue and waits for the result."""
        future = asyncio.Future()
        if queue_name == 'embed':
            await self.embed_queue.put((request_data, future))
        elif queue_name == 'rerank':
            await self.rerank_queue.put((request_data, future))
        return future
