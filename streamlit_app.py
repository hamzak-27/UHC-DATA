import streamlit as st
import requests
import json
import time
from datetime import datetime, timedelta
import base64
import os

# Import configuration
try:
    from config import UHC_API_BASE_URL, UHC_CLIENT_ID, UHC_CLIENT_SECRET, UHC_OAUTH_URL, TOKEN_FILE
except ImportError:
    # Fallback for deployment - use environment variables or Streamlit secrets
    UHC_API_BASE_URL = "https://apimarketplace.uhc.com/Eligibility"
    UHC_OAUTH_URL = "https://apimarketplace.uhc.com/v1/oauthtoken"
    TOKEN_FILE = "uhc_oauth_token.json"
    
    # Try Streamlit secrets first, then environment variables
    try:
        UHC_CLIENT_ID = st.secrets["UHC_CLIENT_ID"]
        UHC_CLIENT_SECRET = st.secrets["UHC_CLIENT_SECRET"]
    except (KeyError, FileNotFoundError):
        UHC_CLIENT_ID = os.getenv("UHC_CLIENT_ID")
        UHC_CLIENT_SECRET = os.getenv("UHC_CLIENT_SECRET")
    
    if not UHC_CLIENT_ID or not UHC_CLIENT_SECRET:
        st.error("❌ UHC API credentials not found. Please set UHC_CLIENT_ID and UHC_CLIENT_SECRET in Streamlit secrets or environment variables.")
        st.info("For Streamlit Cloud: Add credentials in the 'Secrets' section of your app settings.")
        st.info("For local development: Create a config.py file based on config_example.py")
        st.stop()

def save_token_to_file(token, expires_at):
    """Save OAuth token to local file for persistence"""
    try:
        token_data = {
            'oauth_token': token,
            'expires_at': expires_at.isoformat() if expires_at else None,
            'saved_at': datetime.now().isoformat()
        }
        with open(TOKEN_FILE, 'w') as f:
            json.dump(token_data, f)
    except Exception as e:
        st.warning(f"Could not save token to file: {str(e)}")

def load_token_from_file():
    """Load OAuth token from local file"""
    try:
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, 'r') as f:
                token_data = json.load(f)
            
            oauth_token = token_data.get('oauth_token')
            expires_at_str = token_data.get('expires_at')
            
            if oauth_token and expires_at_str:
                expires_at = datetime.fromisoformat(expires_at_str)
                
                # Check if token is still valid (with 5 minute buffer)
                if datetime.now() + timedelta(minutes=5) < expires_at:
                    return oauth_token, expires_at
                else:
                    # Token expired, remove the file
                    os.remove(TOKEN_FILE)
                    return None, None
            
    except Exception as e:
        st.warning(f"Could not load token from file: {str(e)}")
    
    return None, None

def delete_token_file():
    """Delete the token file"""
    try:
        if os.path.exists(TOKEN_FILE):
            os.remove(TOKEN_FILE)
    except Exception as e:
        st.warning(f"Could not delete token file: {str(e)}")

# Initialize session state for token management
# Try to load existing token first
if 'oauth_token' not in st.session_state:
    saved_token, saved_expires = load_token_from_file()
    st.session_state.oauth_token = saved_token
    st.session_state.token_expires_at = saved_expires
    st.session_state.token_generated = saved_token is not None

if 'token_expires_at' not in st.session_state:
    st.session_state.token_expires_at = None
if 'token_generated' not in st.session_state:
    st.session_state.token_generated = False

def generate_oauth_token():
    """Generate OAuth token using client credentials - matches Postman implementation"""
    try:
        # Use the exact format that works in Postman
        url = "https://apimarketplace.uhc.com/v1/oauthtoken"
        
        # Headers as specified in Postman
        headers = {
            'Content-Type': 'application/json',
            'env': 'sandbox'
        }
        
        # Body as JSON with client credentials
        payload = {
            'client_id': UHC_CLIENT_ID,
            'client_secret': UHC_CLIENT_SECRET,
            'grant_type': 'client_credentials'
        }
        
        # Make the request
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get('access_token')
            expires_in = int(token_data.get('expires_in', 3599))
            
            # Store token and expiration time in session state
            st.session_state.oauth_token = f"Bearer {access_token}"
            st.session_state.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
            st.session_state.token_generated = True
            
            # Save token to file for persistence
            save_token_to_file(st.session_state.oauth_token, st.session_state.token_expires_at)
            
            return {
                'success': True,
                'token': st.session_state.oauth_token,
                'expires_at': st.session_state.token_expires_at,
                'data': token_data,
                'method': 'Postman-style JSON request'
            }
        else:
            return {
                'success': False,
                'error': f"Failed to generate token. Status: {response.status_code}, Response: {response.text}",
                'status_code': response.status_code
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': f"Error generating token: {str(e)}",
            'status_code': 500
        }

