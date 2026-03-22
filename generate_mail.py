import settings
import AI_func
import logging
import yaml
logger = logging.getLogger("AlumniETL.generate_mail")

with open("prompts.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)
    LLM_CONFIG = config["system_instructions"]

def generate_customized_mail(self_info,target_df):
    mail_text_request = "### SENDER PROFILE (Me) <br>" + self_info + "\n\n" + "### RECEIVER DATA (The Alum) <br>" + target_df.to_json(orient='records')
    resp = AI_func.invoke_gemini(mail_text_request, model_id='gemini-3-flash-preview', system_instruction=LLM_CONFIG["generate_customized_mail"])
    logger.info(f"Email successfully generated.")
    return resp.text
    