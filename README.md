# UHC Eligibility & Network Status Checker

A Streamlit web application for checking UHC (UnitedHealthcare) member eligibility and network status using the UHC API marketplace.

## Features

- **OAuth Token Management**: Automatic token generation and persistent storage
- **Member Eligibility Search**: Comprehensive eligibility checking with detailed results
- **Comprehensive Benefit Display**: Shows all benefit information including:
  - Patient demographics and contact information
  - Insurance and policy details
  - Deductible information (individual/family, in-network/out-of-network)
  - Out-of-pocket maximums
  - Copay and coinsurance details
  - Referral requirements
  - Primary care physician information
  - Plan messages and coverage details

## Deployment Options

### Option 1: Streamlit Cloud (Recommended)

1. **Fork/Clone this repository**
2. **Set up environment variables in Streamlit Cloud:**
   - `UHC_CLIENT_ID`: Your UHC API client ID
   - `UHC_CLIENT_SECRET`: Your UHC API client secret
3. **Deploy through Streamlit Cloud:**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository
   - Choose the main branch and `streamlit_app.py` as the main file
   - Set the environment variables in the advanced settings

### Option 2: Local Development

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd uhc-eligibility-checker
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up configuration:**
   ```bash
   cp config_example.py config.py
   ```
   Then edit `config.py` with your actual UHC API credentials.

5. **Run the application:**
   ```bash
   streamlit run streamlit_app.py
   ```

## Configuration

### Environment Variables

For production deployment, set these environment variables:

- `UHC_CLIENT_ID`: Your UHC API client ID
- `UHC_CLIENT_SECRET`: Your UHC API client secret

### Local Development

For local development, create a `config.py` file based on `config_example.py`:

```python
import os

UHC_API_BASE_URL = "https://apimarketplace.uhc.com/Eligibility"
UHC_CLIENT_ID = os.getenv("UHC_CLIENT_ID", "your-client-id-here")
UHC_CLIENT_SECRET = os.getenv("UHC_CLIENT_SECRET", "your-client-secret-here")
UHC_OAUTH_URL = "https://apimarketplace.uhc.com/v1/oauthtoken"
TOKEN_FILE = "uhc_oauth_token.json"
```

## Usage

1. **Generate OAuth Token**: Use the sidebar to generate an OAuth token using your UHC API credentials
2. **Search Member Eligibility**: Enter member ID and date of birth (MM/DD/YYYY format)
3. **View Results**: Review comprehensive eligibility information including benefits, deductibles, and coverage details

## API Integration

This application integrates with the UHC API Marketplace:
- **OAuth Endpoint**: `https://apimarketplace.uhc.com/v1/oauthtoken`
- **Eligibility Endpoint**: `https://apimarketplace.uhc.com/Eligibility/api/external/member/eligibility/v3.0`

## Security Notes

- All sensitive configuration data is stored in environment variables
- OAuth tokens are stored locally and automatically refreshed
- The `config.py` file (containing credentials) is excluded from version control

## File Structure

```
├── streamlit_app.py          # Main Streamlit application
├── config_example.py         # Configuration template
├── requirements.txt          # Python dependencies
├── .gitignore               # Git ignore file
├── README.md                # This file
└── run_app.bat              # Windows run script
```

## Requirements

- Python 3.7+
- Streamlit
- requests
- pandas
- python-dateutil

## License

This project is for internal use with UHC API integration.

## Support

For issues related to UHC API access, contact your UHC API representative.
For application issues, check the Streamlit logs or create an issue in this repository. 