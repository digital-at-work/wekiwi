# Made open source under the GNU Affero General Public License, Version 3 (AGPL-3.0),
# by digital@work GmbH (2024). This file is part of wekiwi.
# See the LICENSE file in the project root or https://www.gnu.org/licenses/agpl-3.0.html for details.

import re
import ftfy

def sanitize_text(text):
    """Sanitizes text by fixing encoding issues, then removing patterns."""
    
    # Handle None or empty strings
    if not text:
        return ""
        
    # Handle potential XML/ElementTree objects
    if hasattr(text, 'getroot'):
        try:
            from lxml import etree
            from loguru import logger
            logger.warning(f"Converting ElementTree object to string in sanitize_text")
            return etree.tostring(text, encoding='unicode', method='text')
        except ImportError:
            from loguru import logger
            logger.error("lxml module not found but ElementTree object detected")
            return str(text)
    
    # Special case for URLs - preserve them without excessive processing
    url_pattern = r'^\s*https?://[^\s]+\s*$'
    if re.match(url_pattern, text):
        from loguru import logger
        logger.info(f"URL-only content detected in sanitize_text, preserving as-is")
        return text
        
    # For normal text: 1. fix text if needed 2. remove long urls 3. Remove long, nonsensical chains of characters
    try:
        text = re.sub(r'[a-zA-Z0-9_+=/%\&;:\.,<>\?-]{14,}', '', re.sub(r'(https?://[^/]+/[^/?\s]+)\S*', r'\1', ftfy.fix_text(text)) )
    except Exception as e:
        from loguru import logger
        logger.warning(f"Error in sanitize_text processing: {e}, using raw text")
        # If there's an error in processing, return the original text
        pass
        
    return text