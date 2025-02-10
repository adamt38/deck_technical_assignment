import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_required_env_var(var_name):
    value = os.getenv(var_name)
    if not value:

        raise ValueError(f"Environment variable '{var_name}' is required but not set.")
    return value

USERNAME = get_required_env_var("USERNAME")
PASSWORD = get_required_env_var("PASSWORD")
MFA_CODE = get_required_env_var("MFA_CODE")
BASE_URL = get_required_env_var("BASE_URL")

TIMEOUT = int(os.getenv("TIMEOUT", 30))  # Default timeout is 30 seconds