def is_token_valid():
    """Check if the current token is still valid"""
    if not st.session_state.oauth_token or not st.session_state.token_expires_at:
        return False
    
    # Check if token expires in the next 5 minutes (buffer time)
    buffer_time = timedelta(minutes=5)
    return datetime.now() + buffer_time < st.session_state.token_expires_at

def get_api_headers():
    """Get headers for API requests"""
    return {
        'Authorization': st.session_state.oauth_token,
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-API-Key': UHC_CLIENT_ID,
        'Client-Id': UHC_CLIENT_ID,
        'env': 'sandbox'  # Add sandbox environment header like OAuth
    }

def search_member_eligibility(member_id, date_of_birth, search_option='memberIDDateOfBirth', 
                            service_start=None, service_end=None, first_name=None, last_name=None,
                            payer_id=None, provider_last_name=None, tax_id_number=None):
    """Search for member eligibility information"""
    
    url = f"{UHC_API_BASE_URL}/api/external/member/eligibility/v3.0"
    
    payload = {
        "memberId": member_id,
        "dateOfBirth": date_of_birth,
        "searchOption": search_option,
        "payerID": payer_id or "",
        "providerLastName": provider_last_name or "",
        "taxIdNumber": tax_id_number or "",
        "firstName": first_name or "",
        "lastName": last_name or ""
    }
    
    if service_start:
        payload["serviceStart"] = service_start
    if service_end:
        payload["serviceEnd"] = service_end
    
    try:
        headers = get_api_headers()
        
        # Debug information
        st.write("📤 **Eligibility API Request Details:**")
        st.write(f"URL: {url}")
        st.write("Headers:")
        st.json({k: v if k != 'Authorization' else f"{v[:20]}..." for k, v in headers.items()})
        st.write("Payload:")
        st.json(payload)
        
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=30)
        
        st.write(f"📥 **Response Status:** {response.status_code}")
        
        if response.status_code == 200:
            return {
                'success': True,
                'data': response.json(),
                'status_code': response.status_code
            }
        else:
            error_data = {}
            try:
                error_data = response.json()
            except:
                error_data = {'message': response.text}
            
            # Show error response for debugging
            st.write("📥 **Error Response:**")
            st.json(error_data)
            st.write("📥 **Raw Response Text:**")
            st.code(response.text)
            
            return {
                'success': False,
                'error': error_data,
                'status_code': response.status_code
            }
            
    except requests.exceptions.Timeout:
        return {
            'success': False,
            'error': {'message': 'Request timed out. Please try again.'},
            'status_code': 408
        }
    except Exception as e:
        return {
            'success': False,
            'error': {'message': f'Unexpected error: {str(e)}'},
            'status_code': 500
        }

def check_network_status(member_id, date_of_birth, provider_last_name, 
                       first_date_of_service, last_date_of_service, 
                       transaction_id=None, provider_first_name=None, 
                       provider_tin=None, provider_npi=None, first_name=None):
    """Check provider network status"""
    
    url = f"{UHC_API_BASE_URL}/api/external/networkStatus/v4.0"
    
    payload = {
        "memberId": member_id,
        "dateOfBirth": date_of_birth,
        "providerLastName": provider_last_name,
        "firstDateOfService": first_date_of_service,
        "lastDateOfService": last_date_of_service,
        "familyIndicator": "N",
        "payerID": "",
        "taxIdNumber": "",
        "firstName": "",
        "lastName": ""
    }
    
    if transaction_id:
        payload["transactionId"] = transaction_id
    if provider_first_name:
        payload["providerFirstName"] = provider_first_name
    if provider_tin:
        payload["providerTin"] = provider_tin
    if provider_npi:
        payload["providerNpi"] = provider_npi
    if first_name:
        payload["firstName"] = first_name
    
    if not transaction_id:
        payload["providerMpin"] = ""
    
    try:
        headers = get_api_headers()
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=30)
        
        if response.status_code == 200:
            return {
                'success': True,
                'data': response.json(),
                'status_code': response.status_code
            }
        else:
            error_data = {}
            try:
                error_data = response.json()
                if isinstance(error_data, list) and len(error_data) > 0:
                    error_data = error_data[0]
            except:
                error_data = {'message': response.text}
            
            return {
                'success': False,
                'error': error_data,
                'status_code': response.status_code
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': {'message': f'Unexpected error: {str(e)}'},
            'status_code': 500
        }

