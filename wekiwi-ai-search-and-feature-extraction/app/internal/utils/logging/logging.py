# Made open source under the GNU Affero General Public License, Version 3 (AGPL-3.0),
# by digital@work GmbH (2024). This file is part of wekiwi.
# See the LICENSE file in the project root or https://www.gnu.org/licenses/agpl-3.0.html for details.

import sys
import time

from loguru import logger

import json
from fastapi import Request


def init_logging(level):
    logger.remove()
    logger.add(sys.stdout, level=level, colorize=True, format="<green>{time}</green> <level>{message}</level>")


async def log_requests_and_responses(request: Request, call_next):
    start_time = time.time()
    request_log = {
        "method": request.method,
        "url": str(request.url),
        "headers": dict(request.headers),
    }
    logger.debug(f"Request: {json.dumps(request_log)}")

    try:
        response = await call_next(request)
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        raise

    process_time = round((time.time() - start_time) * 1000)
    response_log = {
        "status_code": response.status_code,
        "headers": dict(response.headers),
        "process_time_ms": process_time,
    }
    logger.info(f"Response: {json.dumps(response_log)}")
    response.headers["X-Process-Time"] = str(process_time)

    return response