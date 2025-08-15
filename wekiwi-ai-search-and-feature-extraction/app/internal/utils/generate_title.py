# Made open source under the GNU Affero General Public License, Version 3 (AGPL-3.0),
# by digital@work GmbH (2024). This file is part of wekiwi.
# See the LICENSE file in the project root or https://www.gnu.org/licenses/agpl-3.0.html for details.

import httpx
from app.config import OLLAMA_API_URL, OLLAMA_TITLE_MODEL

async def generate_german_title(text: str) -> str:
    """
    Generates a single, concise, and descriptive German title for the provided text
    using the OpenAI API.

    Args:
        text (str): The text to generate a title for.

    Returns:
        str: The generated German title.

    Raises:
        httpx.HTTPError: If the request to the API fails.
    """
    
    api_url = OLLAMA_API_URL
    model = OLLAMA_TITLE_MODEL

    # Outcommented code belongs to the previous llama.cpp implementation
    #api_url = "http://188.64.59.20:8057/completion"
    #api_key = "8a7c376d-12f4-473b-8eb1-6b41c5b07928"
    
    headers = {
    #    "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    #prompt = f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\nYou are a CAPTION GENARATOR that provides a SINGLE, EXTENSIVE and DESCRIPTIVE GERMAN TITLE for the provided text. The CAPTION should include the MAIN TOPICS. Your response ONLY includes the CAPTION.<|eot_id|>\n<|start_header_id|>user<|end_header_id|>\n\n{text}<|eot_id|>\n<|start_header_id|>assistant<|end_header_id|>"
    prompt = f"""Du bist ein TITEL-GENERATOR, der einen EINZIGEN, PRÄZISEN und BESCHREIBENDEN DEUTSCHEN TITEL für den folgenden Text erstellt. 
Der TITEL sollte die HAUPTTHEMEN enthalten und nicht länger als 6 Wörter sein.
Antworte NUR mit dem TITEL, ohne Einleitung, Emojis oder zusätzliche Erklärungen.

TEXT:
{text}

TITEL:"""

    data = {
        "model": model,
        "stream": False,
        #"n_predict": 256,
        #"temperature": 1,
        #"stop": [
        #    "</s>",
        #    "<|end|>",
        #    "<|eot_id|>",
        #    "<|end_of_text|>",
        #    "<|im_end|>",
        #    "<|EOT|>",
        #    "<|END_OF_TURN_TOKEN|>",
        #    "<|end_of_turn|>",
        #    "<|endoftext|>",
        #    "assistant",
        #    "user",
        #],
        #"repeat_last_n": 0,
        #"repeat_penalty": 1.2,
        #"penalize_nl": False,
        #"top_k": 0,
        #"top_p": 1,
        #"min_p": 0.35,
        #"tfs_z": 1,
        #"typical_p": 1,
        #"presence_penalty": 0,
        #"frequency_penalty": 0,
        # "mirostat": 0,
        # "mirostat_tau": 5,
        # "mirostat_eta": 0.1,
        #"grammar": "",
        #"n_probs": 0,
        #"min_keep": 0,
        #"cache_prompt": True,
        "prompt": prompt,
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(api_url, headers=headers, json=data)
            print(response.json())
            response.raise_for_status()
            return response.json().get("response", "").strip()
    except httpx.HTTPError as e:
        raise httpx.HTTPError(f"API request failed: {e}") 