async function getAuthorizationRequestURL(endpoint, mode) {
    let queryParams;
    if (mode) {
        queryParams = `?mode=${mode}`
    }
    else {
        queryParams = ''
    }
    try {
        let response = await fetch(`${endpoint}${queryParams}`);
        let data = await response.json();
        let url = data.url;
        return url;
    }
    catch (e) {
        return {
            error: true,
            message: e.message
        };
    }
}

function generateCodeVerifier(length = 43) {
    const possibleChars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~";
    const array = new Uint8Array(length);
    crypto.getRandomValues(array);

    return Array.from(array, byte => possibleChars[byte % possibleChars.length]).join('');
}

async function sha256(plain) {
    let encoder = new TextEncoder();
    let data = encoder.encode(plain);

    return window.crypto.subtle.digest('SHA-256', data); // hash from byte array
}

function base64UrlEncode(a) {
    return btoa(String.fromCharCode.apply(null, new Uint8Array(a)))
        .replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, ''); // symbols replace to make modified base64 for URL
}

async function login() {
    let AuthorizationRequestURL = await getAuthorizationRequestURL('/login/start', 'default');
    if (AuthorizationRequestURL?.error === true) {
        document.querySelector('#errors').innerText = AuthorizationRequestURL.message;
    }
    else {
        location.href = AuthorizationRequestURL;
    }
}

async function loginWithPKCE() {
    let codeVerifier = generateCodeVerifier();
    // let codeVerifier = '1234567890123456789012345678901234567890123456789012345678901234'; // for testing
    sessionStorage.setItem("codeVerifier", codeVerifier);
    let hashed = await sha256(codeVerifier);
    let codeChallenge = base64UrlEncode(hashed);
    let AuthorizationRequestURL = `${await getAuthorizationRequestURL('/login/start', 'pkce-front')}&code_challenge=${codeChallenge}&code_challenge_method=S256`;
    if (AuthorizationRequestURL?.error === true) {
        document.querySelector('#errors').innerText = AuthorizationRequestURL.message;
        return false;

    }

    location.href = AuthorizationRequestURL;

}

async function loginWithPKCEBack() {
    let AuthorizationRequestURL = await getAuthorizationRequestURL('/pkce/login/start');
    if (AuthorizationRequestURL?.error === true) {
        document.querySelector('#errors').innerText = AuthorizationRequestURL.message;
        return false;
    }
    location.href = AuthorizationRequestURL;

}

async function loginWithPKCEBackFormPost() {
    let AuthorizationRequestURL = await getAuthorizationRequestURL('/pkce/login/start', 'form-post');
    if (AuthorizationRequestURL?.error === true) {
        document.querySelector('#errors').innerText = AuthorizationRequestURL.message;
        return false;
    }
    location.href = AuthorizationRequestURL;

}



async function logout() {
    let response = await fetch('/logout', { method: 'POST' });
    if (response.status !== 200) {
        document.querySelector('#errors').innerText = 'Logout failed';
        return false;
    }

    location.reload();

}

async function requestAPI() {
    let response = await fetch('/api');
    let data = await response.json();
    document.querySelector('#api-response').innerText = JSON.stringify(data, null, 2);
}