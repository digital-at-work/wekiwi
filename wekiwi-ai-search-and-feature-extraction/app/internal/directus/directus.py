# Made open source under the GNU Affero General Public License, Version 3 (AGPL-3.0),
# by digital@work GmbH (2024). This file is part of wekiwi.
# See the LICENSE file in the project root or https://www.gnu.org/licenses/agpl-3.0.html for details.

from pydirectus import DirectusClient as BaseDirectusClient
from typing import List

from app.internal.types import ContentOptional


class DirectusClient(BaseDirectusClient):
    """
    Class to interact with Directus.
    """

    def __init__(self, DIRECTUS_URL: str = None, DIRECTUS_ADMIN_KEY: str = None):
        self.token = DIRECTUS_ADMIN_KEY
        self.url = DIRECTUS_URL
        super().__init__(hostname=DIRECTUS_URL, static_token=DIRECTUS_ADMIN_KEY)

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
