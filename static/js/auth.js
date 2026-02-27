document.addEventListener('DOMContentLoaded', () => {
    
    // 1. Extract the parameters from the URL fragment (after the #)
    function getHashParams() {
        const hash = window.location.hash.substring(1);
        const params = {};
        if (hash) {
            hash.split('&').forEach(pair => {
                const [key, value] = pair.split('=');
                params[key] = decodeURIComponent(value);
            });
        }
        return params;
    }

    const params = getHashParams();

    // 2. If the URL contains an access token and username, initiate the login process
    if (params.access_token && params.username) {
        authenticateWithServer(params.access_token, params.username);
    }

    // 3. Send the extracted data to our backend to establish a session
    function authenticateWithServer(token, username) {
        
        // This is the specific POST request the student needs to intercept!
        fetch('/api/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                access_token: token,
                username: username
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Clear the hash from the URL for a cleaner look
                window.history.replaceState(null, null, window.location.pathname);
                // Redirect to the protected dashboard
                window.location.href = '/dashboard';
            } else {
                displayError(data.message || "Authentication failed. The token may be invalid.");
            }
        })
        .catch(error => {
            console.error("Fetch error:", error);
            displayError("A network error occurred while communicating with the server.");
        });
    }

    // 4. Helper function to show errors on the page
    function displayError(message) {
        const errorContainer = document.getElementById('error-container');
        if (errorContainer) {
            errorContainer.textContent = message;
            errorContainer.classList.remove('hidden');
        } else {
            // Fallback if the container isn't in the DOM
            alert("Error: " + message);
        }
    }
});