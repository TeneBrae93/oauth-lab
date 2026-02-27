from flask import Flask, request, jsonify, render_template, redirect, session, url_for
import os
import uuid

app = Flask(__name__)
# In a real app this would be secure; for the lab, a hardcoded string is fine.
app.secret_key = 'super_secret_hack_smarter_key'

# --- MOCK DATABASE ---
# In reality, this would be a database table tracking valid access tokens and who they belong to.
valid_tokens = {}

# The flag the user is trying to get
FLAG = "HSM{1mpl1c1t_trU5t_1s_b4d_mkay}"

# --- ROUTES ---

@app.route('/')
def index():
    """Serves the main login page."""
    # If already logged in, send them to the dashboard
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

# --- MOCK OAUTH PROVIDER ROUTES ---

@app.route('/oauth/auth')
def oauth_auth():
    """
    Simulates the OAuth provider's authorization endpoint.
    This is where the user would normally enter their credentials and consent.
    """
    return render_template('mock_consent.html')

@app.route('/oauth/approve', methods=['POST'])
def oauth_approve():
    """
    Simulates the user clicking "Approve" on the consent screen.
    Generates an access token and redirects back with the Implicit Grant fragment.
    """
    # Simulate authenticating as the standard lab user
    standard_user = "wiener"
    
    # Generate a random token
    access_token = uuid.uuid4().hex
    
    # Store the token in our "database" and link it to the user.
    # (The vulnerable client app will ignore this linkage later!)
    valid_tokens[access_token] = standard_user
    
    # Implicit flow returns the token in the URL fragment (#)
    redirect_url = f"{url_for('index')}#access_token={access_token}&username={standard_user}"
    return redirect(redirect_url)


# --- VULNERABLE CLIENT APP ROUTES ---

@app.route('/api/login', methods=['POST'])
def api_login():
    """
    VULNERABLE ENDPOINT:
    Accepts the token and username from the frontend SPA.
    It checks if the token is valid, but DOES NOT verify if the token belongs to that specific user.
    """
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "Invalid request."}), 400
        
    client_token = data.get('access_token')
    client_username = data.get('username')
    
    # 1. Does the token exist in our system?
    if client_token in valid_tokens:
        # VULNERABILITY HERE: 
        # The server should check: if valid_tokens[client_token] == client_username:
        # But it doesn't! It just implicitly trusts the username sent by the client.
        
        # 2. Log the user in as whatever username they supplied
        session['username'] = client_username
        return jsonify({"success": True})
        
    else:
        return jsonify({"success": False, "message": "Invalid or expired access token."}), 401

@app.route('/dashboard')
def dashboard():
    """
    Protected area. Shows the flag if the user successfully impersonated 'administrator'.
    """
    if 'username' not in session:
        return redirect(url_for('index'))
        
    username = session['username']
    
    # Check if they successfully exploited the lab
    if username == 'administrator':
        flag = FLAG
    else:
        flag = None
        
    return render_template('dashboard.html', username=username, flag=flag)

@app.route('/logout')
def logout():
    """Clears the session."""
    session.pop('username', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Run the app. Listen on all interfaces and bind to port 80 (requires root).
    app.run(host='0.0.0.0', port=80, debug=True)