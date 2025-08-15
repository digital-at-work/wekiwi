# Made open source under the GNU Affero General Public License, Version 3 (AGPL-3.0),
# by digital@work GmbH (2024). This file is part of wekiwi.
# See the LICENSE file in the project root or https://www.gnu.org/licenses/agpl-3.0.html for details.

from typing import List, Optional, Literal, Any # Added Any for potential future use
from pydantic import BaseModel, Field, field_validator

from datetime import datetime



class User(BaseModel):
    id: str
    username: Optional[str] = None
    avatar: Optional[str] = None
    
    
class ContentBase(BaseModel):
    content_id: int
    file_id: str = Field(default="")
    content_type: Literal['text', 'image', 'audio']
    date_created: int = Field(default=0)
    date_updated: int = Field(default=0)
    parent_id: int = Field(default=0)
    summary: str = Field(default="")
    text: str = Field(default="")
    title: str = Field(default="")
    #circle_ids: List[int] = Field(default=[0]) #new
    user_created: str = Field(default="")
    user_updated: str = Field(default="")
    topics: List[str] = Field(default=[""])
    keywords: List[str] = Field(default=[""])

# e.g. Content creation
class ContentValidated(ContentBase):
    # Overwrite None with default values
    @field_validator('file_id', 'summary', 'text', 'title', 'user_created', 'user_updated', mode='before')
    def set_default_str(cls, v):
        # Handle XML/ElementTree objects
        if v is not None and hasattr(v, 'getroot'):
            try:
                from lxml import etree
                from loguru import logger
                logger.warning(f"Converting lxml.etree._ElementTree to string in ContentValidated")
                return etree.tostring(v, encoding='unicode', method='text')
            except ImportError:
                from loguru import logger
                logger.error("lxml module not found but XML object detected")
                return str(v)
        return v or ""
    @field_validator('parent_id', mode='before')
    def set_default_int(cls, v):
        return v or 0
    @field_validator('topics', 'keywords', mode='before')
    def set_default_list(cls, v):
        return v or [""]
    
    # If needed, convert the string object to a Unix timestamp (int)
    @field_validator('date_created', 'date_updated', mode='before')
    @classmethod
    def convert_to_unix_timestamp(cls, value):
        if isinstance(value, str):
            dt = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
            return int(dt.timestamp())
        return value or 0

class ContentSearchResult(ContentBase):
    score: Optional[float]
    child_id: Optional[List["ContentSearchResult"]]
    date_created: Optional[str] = None  # overwriting the int type with str
    date_updated: Optional[str] = None  # overwriting the int type with str

    class Config:
        from_attributes = True

ContentSearchResult.model_rebuild()

# e.g. Content update
class ContentOptional(ContentBase):
    file_id: Optional[str] = None
    content_type: Optional[Literal['text', 'image', 'audio']] = None
    date_created: Optional[int] = None
    date_updated: Optional[int] = None
    parent_id: Optional[int] = None
    summary: Optional[str] = None
    text: Optional[str] = None
    title: Optional[str] = None
    user_created: Optional[str] = None
    user_updated: Optional[str] = None
    topics: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    
    # Add XML handling validator for ContentOptional as well
    @field_validator('text', 'title', 'summary', mode='before')
    def convert_xml_to_string(cls, v):
        # Handle XML/ElementTree objects
        if v is not None and hasattr(v, 'getroot'):
            try:
                from lxml import etree
                from loguru import logger
                logger.warning(f"Converting lxml.etree._ElementTree to string in ContentOptional")
                return etree.tostring(v, encoding='unicode', method='text')
            except ImportError:
                from loguru import logger
                logger.error("lxml module not found but XML object detected")
                return str(v)
        return v


# --- Added for PDF Parsing Flow ---
class PdfParseTriggerPayload(BaseModel):
    directus_file_id: str = Field(..., description="UUID of the uploaded PDF file in Directus")
    parent_content_id: int = Field(..., description="Content ID of the parent item to reply to")
    user_created_id: str = Field(..., description="UUID of the user who created the content")
    company_id: int = Field(..., description="Company ID associated with the content")
    circle_ids: List[int] = Field(..., description="List of circle IDs associated with the content")
    document_content_id: Optional[int] = Field(None, description="Content ID of the document item itself") # Optional, but potentially useful
    title: Optional[str] = Field(None, description="Title of the PDF document to use for the reply")

# --- Added for Direct PDF Upload Flow ---
class DirectPdfUploadRequest(BaseModel):
    user_id: str = Field(..., description="UUID of the user uploading the PDF")
    company_id: Optional[int] = Field(None, description="Company ID associated with the content (Optional if fetched from Directus)")
    circle_ids: Optional[List[int]] = Field(None, description="List of circle IDs associated with the content (Optional if fetched from Directus)")
# --- End Added Section ---
