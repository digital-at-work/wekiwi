# Made open source under the GNU Affero General Public License, Version 3 (AGPL-3.0),
# by digital@work GmbH (2024). This file is part of wekiwi.
# See the LICENSE file in the project root or https://www.gnu.org/licenses/agpl-3.0.html for details.

from fastapi import Depends, HTTPException, status, Header, Request
from typing import Optional
from app.internal.utils.logging import logger

async def validate_user_token(
    api_key: Optional[str] = Header(None, alias="Authorization", description="User's static Directus token for authentication")
) -> str:
    """
    Extracts the user's token from the Authorization header.
    Simply returns the token as-is.
    """
    if not api_key:
        raise HTTPException(status_code=401, detail="Unauthorized: Missing access token")
        
    token = api_key.strip()
        
    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized: Empty token provided")
        
    logger.info(f"User token provided for direct_upload endpoint")
    return token
