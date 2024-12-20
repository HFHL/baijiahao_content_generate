# config.py

import os

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')  # 上传文件的存储目录
SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')  # Flask应用的秘密密钥
API_KEY = os.getenv('OPENAI_API_KEY', 'sk-E7AQ07fKktPxezX7Fb25D31cD54a46B08496Db6c37A78780')  # OpenAI API密钥
BASE_URL = os.getenv('OPENAI_BASE_URL', 'https://az.gptplus5.com/v1')  # OpenAI API基础URL
MODEL_NAME = os.getenv('OPENAI_MODEL_NAME', 'gpt-4o')  # 使用的OpenAI模型
PROMPT_FILE = os.getenv('PROMPT_FILE', os.path.join(os.getcwd(), 'prompts', 'prompts.json'))
ALLOWED_EXTENSIONS = {'zip'}
SAVED_FOLDER = os.getenv('SAVED_FOLDER', os.path.join(os.getcwd(), 'saved_items'))