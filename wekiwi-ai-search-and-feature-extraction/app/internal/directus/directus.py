# Made open source under the GNU Affero General Public License, Version 3 (AGPL-3.0),
# by digital@work GmbH (2024). This file is part of wekiwi.
# See the LICENSE file in the project root or https://www.gnu.org/licenses/agpl-3.0.html for details.

from unittest import result
from pydirectus import DirectusClient as BaseDirectusClient
from typing import List, Optional
from loguru import logger
import httpx

from app.internal.types import ContentOptional


class DirectusClient(BaseDirectusClient):
    """
    Class to interact with Directus as admin. This is to be used by the trigger_parse endpoint.
    Do NOT switch to UserDirectusClient, as it will not work for the parsing that is triggered by the 'Trigger Parse' directus flow.
    Includes patching logic to set user_created field for proper attribution.
    """

    def __init__(self, DIRECTUS_URL: str = None, DIRECTUS_ADMIN_KEY: str = None):
        self.token = DIRECTUS_ADMIN_KEY
        self.url = DIRECTUS_URL
        super().__init__(hostname=DIRECTUS_URL, static_token=DIRECTUS_ADMIN_KEY)
        
    def create_item(self, collection: str, data: dict):
        """
        Creates an item in Directus as admin, then patches it to set the user_created field if specified.
        This approach ensures proper user attribution while working within Directus's permission system.
        
        Args:
            collection: The collection to create the item in (e.g., "contents")
            data: The data to create the item with, may include user_created field
            
        Returns:
            The created (and potentially patched) item
        """
        from loguru import logger
        import httpx
        
        # Extract user_created if present, then remove it for the initial creation
        user_id = None
        if "user_created" in data and data["user_created"]:
            user_id = data["user_created"]
            logger.info(f"Detected user_created field with ID: {user_id}")
        
        # Call the parent class method to create the item
        created_item = super().create_item(collection=collection, data=data)
        logger.info(f"Created item in collection {collection}: {created_item}")
        
        # If we have a user_id and a content_id, patch the user_created field
        if user_id and "content_id" in created_item:
            item_id = created_item.get("content_id")
            logger.info(f"Patching item {item_id} to set user_created to {user_id}")
            
            try:
                # Make direct PATCH request to Directus API
                url = f"{self.url.rstrip('/')}/items/{collection}/{item_id}"
                headers = {
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "user_created": user_id
                }
                
                # Use httpx for the API call
                response = httpx.patch(url, json=payload, headers=headers)
                response.raise_for_status()
                patched_item = response.json().get("data")
                
                logger.info(f"Successfully patched item {item_id} to user {user_id}")
                return patched_item
            except Exception as e:
                logger.error(f"Failed to patch user_created: {e}")
        
        # Return the original item
        return created_item

    async def get_ids(self, collection: str = "contents") -> List[dict]:
        """
        Gets all content ids.
        """
        query = {
            "fields": ["content_id"],
            "limit": 50000,  # TODO: better to do in batches or something?
            # "filter": {"status": "published"} TODO: establish in frontend
        }

        return self.read_items(collection=collection, query=query)

    async def get_ids_rebuild(self, collection: str = "contents") -> List[dict]:
        """
        Gets all content ids.
        """
        query = {
            "filter": {
                # TODO: support other content types
                "content_type": {"_eq": "text"},
            },
            "fields": ["content_id"],
            "limit": 50000,  # TODO: better to do in batches or something?
            # "filter": {"status": "published"} TODO: establish in frontend
        }

        return self.read_items(collection=collection, query=query)

    async def get_contents_rebuild(
        self,
        content_ids: List[int],
    ) -> List[ContentOptional]:
        """
        Gets the content information for specific content ids.
        """
        query = {
            "filter": {
                "_or": [
                    {
                        "content_id": {"_in": content_ids},
                    },
                    {
                        "child_id": {
                            "content_id": {"_in": content_ids},
                        }
                    },
                    {
                        "child_id": {
                            "child_id": {
                                "content_id": {"_in": content_ids},
                            }
                        }
                    },
                    # TODO: add attachments?
                ]
            },
            "fields": [
                "content_id",
                "file_id",
                "content_type",
                "title",
                "text",
                "user_created",
                "user_updated",
                "parent_id",
                "date_created",
                "date_updated",
                "company_id",
                "circle_contents.circle_id.circle_id",
                {"interaction_id": ["interaction_id"]},
                {
                    "user_created": ["avatar", "username"],
                    "user_updated": ["avatar", "username"],
                },
            ],
        }

        return self.read_items("contents", query=query)

    async def get_contents(
        self,
        content_ids: List[int],
        company_id: int,
    ) -> List[ContentOptional]:
        """
        Gets the content information for specific content ids.
        """
        query = {
            "filter": {
                "_and": [
                    {
                        "company_id": {"_eq": company_id},
                    },
                    {
                        "_or": [
                            {
                                "content_id": {"_in": content_ids},
                            },
                            {
                                "child_id": {
                                    "content_id": {"_in": content_ids},
                                }
                            },
                            {
                                "child_id": {
                                    "child_id": {
                                        "content_id": {"_in": content_ids},
                                    }
                                }
                            },
                            # TODO: add attachments?
                        ]
                    },
                ]
            },
            "fields": [
                ## DO NOT CHANGE THE ORDER OF THESE FIELDS
                "content_id",
                "file_id",
                "content_type",
                "title",
                "text",
                "parent_id",
                "date_created",
                "date_updated",
                "interaction_id.interaction_id",
                "user_created.avatar",
                "user_created.username",
                "user_updated.avatar",
                "user_updated.username",
            ],
        }

        return self.read_items("contents", query=query)

    async def getCirclesAccess(self, user_ids: List[str]):
        """
        Gets the circles a user is part of.
        """
        query = {"filter": {"directus_users_id": {"_in": user_ids}}}
        return await self.read_items("user_circle", query=query)

    async def disconnect(self):
        """
        Logs out the client.
        """
        await self.close()
        
    def upload_file(self, file_data: bytes, filename: str, mime_type: str = None, folder: str = None):
        """
        Uploads a file to Directus and returns the file ID.
        
        Args:
            file_data: The binary content of the file
            filename: The name of the file
            mime_type: The MIME type of the file (default: application/pdf)
            mime_type: Optional MIME type (e.g., PDF, DOCX). Will be guessed if not provided.
            folder: Optional folder ID to store the file in, overrides the default content folder
            
        Returns:
            The file ID if successful, None otherwise
        """
        from loguru import logger
        import httpx
        import mimetypes
        try:
            # If no mime_type is provided, try to guess it from the filename
            if not mime_type:
                mime_type, _ = mimetypes.guess_type(filename)
                if not mime_type:
                    mime_type = "application/octet-stream"
                logger.info(f"Guessed MIME type: {mime_type}")
            # Prepare the upload URL
            upload_url = f"{self.url.rstrip('/')}/files"
            
            # Set up headers with authentication
            headers = {
                "Authorization": f"Bearer {self.token}"
            }
            
            # Create form data as a dict (will be added outside the files dict)
            form_data = {}
            
            # Use the hardcoded UUID for the 'content' folder - this exists in the system
            # This is the UUID for the content folder in staging: ec201009-b69a-4bee-8b3d-ae24fe220cc7
            content_folder_id = "ec201009-b69a-4bee-8b3d-ae24fe220cc7"
            
            # If a specific folder was provided, use that instead
            if folder:
                # Use the provided folder ID
                form_data["folder"] = folder
                logger.info(f"Using provided folder ID: {folder}")
            else:
                # Use the content folder ID
                form_data["folder"] = content_folder_id
                logger.info(f"Using content folder ID: {content_folder_id}")
            
            # CRITICAL: File must be provided in a field named 'file' per Directus API requirements
            # This field must be named 'file' exactly - this is a requirement from Directus API
            files = {
                'file': (filename, file_data, mime_type)
            }
            
            # Log detailed information about the upload
            logger.info(f"Uploading file {filename} to Directus with MIME type {mime_type}")
            logger.info(f"Request URL: {upload_url}")
            logger.info(f"Form data: {form_data}")
            
            # Send the POST request with files and form_data separate (standard multipart/form-data)
            response = httpx.post(upload_url, files=files, data=form_data, headers=headers)
            
            # Log response status for debugging
            if response.status_code >= 400:
                logger.error(f"Error response from Directus: {response.status_code} - {response.text}")
            
            response.raise_for_status()
            
            # Extract the file ID from the response
            response_data = response.json()
            file_id = response_data.get('data', {}).get('id')
            
            if file_id:
                logger.info(f"Successfully uploaded file. File ID: {file_id}")
                return file_id
            else:
                logger.error(f"File upload response missing ID: {response_data}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to upload file to Directus: {e}")
            return None


