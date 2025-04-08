# Demo OAuth app and attacker's server


Here is the demo PoC for the research *"Attacks via a New OAuth flow, Authorization Code Injection, and Whether HttpOnly, PKCE, and BFF Can Help"*. To work with it you'll need to set up any authorization server; **it's not included here**.

<mark>**This is not meant to be a real app. The code is provided for demonstration purposes only. Refrain from using code samples from this repo in your production applications.**</mark>

## Repo structure
- oauth_poc - demo app
- attacker_poc - demo attacker's server

## Setup

### TLS and secure contexts
TLS might be needed to provide a [secure context](https://developer.mozilla.org/en-US/docs/Web/Security/Secure_Contexts) to use `window.crypto.subtle.digest()` for creating code challenge on the frontend ("pkce-front" case).

However, that's not the only way to provide a secure context for the local app:
>Locally-delivered resources such as those with http://127.0.0.1 URLs, http://localhost and http://*.localhost URLs (e.g., http://dev.whatever.localhost/), and file:// URLs are also considered to have been delivered securely.

For more see [When is a context considered secure?](https://developer.mozilla.org/en-US/docs/Web/Security/Secure_Contexts#when_is_a_context_considered_secure)

**So, by default the TLS is disabled, but be sure to provide the secure context for your app or stub the code challenge generation, or skip this case completely.**

Whether the context is secure can be checked by accesing the `window.isSecureContext` property in your browser.

If you decide to use TLS, uncomment the specific section in `oauth_poc/app.py` and `attacker_poc/attacker.py` and provide valid TLS certificates to the application in `oauth_poc/config.py`. Also, do not forget to turn on TLS on your authorization server if you intend to try the iframe case.


### oauth_poc

1. Move to the `oauth_poc` directory
2. Create and activate a virtual env
```
python -m venv venv
source venv/bin/activate   # On windows use: venv\Scripts\activate
```
3. Install dependencies
```
pip install -r requirements.txt
```
4. Modify settings

In `oauth_poc/config.py` set the appropriate authorization server params and client settings.

You can also change the port in `oauth_poc/app.py`
```
if __name__ == '__main__':
    app.run(debug=True, host="127.0.0.1", port=5555
    )
```

**By default TLS is disabled.**

5. Serve the app
```
python app.py
```
### attacker_poc

1. Move to the `attacker_poc` directory
2. Create and activate a virtual env
```
python -m venv venv
source venv/bin/activate   # On windows use: venv\Scripts\activate
```
3. Install dependencies
```
pip install -r requirements.txt
```
4. Modify settings

In `attacker_poc/attacker.py` set the `APP_HOST` setting to match the host of the application you served.

In `attacker_poc/static/malicious/[1-4].js` change the `ATTACKER_HOST` const to match the host of the attacker's server.

Also, you'll need to change the attacker's server's host in the textarea in `oauth_poc/templates/xss.html`.

**By default TLS is disabled.**

5. Serve the app
```
python attacker.py
```
