# Made open source under the GNU Affero General Public License, Version 3 (AGPL-3.0),
# by digital@work GmbH (2024). This file is part of wekiwi.
# See the LICENSE file in the project root or https://www.gnu.org/licenses/agpl-3.0.html for details.

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import secrets

from app.config import API_SECRET


security = HTTPBearer()


def check_authentication(AuthorizationCredentials: HTTPAuthorizationCredentials = Depends(security)):
    correct_secret = secrets.compare_digest(AuthorizationCredentials.credentials, API_SECRET)
    if not correct_secret:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
