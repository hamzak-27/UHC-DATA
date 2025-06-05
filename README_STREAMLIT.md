# UHC Eligibility & Network Status Checker - Streamlit App

This Streamlit application provides a user-friendly interface for checking UHC member eligibility, network status, and copay details using the UHC API.

## Features

- **OAuth Token Management**: Generate and manage OAuth tokens with automatic expiration tracking
- **Member Eligibility Search**: Search for member eligibility information
- **Provider Network Status**: Check if providers are in-network
- **Copay Details**: Retrieve copay and coinsurance information

## Configuration

The app uses the following configuration (extracted from Django settings.py):
- Client ID: `ed655571-155f-47ab-a9ce-1270fa585f26`
- Client Secret: `hND8Q~4Ir19~YOMs8aQ0msbHgVIK~U5AfVT5SaVE`
- OAuth URL: `https://apimarketplace.uhc.com/v1/oauthtoken`
- API Base URL: `https://apimarketplace.uhc.com/Eligibility`

## Installation

1. Install dependencies:
```bash
pip install -r requirements_streamlit.txt
```

2. Run the Streamlit app:
```bash
streamlit run streamlit_app.py
```

## Usage

### 1. Generate OAuth Token
- Click "Generate OAuth Token" in the sidebar
- The token will be automatically used for all API requests
- Token expires after 1 hour and needs to be regenerated

### 2. Member Eligibility Search
- Enter Member ID and Date of Birth (required)
- Fill in optional fields as needed
- Click "Search Eligibility" to get member information
- Results will be displayed with key metrics and detailed JSON

### 3. Provider Network Status
- After performing eligibility search, member information will auto-populate
- Enter provider information (Provider Last Name is required)
- Enter service dates
- Click "Check Network Status" to verify provider network participation

### 4. Copay Details
- Available after successful eligibility search
- Automatically uses patient key and transaction ID from eligibility search
- Click "Get Copay Details" to retrieve copay and coinsurance information

## Token Management

- Tokens expire after 1 hour
- The app shows token status and expiration time
- Automatic token validation before API calls
- 5-minute buffer for token expiration to prevent failed requests

## Error Handling

The app includes comprehensive error handling for:
- Network timeouts
- API errors
- Invalid responses
- Token expiration

## Security Notes

- Client credentials are currently hardcoded (extracted from Django settings)
- For production use, consider using environment variables
- Tokens are stored in Streamlit session state (memory only)

## API Endpoints Used

1. **OAuth Token**: `/v1/oauthtoken`
2. **Eligibility Search**: `/api/external/member/eligibility/v3.0`
3. **Network Status**: `/api/external/networkStatus/v4.0`
4. **Copay Details**: `/api/external/member/copay/v2.0` 