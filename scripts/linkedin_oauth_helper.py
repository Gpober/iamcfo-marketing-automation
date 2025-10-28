#!/usr/bin/env python3
"""
LinkedIn OAuth Helper
Generates an access token for LinkedIn API access
Author: Greg Pober
"""

import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import webbrowser
import requests

# LinkedIn OAuth Configuration
CLIENT_ID = input("Enter your LinkedIn Client ID: ").strip()
CLIENT_SECRET = input("Enter your LinkedIn Client Secret: ").strip()
REDIRECT_URI = "http://localhost:8080/callback"
SCOPES = "openid profile email w_member_social w_organization_social r_organization_social"

# Global variable to store the authorization code
auth_code = None

class OAuthHandler(BaseHTTPRequestHandler):
    """HTTP server to capture OAuth callback"""
    
    def do_GET(self):
        global auth_code
        
        # Parse the callback URL
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        
        if 'code' in params:
            auth_code = params['code'][0]
            
            # Send success response
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"""
                <html>
                    <body style="font-family: Arial; text-align: center; padding: 50px;">
                        <h1 style="color: #00BFFF;">Success! ✅</h1>
                        <p>Authorization successful! You can close this window.</p>
                        <p>Go back to your terminal to complete the setup.</p>
                    </body>
                </html>
            """)
        else:
            # Error response
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            error = params.get('error_description', ['Unknown error'])[0]
            self.wfile.write(f"""
                <html>
                    <body style="font-family: Arial; text-align: center; padding: 50px;">
                        <h1 style="color: #ff0000;">Error ❌</h1>
                        <p>{error}</p>
                    </body>
                </html>
            """.encode())
    
    def log_message(self, format, *args):
        # Suppress server logs
        pass

def get_authorization_code():
    """Step 1: Get authorization code from user"""
    global auth_code
    
    # Build authorization URL
    auth_url = (
        f"https://www.linkedin.com/oauth/v2/authorization?"
        f"response_type=code&"
        f"client_id={CLIENT_ID}&"
        f"redirect_uri={urllib.parse.quote(REDIRECT_URI)}&"
        f"scope={urllib.parse.quote(SCOPES)}"
    )
    
    print("\n" + "=" * 60)
    print("🔐 STEP 1: AUTHORIZE ACCESS")
    print("=" * 60)
    print("\nOpening browser for LinkedIn authorization...")
    print("\n⚠️  IMPORTANT:")
    print("1. You'll be redirected to LinkedIn")
    print("2. Sign in if needed")
    print("3. Click 'Allow' to authorize the app")
    print("4. You'll be redirected back automatically")
    print("\nIf browser doesn't open, copy this URL:")
    print(f"\n{auth_url}\n")
    
    # Open browser
    webbrowser.open(auth_url)
    
    # Start local server to capture callback
    print("Starting local server on port 8080...")
    print("Waiting for authorization...\n")
    
    server = HTTPServer(('localhost', 8080), OAuthHandler)
    
    # Wait for one request (the callback)
    while auth_code is None:
        server.handle_request()
    
    return auth_code

def exchange_code_for_token(code):
    """Step 2: Exchange authorization code for access token"""
    
    print("\n" + "=" * 60)
    print("🔑 STEP 2: EXCHANGE CODE FOR TOKEN")
    print("=" * 60)
    
    token_url = "https://www.linkedin.com/oauth/v2/accessToken"
    
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI
    }
    
    try:
        response = requests.post(token_url, data=data)
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data['access_token']
            expires_in = token_data.get('expires_in', 'unknown')
            
            print(f"\n✅ Success! Access token generated!")
            print(f"⏰ Expires in: {expires_in} seconds (~60 days)")
            
            return access_token
        else:
            print(f"\n❌ Error getting token:")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"\n❌ Exception: {e}")
        return None

def get_organization_id(access_token):
    """Step 3: Get organization ID for your company page"""
    
    print("\n" + "=" * 60)
    print("🏢 STEP 3: GET ORGANIZATION ID")
    print("=" * 60)
    
    # First get user info to find organizations
    url = "https://api.linkedin.com/v2/organizationAcls?q=roleAssignee"
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'X-Restli-Protocol-Version': '2.0.0'
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            elements = data.get('elements', [])
            
            if elements:
                print(f"\n✅ Found {len(elements)} organization(s):")
                for i, org in enumerate(elements, 1):
                    org_id = org.get('organization', '').split(':')[-1]
                    role = org.get('role', 'Unknown')
                    print(f"\n{i}. Organization ID: {org_id}")
                    print(f"   Role: {role}")
                
                # Return first org ID (usually your company)
                first_org_id = elements[0].get('organization', '').split(':')[-1]
                return first_org_id
            else:
                print("\n⚠️  No organizations found")
                print("Make sure you're an admin of your company page!")
                return None
        else:
            print(f"\n❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"\n❌ Exception: {e}")
        return None

def main():
    """Main execution"""
    print("\n" + "=" * 60)
    print("🚀 LINKEDIN OAUTH HELPER")
    print("=" * 60)
    print("\nThis script will help you generate a LinkedIn access token")
    print("for the I AM CFO social automation system.")
    print("\n⚠️  Make sure you've added http://localhost:8080/callback")
    print("to your app's redirect URLs in LinkedIn Developer Portal!")
    
    input("\nPress Enter to continue...")
    
    # Step 1: Get authorization code
    code = get_authorization_code()
    
    if not code:
        print("\n❌ Failed to get authorization code")
        return
    
    # Step 2: Exchange for access token
    access_token = exchange_code_for_token(code)
    
    if not access_token:
        print("\n❌ Failed to get access token")
        return
    
    # Step 3: Get organization ID
    org_id = get_organization_id(access_token)
    
    # Show final results
    print("\n" + "=" * 60)
    print("🎉 SUCCESS! YOUR CREDENTIALS:")
    print("=" * 60)
    
    print("\n📋 Add these to your GitHub Secrets:")
    print(f"\nLINKEDIN_ACCESS_TOKEN={access_token}")
    
    if org_id:
        print(f"LINKEDIN_ORG_ID={org_id}")
    else:
        print(f"LINKEDIN_ORG_ID=<find this manually>")
    
    print("\n" + "=" * 60)
    print("📝 NEXT STEPS:")
    print("=" * 60)
    print("\n1. Go to your GitHub repo:")
    print("   https://github.com/gpober/iamcfo-marketing-automation/settings/secrets/actions")
    print("\n2. Click 'New repository secret'")
    print("\n3. Add LINKEDIN_ACCESS_TOKEN (paste value above)")
    print("\n4. Add LINKEDIN_ORG_ID (paste value above)")
    print("\n5. Your bot is ready to post automatically!")
    print("\n⚠️  Note: This token expires in ~60 days.")
    print("You'll need to regenerate it when it expires.")
    print("=" * 60)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
