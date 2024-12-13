# Made open source under the GNU Affero General Public License, Version 3 (AGPL-3.0),
# by digital@work GmbH (2024). This file is part of wekiwi.
# See the LICENSE file in the project root or https://www.gnu.org/licenses/agpl-3.0.html for details.

import re
import ftfy

def sanitize_text(text):
    """Sanitizes text by fixing encoding issues, then removing patterns."""

    # 1. fix text if needed 2. remove long urls 3. Remove long, nonsensical chains of characters
    text = re.sub(r'[a-zA-Z0-9_+=/%&;:\.,<>\?-]{14,}', '', re.sub(r'(https?://[^/]+/[^/?\s]+)\S*', r'\1', ftfy.fix_text(text)) )

    return text