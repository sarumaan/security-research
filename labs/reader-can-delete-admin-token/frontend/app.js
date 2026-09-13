const API = "";

const tokenList = document.getElementById("tokenList");
const tokenCount = document.getElementById("tokenCount");
const resetButton = document.getElementById("resetButton");
const toast = document.getElementById("toast");
const loginScreen = document.getElementById("loginScreen");
const loginForm = document.getElementById("loginForm");
const loginError = document.getElementById("loginError");

async function login(event) {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    loginError.textContent = "";

    const response = await fetch(`${API}/login`, {
        method: "POST",
        credentials: "include",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            email,
            password
        })
    });

    if (!response.ok) {
        const data = await response.json();
        loginError.textContent =
            data.error || "Login failed.";
        return;
    }

    loginScreen.style.display = "none";

    await loadCurrentToken();
}

function showToast(message) {
    toast.textContent = message;
    toast.classList.add("show");

    setTimeout(() => {
        toast.classList.remove("show");
    }, 3000);
}

async function loadCurrentToken() {
    const response = await fetch(`${API}/api/v2/me/token`, {
        credentials: "include"
    });

    if (!response.ok) {
        showToast("Unable to load your token.");
        return;
    }

    const token = await response.json();

    tokenCount.textContent = "1";

    tokenList.innerHTML = `
        <div class="token-card">
            <div class="token-info">
                <div class="token-icon">◆</div>

                <div>
                    <div class="token-name">
                        ${token.name}
                        <span class="role-badge role-reader">
                            ${token.role}
                        </span>
                    </div>

                    <div class="token-owner">
                        ${token.email}
                        · Token ID ${token.id}
                    </div>
                </div>
            </div>

            <div class="token-actions">
                <button class="action-button" id="testOwnSession">
                    Test Session
                </button>
            </div>
        </div>
    `;

    document
        .getElementById("testOwnSession")
        .addEventListener("click", testSession);
}

async function testSession() {
    showToast("Testing session...");

    const response = await fetch(`${API}/api/v2/me`, {
        credentials: "include"
    });

    if (response.ok) {
        const data = await response.json();

        showToast(
            `Authenticated — ${data.user.role}`
        );
    } else if (response.status === 401) {
        showToast("Session is no longer valid.");
    } else {
        showToast(
            `Session test returned HTTP ${response.status}.`
        );
    }
}

async function resetLab() {
    const confirmed = confirm(
        "Reset the entire lab?\n\n" +
        "This restores the Admin and Reader accounts and tokens."
    );

    if (!confirmed) {
        return;
    }

    resetButton.disabled = true;
    showToast("Resetting lab...");

    const response = await fetch(
        `${API}/api/lab/reset`,
        {
            method: "POST"
        }
    );

    resetButton.disabled = false;

    if (response.ok) {
        showToast("Lab reset successfully.");
        await loadCurrentToken();
    } else {
        showToast(
            `Reset failed — HTTP ${response.status}`
        );
    }
}

resetButton.addEventListener("click", resetLab);
loginForm.addEventListener("submit", login);
async function resetFromLogin() {
    const confirmed = confirm(
        "Reset the entire lab?\n\n" +
        "This restores the Admin and Reader accounts and tokens."
    );

    if (!confirmed) {
        return;
    }

    loginResetButton.disabled = true;
    resetMessage.textContent = "Resetting lab...";

    const response = await fetch("/api/lab/reset", {
        method: "POST",
        credentials: "include"
    });

    loginResetButton.disabled = false;

    if (response.ok) {
        resetMessage.textContent =
            "Lab reset. Use the default Reader credentials to sign in.";
    } else {
        resetMessage.textContent =
            `Reset failed — HTTP ${response.status}`;
    }
}
loginResetButton.addEventListener("click", resetFromLogin);