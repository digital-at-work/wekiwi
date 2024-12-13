# Made open source under the GNU Affero General Public License, Version 3 (AGPL-3.0),
# by digital@work GmbH (2024). This file is part of wekiwi.
# See the LICENSE file in the project root or https://www.gnu.org/licenses/agpl-3.0.html for details.

from FlagEmbedding import BGEM3FlagModel, FlagReranker

from typing import List, Union, Optional, Dict, Tuple
from sentence_transformers import SentenceTransformer

#TODO: use https://huggingface.co/jinaai/jina-reranker-v2-base-multilingual
class BGEReRankWrapper:
    def __init__(
        self,
        model_name_or_path: str,
        device: str = "cpu",
        use_fp16: bool = False,
        batch_size: int = 32,
        max_length: int = 1024,
    ):
        self.model = FlagReranker(model_name_or_path, device=device, use_fp16=use_fp16)
        self.batch_size = batch_size
        self.max_length = max_length

    def rerank(self, sentence_pairs: List[Tuple[str, str]]) -> List[float]:
        scores = self.model.compute_score(
            sentence_pairs=sentence_pairs,
            batch_size=self.batch_size,
            max_length=self.max_length,
        )
        if len(sentence_pairs) == 1:
            return [scores]
        return scores


class BGEM3Wrapper:
    def __init__(
        self,
        model_name_or_path: str,
        device: str = "cpu",
        use_fp16: bool = False,
        batch_size: int = 32,
        max_length: int = 2048,
        max_q_length: int = 512,
        rerank_weights: List[float] = [0.4, 0.2, 0.4],
    ):
        self.model = BGEM3FlagModel(model_name_or_path, device=device, use_fp16=use_fp16)
        self.batch_size = batch_size
        self.max_length = max_length
        self.max_q_length = max_q_length
        self.rerank_weights = rerank_weights

    def embed(
        self,
        sentences: List[str],
        return_sparse: bool = True,
        return_dense: bool = True,
        return_colbert: bool = False,
    ): #-> Tuple[list[float], list[float], list[float]]:
        embeddings = self.model.encode(
            sentences,
            batch_size=self.batch_size,
            max_length=self.max_length,
            return_sparse=return_sparse,
            return_dense=return_dense,
            return_colbert_vecs=return_colbert,
        )       
        # TODO: why does the processor not work with a tuple or an array return type? 
        #sparse_embeddings = embeddings["dense_vecs"]
        #dense_embeddings = embeddings["lexical_weights"]
        #colbert_embeddings = embeddings["colbert_vecs"]
        return embeddings["lexical_weights"]

    def rerank(self, sentence_pairs: List[Tuple[str, str]]) -> List[float]:
        scores = self.model.compute_score(
            sentence_pairs,
            batch_size=self.batch_size,
            max_query_length=self.max_q_length,
            max_passage_length=self.max_length,
            weights_for_different_modes=self.rerank_weights,
        )["colbert+sparse+dense"]
        return scores


class SentenceTransformerWrapper:
    def __init__(
        self,
        model_name_or_path: Optional[str] = None,
        device: Optional[str] = None,
        target_devices: Optional[List[str]] = None,
        fp_16: Optional[bool] = False,
        batch_size: Optional[int] = 32,
        local_files_only = False
    ):
        self.model = SentenceTransformer(
            model_name_or_path=model_name_or_path,
            trust_remote_code=True,
            device=device,
            # model_kwargs={"torch_dtype": torch.float16 if fp_16 else "auto"},
            local_files_only=local_files_only,
        )
        self.device = device
        self.batch_size = batch_size
        self.target_devices = target_devices
    
    def __await__(self):
        return self._start_multi_process_pool().__await__()

    def _start_multi_process_pool(self):
        self.pool = self.model.start_multi_process_pool(
            target_devices=self.target_devices,
        )  # 4 CPU devices will be used by default
        return self

    @staticmethod
    def stop_multi_process_pool(pool):
        SentenceTransformer.stop_multi_process_pool(pool)

    def embed(
        self,
        sentences: List[str],
        batch_size: int = 32,
        show_progress_bar: Optional[bool] = None,
        output_value: str = "sentence_embedding",
        normalize_embeddings: bool = False,
        prompt_name: Optional[str] = None,
        prompt: Optional[str] = None,
        device: Optional[str] = None,
    ) -> Union[List[List[float]]]:
        return self.model.encode(
            sentences=sentences,
            batch_size=batch_size,
            show_progress_bar=show_progress_bar,
            output_value=output_value,
            convert_to_numpy=True,
            normalize_embeddings=normalize_embeddings,
            prompt_name=prompt_name,
            prompt=prompt,
            device=device or self.device,
        ).tolist()

    def embed_multi_process(
        self,
        sentences: List[str],
        batch_size: None,
        chunk_size: Optional[int] = None,
        normalize_embeddings: bool = False,
        prompt_name: Optional[str] = None,
        prompt: Optional[str] = None,
    ):
        if batch_size is None:
            batch_size = self.batch_size
        return self.model.encode_multi_process(
            sentences=sentences,
            batch_size=batch_size,
            chunk_size=chunk_size,
            normalize_embeddings=normalize_embeddings,
            prompt_name=prompt_name,
            prompt=prompt,
        )

    def tokenize(self, texts: Union[List[str], List[Dict], List[Tuple[str, str]]]):
        return self.model.tokenize(texts)
