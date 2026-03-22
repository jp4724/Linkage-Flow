import settings
import re
import os
import json
import yaml
import logging
from google import genai
from google.genai import types
from google.api_core import exceptions
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY").strip()
logger = logging.getLogger("AlumniETL.AI")

@retry(
    stop=stop_after_attempt(5), # max 3 times retry
    wait=wait_exponential(multiplier=1, min=4, max=10), 
    retry=retry_if_exception_type((
        exceptions.InternalServerError, # 500 Error
        exceptions.ResourceExhausted,   # 429 Error(Rate Limit)
        exceptions.ServiceUnavailable,  # 503 Error
        exceptions.DeadlineExceeded)),  # 504 Error
    before_sleep=lambda retry_state: logger.warning(
        f"Gemini API issue. Attempt {retry_state.attempt_number} failed. "
        f"Error: {retry_state.outcome.exception()}. Retrying in a few seconds..."
    )
)
def invoke_gemini(main_request,*, model_id = 'gemini-2.5-flash', system_instruction=None):
    # Fill in the question
    try: 
        content = main_request
        client = genai.Client(api_key=API_KEY)
        
        logger.debug(f"Sending request: {repr(main_request)[:200]}...")
        response = client.models.generate_content(
            model=model_id, 
            contents=content,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction
            )
        )
        token_count = response.usage_metadata.total_token_count
        logger.info(f"Gemini call success! Token used: {token_count}")
        return response
    except Exception as e:
        print(f"\n=== CAUGHT EXCEPTION in invoke_gemini ===")
        print(f"Type: {type(e).__name__}")
        print(f"Full repr: {repr(e)}")
        print(f"Message: {str(e)}")
        print("=======================================\n")
        raise

def clean_text_for_llm(text):
    if not text:
        return ""
    text = text.replace('', '').replace('', "'")
    text = re.sub(r'[^\x20-\x7E\n]', ' ', text)
    text = " ".join(text.split())
    return text
    
def read_LLM_config():
    try:
        with open("prompts.yaml", "r", encoding="utf-8") as f:
            llm_config = yaml.safe_load(f)['system_instructions']
        return llm_config
    except FileNotFoundError:
        print(f"Failed to find LLM config file")
        return None

def extract_json_from_string(GenAI_resp):
    # This function read GenAI response text and extracts JSON content from it

    # this regex looks for text betweeen ```json and or just ``` and ```
    # It also handles cases where there no backticks at all
    pattern = r"```(?:json)?\s*([\s\S]*?)\s*```"
    match = re.search(pattern, GenAI_resp)

    if match:
        # If markdown blocks were found, take the content inside
        json_content = match.group(1).strip()
    else:
        # If no markdown blocks, assume the whole text is JSON
        json_content = GenAI_resp.strip()

    # Test if it's valid JSON
    try: 
        return json.loads(json_content)
    except json.JSONDecodeError as e:
        return f"Error: Ivalid JSON structure - {str(e)}"