# Made open source under the GNU Affero General Public License, Version 3 (AGPL-3.0),
# by digital@work GmbH (2024). This file is part of wekiwi.
# See the LICENSE file in the project root or https://www.gnu.org/licenses/agpl-3.0.html for details.

from typing import List, Tuple
import re
from loguru import logger
from langchain_core.documents import Document

from langchain_text_splitters import HTMLSectionSplitter, RecursiveCharacterTextSplitter

def text_splitter(
    html_string: str,
    headers_to_split_on: List[Tuple[str, str]] = [
        ("h1", "Header 1"),
        ("h2", "Header 2"),
        ("h3", "Header 3"),
        ("h4", "Header 4"),
    ],
    chunk_size: int = 368,
    chunk_overlap: int = 30
) -> List[Document]:
    # Check if the input is primarily a URL
    url_pattern = r'https?://[^\s]+'
    if html_string and re.match(url_pattern, html_string.strip()):
        logger.info(f"Detected URL-only content, treating as plain text")
        return [Document(page_content=html_string)]
    
    # Check for very short text (likely not valid HTML)
    if html_string and len(html_string.split()) <= 2:
        logger.info(f"Text too short for HTML parsing, treating as plain text")
        return [Document(page_content=html_string)]
    
    try:
        # Initialize the HTMLSectionSplitter with default headers
        html_splitter = HTMLSectionSplitter(headers_to_split_on=headers_to_split_on)
        
        # Split the HTML 
        html_header_splits = html_splitter.split_text(html_string)
        
        # Initialize the RecursiveCharacterTextSplitter with default chunk size and overlap
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap
        ) # TODO: use .from_huggingface_tokenizer?
        
        # Further split the header-based splits into smaller chunks
        splits = text_splitter.split_documents(html_header_splits)
        
        return splits
    except Exception as e:
        logger.warning(f"Error processing HTML in text_splitter: {e}")
        # Fallback to simple document without HTML parsing
        return [Document(page_content=html_string)]