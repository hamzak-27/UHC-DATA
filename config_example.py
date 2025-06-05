import os

# UHC API Configuration
# Copy this file to config.py and replace the placeholder values with your actual credentials
UHC_API_BASE_URL = "https://apimarketplace.uhc.com/Eligibility"
UHC_CLIENT_ID = os.getenv("UHC_CLIENT_ID", "your-client-id-here")
UHC_CLIENT_SECRET = os.getenv("UHC_CLIENT_SECRET", "your-client-secret-here")
UHC_OAUTH_URL = "https://apimarketplace.uhc.com/v1/oauthtoken"

# Token storage file
TOKEN_FILE = "uhc_oauth_token.json" 