class UserDirectusClient(BaseDirectusClient):
    """
    Class to interact with Directus using a user's token directly.
    Does not include the patching logic used by the admin client.
    Use this client when the user is already authenticated with their own token.
    """

    def __init__(self, directus_url: str, user_token: str):
        self.url = directus_url
        self.token = user_token
        super().__init__(hostname=directus_url, static_token=user_token)
        logger.info("Initialized UserDirectusClient with user token")

    def create_item(self , collection: str, data: dict):
        url = f"{self.url.rstrip('/')}/items/{collection}"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        try :
            response = httpx.post(url, json=data, headers=headers)
            response.raise_for_status()
            result = response.json()
            logger.info(f"Successfully created item in Directus collection '{collection}': {result}")
            return result.get("data")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error while creating item :{e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error while creating item in Directus: {e}")
            raise
            
    def upload_file(self, file_data: bytes, filename: str, mime_type: str = None, folder: str = None):
        """
        Uploads a file to Directus and returns the file ID.
        Uses the user's token directly without admin patching.
        
        Args:
            file_data: The binary content of the file
            filename: The name of the file
            mime_type: Optional MIME type (e.g., PDF, DOCX). Will be guessed if not provided.
            folder: Optional folder ID to store the file in, overrides the default content folder
            
        Returns:
            The file ID if successful, None otherwise
        """
        try:
            # If no mime_type is provided, try to guess it from the filename
            if not mime_type:
                import mimetypes
                mime_type, _ = mimetypes.guess_type(filename)
                if not mime_type:
                    mime_type = "application/octet-stream"
                logger.info(f"Guessed MIME type: {mime_type}")
                
            # Prepare the upload URL
            upload_url = f"{self.url.rstrip('/')}/files"
            
            # Set up headers with authentication
            headers = {
                "Authorization": f"Bearer {self.token}"
            }
            
            # Create form data as a dict (will be added outside the files dict)
            form_data = {}
            
            # Use the hardcoded UUID for the 'content' folder - this exists in the system
            # This is the UUID for the content folder in staging: ec201009-b69a-4bee-8b3d-ae24fe220cc7
            content_folder_id = "ec201009-b69a-4bee-8b3d-ae24fe220cc7"
            
            # If a specific folder was provided, use that instead
            if folder:
                # Use the provided folder ID
                form_data["folder"] = folder
                logger.info(f"Using provided folder ID: {folder}")
            else:
                # Use the content folder ID
                form_data["folder"] = content_folder_id
                logger.info(f"Using content folder ID: {content_folder_id}")
            
            # CRITICAL: File must be provided in a field named 'file' per Directus API requirements
            # This field must be named 'file' exactly - this is a requirement from Directus API
            files = {
                'file': (filename, file_data, mime_type)
            }
            
            # Log detailed information about the upload
            logger.info(f"Uploading file {filename} to Directus with MIME type {mime_type}")
            logger.info(f"Request URL: {upload_url}")
            
            # Send the POST request with files and form_data separate (standard multipart/form-data)
            response = httpx.post(upload_url, files=files, data=form_data, headers=headers)
            
            # Log response status for debugging
            if response.status_code >= 400:
                logger.error(f"Error response from Directus: {response.status_code} - {response.text}")
            
            response.raise_for_status()
            
            # Extract the file ID from the response
            response_data = response.json()
            file_id = response_data.get('data', {}).get('id')
            
            if file_id:
                logger.info(f"Successfully uploaded file. File ID: {file_id}")
                return file_id
            else:
                logger.error(f"File upload response missing ID: {response_data}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to upload file to Directus: {e}")
            return None

    async def get_user_info(self):
        """
        Get the current user's information from Directus.
        Returns the user data if successful, None otherwise.
        """
        try:
            url = f"{self.url.rstrip('/')}/users/me?fields=*,user_circles.circle_id"
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                return response.json().get("data")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error while getting user info: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error while getting user info: {e}")
            raise
            
