# config.py
from pathlib import Path
from datetime import datetime

# 获取当前项目的根目录
BASE_DIR = Path(__file__).resolve().parent
queryFilePath = BASE_DIR / "query.sql"
selfInfoPath = BASE_DIR/"data/self.txt"

# 定义文件夹路径
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
PROMPT_DIR = BASE_DIR / "prompts"

# 确保文件夹存在（不存在则自动创建）
DATA_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# 具体文件路径
JD_FILE = DATA_DIR / "JD.txt"
EXP_FILE = DATA_DIR / "self.txt"
PROMPT_YAML = PROMPT_DIR / "cover_letter_prompt.yaml"

# Self-information
USER_INFO = {
    "name": "Jingming Peng",
    "address": "407 W 206th St., New York, NY, 10034",
    "phone": "646-528-7619",
    "email": "jimmy.peng12666@outlook.com",
    "date": datetime.now().strftime("%B %d, %Y")
}

# API config
GEMINI_MODEL = "gemini-2.5-flash"