def get_copay_coinsurance_details(patient_key, transaction_id):
    """Get copay and coinsurance details"""
    
    url = f"{UHC_API_BASE_URL}/api/external/member/copay/v2.0"
    
    payload = {
        "patientKey": patient_key,
        "transactionId": transaction_id
    }
    
    try:
        headers = get_api_headers()
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=30)
        
        if response.status_code == 200:
            return {
                'success': True,
                'data': response.json(),
                'status_code': response.status_code
            }
        else:
            error_data = {}
            try:
                error_data = response.json()
            except:
                error_data = {'message': response.text}
            
            return {
                'success': False,
                'error': error_data,
                'status_code': response.status_code
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': {'message': f'Unexpected error: {str(e)}'},
            'status_code': 500
        }

def format_date_to_us(date_string):
    """Convert date string to MM/DD/YYYY format"""
    if not date_string or date_string == 'N/A':
        return 'N/A'
    
    try:
        # Try different date formats that might be returned by the API
        formats_to_try = [
            '%Y-%m-%d',      # YYYY-MM-DD
            '%m/%d/%Y',      # MM/DD/YYYY (already correct)
            '%d/%m/%Y',      # DD/MM/YYYY
            '%Y%m%d',        # YYYYMMDD
            '%m-%d-%Y',      # MM-DD-YYYY
            '%d-%m-%Y',      # DD-MM-YYYY
        ]
        
        for fmt in formats_to_try:
            try:
                date_obj = datetime.strptime(date_string, fmt)
                return date_obj.strftime('%m/%d/%Y')
            except ValueError:
                continue
        
        # If no format works, return the original string
        return date_string
        
    except Exception:
        return date_string

