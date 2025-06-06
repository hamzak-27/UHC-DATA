# Example configuration file for UHC Eligibility App
# 
# FOR LOCAL DEVELOPMENT ONLY:
# 1. Copy this file to config.py
# 2. Replace the placeholder values with your actual API credentials
# 3. config.py is excluded from git by .gitignore
#
# FOR STREAMLIT CLOUD DEPLOYMENT:
# Use Streamlit secrets instead - this file is not needed in production

# UHC API Configuration
UHC_API_BASE_URL = "https://apimarketplace.uhc.com/Eligibility"
UHC_OAUTH_URL = "https://apimarketplace.uhc.com/v1/oauthtoken"

# API Credentials - Replace with your actual credentials
UHC_CLIENT_ID = "your_client_id_here"
UHC_CLIENT_SECRET = "your_client_secret_here"

# Local token storage file
TOKEN_FILE = "uhc_oauth_token.json" 