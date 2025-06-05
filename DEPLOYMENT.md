# Deployment Guide for UHC Eligibility Checker

## Streamlit Cloud Deployment (Recommended)

### Step 1: Prepare Your Repository

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Prepare for Streamlit Cloud deployment"
   git push origin main
   ```

2. **Ensure these files are in your repository:**
   - `streamlit_app.py` (main application file)
   - `requirements.txt` (dependencies)
   - `config_example.py` (configuration template)
   - `README.md` (documentation)
   - `.streamlit/config.toml` (Streamlit settings)
   - `.gitignore` (excludes sensitive files)

3. **Verify sensitive files are excluded:**
   - `config.py` should NOT be in the repository
   - `uhc_oauth_token.json` should NOT be in the repository

### Step 2: Deploy on Streamlit Cloud

1. **Go to Streamlit Cloud:**
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Sign in with your GitHub account

2. **Create New App:**
   - Click "New app"
   - Select your repository
   - Branch: `main`
   - Main file path: `streamlit_app.py`

3. **Configure Secrets:**
   - Click "Advanced settings" before deploying
   - In the "Secrets" section, add:
   ```toml
   UHC_CLIENT_ID = "your-actual-client-id"
   UHC_CLIENT_SECRET = "your-actual-client-secret"
   ```

4. **Deploy:**
   - Click "Deploy!"
   - Wait for the app to build and launch

### Step 3: Verify Deployment

1. **Test OAuth Token Generation:**
   - Use the sidebar to generate an OAuth token
   - Should see "Token generated successfully!"

2. **Test Eligibility Search:**
   - Enter test member ID and date of birth
   - Verify the comprehensive results display

## Local Development Setup

### Option 1: Using config.py (Recommended for Development)

1. **Create configuration file:**
   ```bash
   cp config_example.py config.py
   ```

2. **Edit config.py with your credentials:**
   ```python
   import os

   UHC_API_BASE_URL = "https://apimarketplace.uhc.com/Eligibility"
   UHC_CLIENT_ID = os.getenv("UHC_CLIENT_ID", "your-actual-client-id")
   UHC_CLIENT_SECRET = os.getenv("UHC_CLIENT_SECRET", "your-actual-client-secret")
   UHC_OAUTH_URL = "https://apimarketplace.uhc.com/v1/oauthtoken"
   TOKEN_FILE = "uhc_oauth_token.json"
   ```

3. **Run the app:**
   ```bash
   streamlit run streamlit_app.py
   ```

### Option 2: Using Environment Variables

1. **Set environment variables:**
   ```bash
   # On Windows
   set UHC_CLIENT_ID=your-actual-client-id
   set UHC_CLIENT_SECRET=your-actual-client-secret

   # On macOS/Linux
   export UHC_CLIENT_ID=your-actual-client-id
   export UHC_CLIENT_SECRET=your-actual-client-secret
   ```

2. **Run the app:**
   ```bash
   streamlit run streamlit_app.py
   ```

## Troubleshooting

### Common Issues

1. **"UHC API credentials not found" Error:**
   - **Streamlit Cloud:** Check that secrets are properly set in advanced settings
   - **Local:** Verify config.py exists and has correct credentials, or environment variables are set

2. **"Module 'config' not found" (Local Development):**
   - Create config.py from config_example.py
   - Or set environment variables as shown above

3. **OAuth Token Generation Fails:**
   - Verify client ID and secret are correct
   - Check that you have access to the UHC API sandbox environment
   - Ensure network connectivity to UHC API endpoints

4. **App Won't Start on Streamlit Cloud:**
   - Check the logs in Streamlit Cloud
   - Verify all required packages are in requirements.txt
   - Ensure the main file path is set to `streamlit_app.py`

### Logs and Debugging

- **Streamlit Cloud:** View logs in the app management interface
- **Local:** Check the terminal where you ran `streamlit run`

## Security Best Practices

1. **Never commit sensitive data:**
   - config.py is excluded by .gitignore
   - Always use environment variables or Streamlit secrets for credentials

2. **Token Management:**
   - OAuth tokens are automatically refreshed
   - Token files are excluded from version control

3. **API Rate Limiting:**
   - The app handles token expiration automatically
   - Consider implementing rate limiting for production use

## Updates and Maintenance

### Updating the Deployed App

1. **Make changes locally and test**
2. **Commit and push to GitHub:**
   ```bash
   git add .
   git commit -m "Description of changes"
   git push origin main
   ```
3. **Streamlit Cloud automatically redeploys** when you push to the main branch

### Updating Dependencies

1. **Update requirements.txt** if you add new packages
2. **Test locally** before deploying
3. **Commit and push** to trigger redeployment

## Support

- **UHC API Issues:** Contact your UHC API representative
- **Streamlit Cloud Issues:** Check [Streamlit documentation](https://docs.streamlit.io)
- **Application Issues:** Review logs and check this deployment guide 