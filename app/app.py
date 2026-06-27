from flask import Flask, render_template, jsonify, redirect, request, session, url_for
import requests
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Required for session management

# Dummy OAuth Client Configuration -- replace with your real credentials
GOOGLE_OAUTH_CLIENT_ID = 'YOUR_GOOGLE_CLIENT_ID'
GOOGLE_OAUTH_CLIENT_SECRET = 'YOUR_GOOGLE_CLIENT_SECRET'
OUTLOOK_OAUTH_CLIENT_ID = 'YOUR_OUTLOOK_CLIENT_ID'
OUTLOOK_OAUTH_CLIENT_SECRET = 'YOUR_OUTLOOK_CLIENT_SECRET'

# OAuth endpoints and scopes (for demonstration; update as needed)
GOOGLE_AUTHORIZATION_URL = 'https://accounts.google.com/o/oauth2/auth'
GOOGLE_TOKEN_URL = 'https://oauth2.googleapis.com/token'
OUTLOOK_AUTHORIZATION_URL = 'https://login.microsoftonline.com/common/oauth2/v2.0/authorize'
OUTLOOK_TOKEN_URL = 'https://login.microsoftonline.com/common/oauth2/v2.0/token'



@app.route('/')
def index():
    google_email = session.get('google_email')
    print("Google Email in Session:", google_email)  # Debug output in your console
    return render_template('index.html', google_email=google_email)

@app.route('/connect/google')
def connect_google():
    # Build the Google OAuth URL
    google_auth_url = (
        f"{GOOGLE_AUTHORIZATION_URL}"
        
        f"&response_type=code"
        f"&redirect_uri={url_for('google_callback', _external=True)}"
        f"&scope=https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/userinfo.email"
    )
    return redirect(google_auth_url)

@app.route('/connect/google/callback')
def google_callback():
    code = request.args.get('code')
    if not code:
        return "Error: No code provided", 400

    data = {
        'code': code,
        
        'redirect_uri': url_for('google_callback', _external=True),
        'grant_type': 'authorization_code'
    }
    token_response = requests.post(GOOGLE_TOKEN_URL, data=data)
    token_json = token_response.json()
    access_token = token_json.get('access_token')
    if not access_token:
        return jsonify({"error": "Failed to exchange token", "details": token_json}), 400

    # ✅ Fetch user info
    userinfo_response = requests.get(
        'https://www.googleapis.com/oauth2/v3/userinfo',
        params={'alt': 'json'},
        headers={'Authorization': f'Bearer {access_token}'}
    )
    userinfo = userinfo_response.json()
    email = userinfo.get('email')

    # ✅ Save both token and email to session
    session['google_token'] = access_token
    session['google_email'] = email
    # Debug print to verify fetched email
    print("Fetched Google email:", email)
    
    # Store email in the session
    session['google_email'] = email

    return redirect(url_for('index'))


@app.route('/connect/outlook')
def connect_outlook():
    # Build the Outlook OAuth URL
    outlook_auth_url = (
        f"{OUTLOOK_AUTHORIZATION_URL}"
        f"?client_id={OUTLOOK_OAUTH_CLIENT_ID}"
        f"&response_type=code"
        f"&redirect_uri={url_for('outlook_callback', _external=True)}"
        f"&scope=Mail.Read"
    )
    return redirect(outlook_auth_url)

@app.route('/connect/outlook/callback')
def outlook_callback():
    code = request.args.get('code')
    if not code:
        return "Error: No code provided", 400

    # In production, exchange the code for an access token via a POST request.
    session['outlook_token'] = 'dummy_outlook_access_token'
    return redirect(url_for('index'))

def fetch_emails_from_gmail(token):
    # Dummy function: Replace with actual Gmail API calls
    # For example, GET https://www.googleapis.com/gmail/v1/users/me/messages?access_token=token
    return "Fetched emails from Gmail."

def fetch_emails_from_outlook(token):
    # Dummy function: Replace with Microsoft Graph API calls to fetch emails
    return "Fetched emails from Outlook."

def summarize_emails(all_emails_text):
    # Dummy function: In production, send the combined emails text
    # to an AI API (such as Llama 2) for summarization.
    return "This is a summarized version of your emails."

@app.route('/summarize', methods=['GET'])
def summarize():
    try:
        google_email_data = ""
        outlook_email_data = ""
        # Check if tokens exist in the session
        if 'google_token' in session:
            google_email_data = fetch_emails_from_gmail(session['google_token'])
        if 'outlook_token' in session:
            outlook_email_data = fetch_emails_from_outlook(session['outlook_token'])
        
        # Combine fetched emails; ensure a newline between sources
        combined_emails = f"{google_email_data}\n{outlook_email_data}"
        
        # Summarize combined emails using the summarization function
        summary = summarize_emails(combined_emails)
        return jsonify({"summary": summary})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)