def display_formatted_eligibility_results(data):
    """Display eligibility results in a formatted, user-friendly way"""
    
    st.subheader("📋 Eligibility Search Results")
    
    # Basic member information
    st.markdown("### 👤 Member Information")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        member_id = data.get('memberId', 'N/A')
        st.metric("Member ID", member_id)
    
    with col2:
        search_status = data.get('searchStatus', 'N/A')
        st.metric("Search Status", search_status)
    
    with col3:
        transaction_id = data.get('transactionId', 'N/A')
        st.metric("Transaction ID", transaction_id)
    
    # Process member policies
    if 'memberPolicies' in data and len(data['memberPolicies']) > 0:
        for idx, policy in enumerate(data['memberPolicies']):
            st.markdown(f"### 🏥 Policy {idx + 1}")
            
            # Patient Demographics
            if 'patientInfo' in policy and policy['patientInfo']:
                patient_info = policy['patientInfo'][0]
                
                st.markdown("#### 📝 Patient Demographics")
                demo_col1, demo_col2, demo_col3 = st.columns(3)
                
                with demo_col1:
                    first_name = patient_info.get('firstName', 'N/A')
                    last_name = patient_info.get('lastName', 'N/A')
                    middle_name = patient_info.get('middleName', '')
                    full_name = f"{first_name} {middle_name} {last_name}".strip()
                    st.info(f"**Name:** {full_name}")
                    
                    dob = patient_info.get('dateOfBirth', 'N/A')
                    formatted_dob = format_date_to_us(dob)
                    st.info(f"**Date of Birth:** {formatted_dob}")
                    
                    gender = patient_info.get('gender', 'N/A')
                    st.info(f"**Gender:** {gender}")
                
                with demo_col2:
                    relationship = patient_info.get('relationship', 'N/A')
                    st.info(f"**Relationship:** {relationship}")
                    
                    patient_key = patient_info.get('patientKey', 'N/A')
                    st.info(f"**Patient Key:** {patient_key}")
                    
                    subscriber_bool = patient_info.get('subscriberBoolean', 'N/A')
                    st.info(f"**Subscriber:** {'Yes' if subscriber_bool else 'No'}")
                
                with demo_col3:
                    address1 = patient_info.get('addressLine1', 'N/A')
                    address2 = patient_info.get('addressLine2', '')
                    city = patient_info.get('city', 'N/A')
                    state = patient_info.get('state', 'N/A')
                    zip_code = patient_info.get('zip', 'N/A')
                    
                    address = f"{address1}"
                    if address2:
                        address += f", {address2}"
                    address += f", {city}, {state} {zip_code}"
                    st.info(f"**Address:** {address}")
            
            # Insurance Information
            if 'insuranceInfo' in policy:
                insurance_info = policy['insuranceInfo']
                st.markdown("#### 🏥 Insurance Information")
                
                ins_col1, ins_col2, ins_col3 = st.columns(3)
                
                with ins_col1:
                    payer_name = insurance_info.get('payerName', 'N/A')
                    st.info(f"**Payer Name:** {payer_name}")
                    
                    member_id = insurance_info.get('memberId', 'N/A')
                    st.info(f"**Member ID:** {member_id}")
                    
                    group_number = insurance_info.get('groupNumber', 'N/A')
                    st.info(f"**Group Number:** {group_number}")
                
                with ins_col2:
                    insurance_type = insurance_info.get('insuranceType', 'N/A')
                    st.info(f"**Insurance Type:** {insurance_type}")
                    
                    plan_description = insurance_info.get('planDescription', 'N/A')
                    st.info(f"**Plan Description:** {plan_description}")
                    
                    payer_status = insurance_info.get('payerStatus', 'N/A')
                    st.info(f"**Payer Status:** {payer_status}")
                
                with ins_col3:
                    line_of_business = insurance_info.get('lineOfBusiness', 'N/A')
                    st.info(f"**Line of Business:** {line_of_business}")
                    
                    payer_id = insurance_info.get('payerId', 'N/A')
                    st.info(f"**Payer ID:** {payer_id}")
                    
                    platform = insurance_info.get('platform', 'N/A')
                    st.info(f"**Platform:** {platform}")
            
            # Policy Information
            if 'policyInfo' in policy:
                policy_info = policy['policyInfo']
                st.markdown("#### 📋 Policy Information")
                
                pol_col1, pol_col2, pol_col3 = st.columns(3)
                
                with pol_col1:
                    policy_status = policy_info.get('policyStatus', 'N/A')
                    st.info(f"**Policy Status:** {policy_status}")
                    
                    coverage_type = policy_info.get('coverageType', 'N/A')
                    st.info(f"**Coverage Type:** {coverage_type}")
                
                with pol_col2:
                    if 'eligibilityDates' in policy_info:
                        elig_dates = policy_info['eligibilityDates']
                        start_date = format_date_to_us(elig_dates.get('startDate', 'N/A'))
                        end_date = format_date_to_us(elig_dates.get('endDate', 'N/A'))
                        st.info(f"**Eligibility Period:** {start_date} to {end_date}")
                
                with pol_col3:
                    if 'planDates' in policy_info:
                        plan_dates = policy_info['planDates']
                        plan_start = format_date_to_us(plan_dates.get('startDate', 'N/A'))
                        plan_end = format_date_to_us(plan_dates.get('endDate', 'N/A'))
                        st.info(f"**Plan Period:** {plan_start} to {plan_end}")
            
            # Plan Message
            if 'planMessage' in policy and policy['planMessage']:
                st.markdown("#### 💬 Plan Message")
                st.info(policy['planMessage'])
            
            # Referral Information
            if 'referralInfo' in policy:
                referral_info = policy['referralInfo']
                st.markdown("#### 🔄 Referral Information")
                
                ref_col1, ref_col2 = st.columns(2)
                
                with ref_col1:
                    referral_indicator = referral_info.get('referralIndicator', 'N/A')
                    referral_needed = 'Yes' if referral_indicator == 'Y' else 'No' if referral_indicator == 'N' else referral_indicator
                    st.info(f"**Referral Required:** {referral_needed}")
                
                with ref_col2:
                    rlink_ebn = referral_info.get('rLinkEBN', 'N/A')
                    st.info(f"**rLink EBN:** {'Yes' if rlink_ebn else 'No' if rlink_ebn is False else rlink_ebn}")
            
            # Primary Care Physician Information
            if 'primaryCarePhysicianInfo' in policy:
                pcp_info = policy['primaryCarePhysicianInfo']
                if pcp_info.get('pcpFound') == 'true':
                    st.markdown("#### 👨‍⚕️ Primary Care Physician")
                    
                    pcp_col1, pcp_col2 = st.columns(2)
                    
                    with pcp_col1:
                        pcp_name = f"{pcp_info.get('firstName', '')} {pcp_info.get('middleName', '')} {pcp_info.get('lastName', '')}".strip()
                        st.info(f"**PCP Name:** {pcp_name}")
                        
                        provider_group = pcp_info.get('providerGroupName', 'N/A')
                        st.info(f"**Provider Group:** {provider_group}")
                    
                    with pcp_col2:
                        pcp_address = f"{pcp_info.get('addressLine1', '')}"
                        if pcp_info.get('addressLine2'):
                            pcp_address += f", {pcp_info.get('addressLine2')}"
                        pcp_address += f", {pcp_info.get('city', '')}, {pcp_info.get('state', '')} {pcp_info.get('zip', '')}"
                        st.info(f"**Address:** {pcp_address}")
                        
                        network_status = pcp_info.get('networkStatusCode', 'N/A')
                        st.info(f"**Network Status:** {network_status}")
            
            # Additional Coverage Information
            if 'additionalCoverageInfo' in policy and policy['additionalCoverageInfo']:
                additional_coverage = policy['additionalCoverageInfo'][0]
                if additional_coverage.get('additionalCoverage') != 'None':
                    st.markdown("#### ➕ Additional Coverage Information")
                    st.info(f"**Additional Coverage:** {additional_coverage.get('additionalCoverage', 'N/A')}")
            
            # Deductible Information
            if 'deductibleInfo' in policy:
                deductible_info = policy['deductibleInfo']
                if deductible_info.get('found'):
                    st.markdown("#### 💰 Deductible Information")
                    
                    if deductible_info.get('message'):
                        st.info(f"**Message:** {deductible_info['message']}")
                    
                    # Create deductible table
                    import pandas as pd
                    deductible_data = []
                    
                    # Individual deductibles
                    individual = deductible_info.get('individual', {})
                    if individual.get('found'):
                        # In-Network
                        in_network = individual.get('inNetwork', {})
                        if in_network.get('found'):
                            deductible_data.append({
                                'Type': 'Individual In-Network',
                                'Plan Amount': f"${in_network.get('planAmount', '0')}{in_network.get('planAmountFrequency', '')}",
                                'Remaining': f"${in_network.get('remainingAmount', '0')}",
                                'Met YTD': f"${in_network.get('metYtdAmount', '0')}"
                            })
                        
                        # Out-of-Network
                        out_network = individual.get('outOfNetwork', {})
                        if out_network.get('found'):
                            deductible_data.append({
                                'Type': 'Individual Out-of-Network',
                                'Plan Amount': f"${out_network.get('planAmount', '0')}{out_network.get('planAmountFrequency', '')}",
                                'Remaining': f"${out_network.get('remainingAmount', '0')}",
                                'Met YTD': f"${out_network.get('metYtdAmount', '0')}"
                            })
                    
                    # Family deductibles
                    family = deductible_info.get('family', {})
                    if family.get('found'):
                        # In-Network
                        in_network = family.get('inNetwork', {})
                        if in_network.get('found'):
                            deductible_data.append({
                                'Type': 'Family In-Network',
                                'Plan Amount': f"${in_network.get('planAmount', '0')}{in_network.get('planAmountFrequency', '')}",
                                'Remaining': f"${in_network.get('remainingAmount', '0')}",
                                'Met YTD': f"${in_network.get('metYtdAmount', '0')}"
                            })
                        
                        # Out-of-Network
                        out_network = family.get('outOfNetwork', {})
                        if out_network.get('found'):
                            deductible_data.append({
                                'Type': 'Family Out-of-Network',
                                'Plan Amount': f"${out_network.get('planAmount', '0')}{out_network.get('planAmountFrequency', '')}",
                                'Remaining': f"${out_network.get('remainingAmount', '0')}",
                                'Met YTD': f"${out_network.get('metYtdAmount', '0')}"
                            })
                    
                    if deductible_data:
                        df_deductibles = pd.DataFrame(deductible_data)
                        st.dataframe(df_deductibles, use_container_width=True)
            
            # Out of Pocket Information
            if 'outOfPocketInfo' in policy:
                oop_info = policy['outOfPocketInfo']
                if oop_info.get('found'):
                    st.markdown("#### 🏦 Out of Pocket Information")
                    
                    if oop_info.get('message'):
                        st.info(f"**Message:** {oop_info['message']}")
                    
                    # Create out of pocket table
                    import pandas as pd
                    oop_data = []
                    
                    # Individual out of pocket
                    individual = oop_info.get('individual', {})
                    if individual.get('found'):
                        # In-Network
                        in_network = individual.get('inNetwork', {})
                        if in_network.get('found'):
                            oop_data.append({
                                'Type': 'Individual In-Network',
                                'Plan Amount': f"${in_network.get('planAmount', '0')}{in_network.get('planAmountFrequency', '')}",
                                'Remaining': f"${in_network.get('remainingAmount', '0')}",
                                'Met YTD': f"${in_network.get('metYtdAmount', '0')}"
                            })
                        
                        # Out-of-Network
                        out_network = individual.get('outOfNetwork', {})
                        if out_network.get('found'):
                            oop_data.append({
                                'Type': 'Individual Out-of-Network',
                                'Plan Amount': f"${out_network.get('planAmount', '0')}{out_network.get('planAmountFrequency', '')}",
                                'Remaining': f"${out_network.get('remainingAmount', '0')}",
                                'Met YTD': f"${out_network.get('metYtdAmount', '0')}"
                            })
                    
                    # Family out of pocket
                    family = oop_info.get('family', {})
                    if family.get('found'):
                        # In-Network
                        in_network = family.get('inNetwork', {})
                        if in_network.get('found'):
                            oop_data.append({
                                'Type': 'Family In-Network',
                                'Plan Amount': f"${in_network.get('planAmount', '0')}{in_network.get('planAmountFrequency', '')}",
                                'Remaining': f"${in_network.get('remainingAmount', '0')}",
                                'Met YTD': f"${in_network.get('metYtdAmount', '0')}"
                            })
                        
                        # Out-of-Network
                        out_network = family.get('outOfNetwork', {})
                        if out_network.get('found'):
                            oop_data.append({
                                'Type': 'Family Out-of-Network',
                                'Plan Amount': f"${out_network.get('planAmount', '0')}{out_network.get('planAmountFrequency', '')}",
                                'Remaining': f"${out_network.get('remainingAmount', '0')}",
                                'Met YTD': f"${out_network.get('metYtdAmount', '0')}"
                            })
                    
                    if oop_data:
                        df_oop = pd.DataFrame(oop_data)
                        st.dataframe(df_oop, use_container_width=True)
            
            # Copay Maximum Information
            if 'copayMaxInfo' in policy:
                copay_max_info = policy['copayMaxInfo']
                if copay_max_info.get('found'):
                    st.markdown("#### 💵 Copay Maximum Information")
                    
                    if copay_max_info.get('message'):
                        st.info(f"**Message:** {copay_max_info['message']}")
                    
                    # Create copay max table (similar structure as above)
                    import pandas as pd
                    copay_max_data = []
                    
                    # Individual copay max
                    individual = copay_max_info.get('individual', {})
                    if individual.get('found'):
                        in_network = individual.get('inNetwork', {})
                        if in_network.get('found'):
                            copay_max_data.append({
                                'Type': 'Individual In-Network',
                                'Plan Amount': f"${in_network.get('planAmount', '0')}{in_network.get('planAmountFrequency', '')}",
                                'Remaining': f"${in_network.get('remainingAmount', '0')}",
                                'Met YTD': f"${in_network.get('metYtdAmount', '0')}"
                            })
                    
                    if copay_max_data:
                        df_copay_max = pd.DataFrame(copay_max_data)
                        st.dataframe(df_copay_max, use_container_width=True)
                else:
                    if copay_max_info.get('message'):
                        st.markdown("#### 💵 Copay Maximum Information")
                        st.info(f"**Message:** {copay_max_info['message']}")
            
            # Out of Pocket Maximum Information (different from outOfPocketInfo)
            if 'outOfPocketMaxInfo' in policy:
                oop_max_info = policy['outOfPocketMaxInfo']
                if oop_max_info.get('found'):
                    st.markdown("#### 🏦 Out of Pocket Maximum Information")
                    
                    if oop_max_info.get('message'):
                        st.info(f"**Message:** {oop_max_info['message']}")
                else:
                    if oop_max_info.get('message'):
                        st.markdown("#### 🏦 Out of Pocket Maximum Information")
                        st.info(f"**Message:** {oop_max_info['message']}")
            
            # Copay Cap Information
            if policy.get('copayCapIndicator') or policy.get('copayCapMessage'):
                st.markdown("#### 🛡️ Copay Cap Information")
                
                copay_cap_col1, copay_cap_col2 = st.columns(2)
                
                with copay_cap_col1:
                    copay_cap_indicator = policy.get('copayCapIndicator', False)
                    st.info(f"**Copay Cap Applied:** {'Yes' if copay_cap_indicator else 'No'}")
                
                with copay_cap_col2:
                    if policy.get('copayCapMessage'):
                        st.info(f"**Copay Cap Message:** {policy['copayCapMessage']}")
            
            st.markdown("---")
    
    # Requesting Provider Information
    if 'requestingProvider' in data:
        requesting_provider = data['requestingProvider']
        st.markdown("### 🏥 Requesting Provider Information")
        
        req_col1, req_col2 = st.columns(2)
        
        with req_col1:
            provider_name = f"{requesting_provider.get('providerFirstName', '')} {requesting_provider.get('providerMiddleName', '')} {requesting_provider.get('providerLastName', '')}".strip()
            if not provider_name:
                provider_name = requesting_provider.get('organizationName', 'N/A')
            st.info(f"**Provider Name:** {provider_name}")
            
            organization_name = requesting_provider.get('organizationName', 'N/A')
            if organization_name and organization_name != provider_name:
                st.info(f"**Organization:** {organization_name}")
        
        with req_col2:
            npi = requesting_provider.get('npi', 'N/A')
            st.info(f"**NPI:** {npi}")
            
            tax_id = requesting_provider.get('taxIdNumber', 'N/A')
            st.info(f"**Tax ID:** {tax_id}")
    
    else:
        st.warning("⚠️ No member policies found in the response.")
    
    # Show raw JSON in expandable section
    with st.expander("🔍 View Raw JSON Response", expanded=False):
        st.json(data)

