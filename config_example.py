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
UHC_CLIENT_ID = "ed655571-155f-47ab-a9ce-1270fa585f26"
UHC_CLIENT_SECRET = "hND8Q~4Ir19~YOMs8aQ0msbHgVIK~U5AfVT5SaVE"

# Local token storage file
TOKEN_FILE = "uhc_oauth_token.json" 