def main():
    st.set_page_config(
        page_title="UHC Eligibility & Network Status Checker",
        page_icon="🏥",
        layout="wide"
    )
    
    st.title("🏥 UHC Eligibility & Network Status Checker")
    st.markdown("---")
    
    # Sidebar for OAuth token management
    st.sidebar.header("🔐 OAuth Token Management")
    
    # Check token status
    token_valid = is_token_valid()
    
    if token_valid:
        st.sidebar.success("✅ Token is valid")
        expires_in = st.session_state.token_expires_at - datetime.now()
        st.sidebar.info(f"Expires in: {str(expires_in).split('.')[0]}")
        
        # Show if token was loaded from file
        if os.path.exists(TOKEN_FILE):
            st.sidebar.info("🔄 Token loaded from saved file")
    else:
        st.sidebar.warning("⚠️ Token expired or not generated")
    
    # Generate token button
    if st.sidebar.button("🔄 Generate OAuth Token", type="primary"):
        with st.sidebar:
            with st.spinner("Generating OAuth token..."):
                result = generate_oauth_token()
                
                if result['success']:
                    st.success("✅ Token generated successfully!")
                    st.info(f"Method used: {result.get('method', 'Unknown')}")
                    st.info(f"Token expires at: {result['expires_at'].strftime('%Y-%m-%d %H:%M:%S')}")
                else:
                    st.error(f"❌ Failed to generate token: {result['error']}")
    
    # Manual token entry as fallback
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔧 Manual Token Entry")
    st.sidebar.markdown("*Use this if automatic generation fails*")
    
    manual_token = st.sidebar.text_area(
        "Paste Bearer Token:",
        placeholder="Bearer eyJ0eXAiOiJKV1Q...",
        height=100
    )
    
    if st.sidebar.button("📝 Use Manual Token"):
        if manual_token and manual_token.startswith("Bearer "):
            st.session_state.oauth_token = manual_token
            # Set expiration to 1 hour from now
            st.session_state.token_expires_at = datetime.now() + timedelta(hours=1)
            st.session_state.token_generated = True
            
            # Save manual token to file for persistence
            save_token_to_file(st.session_state.oauth_token, st.session_state.token_expires_at)
            
            st.sidebar.success("✅ Manual token set successfully!")
        else:
            st.sidebar.error("❌ Please enter a valid Bearer token")
    
    # Clear token button
    if st.sidebar.button("🗑️ Clear Saved Token", help="Clear the saved token file"):
        st.session_state.oauth_token = None
        st.session_state.token_expires_at = None
        st.session_state.token_generated = False
        delete_token_file()
        st.sidebar.success("✅ Token cleared successfully!")
        st.rerun()
    
    # Show current token status
    if st.session_state.oauth_token:
        with st.sidebar.expander("📋 Token Details"):
            st.text("Token (first 50 chars):")
            st.code(st.session_state.oauth_token[:50] + "...")
            if st.session_state.token_expires_at:
                st.text(f"Expires: {st.session_state.token_expires_at.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Main content - Eligibility Search only
    st.header("🔍 Member Eligibility Search")
    
    # Show token status
    if not token_valid:
        st.warning("⚠️ Please generate an OAuth token first using the sidebar to perform searches.")
    else:
        st.success("✅ OAuth token is valid - ready to perform searches!")
    
    # Eligibility search form - always visible
    col1, col2 = st.columns(2)
    
    with col1:
        member_id = st.text_input("Member ID *", placeholder="Enter member ID")
        date_of_birth_str = st.text_input("Date of Birth *", placeholder="MM/DD/YYYY")
        first_name = st.text_input("First Name", placeholder="Optional")
        last_name = st.text_input("Last Name", placeholder="Optional")
    
    with col2:
        payer_id = st.text_input("Payer ID", placeholder="Optional")
        provider_last_name = st.text_input("Provider Last Name", placeholder="Optional")
        tax_id_number = st.text_input("Tax ID Number", placeholder="Optional")
        search_option = st.selectbox("Search Option", ["memberIDDateOfBirth"])
    
        # Submit button - check token validity on click
    if st.button("🔍 Search Eligibility", type="primary", disabled=not token_valid):
        if not token_valid:
            st.error("❌ Cannot perform search: OAuth token is required. Please generate a token first.")
        elif member_id and date_of_birth_str:
            # Validate and convert date format
            try:
                # Parse MM/DD/YYYY format
                date_of_birth = datetime.strptime(date_of_birth_str, '%m/%d/%Y')
                
                # Show debug information
                st.info(f"🔍 Searching for Member ID: {member_id}")
                st.info(f"📅 Date of Birth: {date_of_birth.strftime('%m/%d/%Y')} (API format: {date_of_birth.strftime('%Y-%m-%d')})")
                
                with st.spinner("Searching member eligibility..."):
                    result = search_member_eligibility(
                        member_id=member_id,
                        date_of_birth=date_of_birth.strftime('%Y-%m-%d'),
                        search_option=search_option,
                        first_name=first_name or None,
                        last_name=last_name or None,
                        payer_id=payer_id or None,
                        provider_last_name=provider_last_name or None,
                        tax_id_number=tax_id_number or None
                    )
                
                if result['success']:
                    st.success("✅ Eligibility search completed successfully!")
                    
                    # Store results in session state
                    st.session_state.eligibility_result = result['data']
                    st.session_state.member_id = member_id
                    st.session_state.date_of_birth = date_of_birth.strftime('%Y-%m-%d')
                    
                    # Display formatted results
                    display_formatted_eligibility_results(result['data'])
                
                else:
                    st.error(f"❌ Search failed: {result['error'].get('message', 'Unknown error')}")
                    st.json(result['error'])
                    
            except ValueError:
                st.error("❌ Invalid date format. Please enter date in MM/DD/YYYY format (e.g., 01/15/1990)")
            except Exception as e:
                st.error(f"❌ Error processing date: {str(e)}")
        else:
            st.error("❌ Please fill in Member ID and Date of Birth")
    
    # Footer
    st.markdown("---")
    st.markdown("*UHC Eligibility & Network Status Checker - Built with Streamlit*")

if __name__ == "__main__":
    main()