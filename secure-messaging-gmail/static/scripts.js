// Modal Handling
const registerModal = document.getElementById("register-modal");
const exchangeModal = document.getElementById("exchange-modal");
const registerBtn = document.getElementById("register-btn");
const exchangeBtn = document.getElementById("exchange-btn");
const registerClose = document.getElementById("register-close");
const exchangeClose = document.getElementById("exchange-close");

registerBtn.onclick = function() {
    registerModal.style.display = "block";
}
exchangeBtn.onclick = function() {
    exchangeModal.style.display = "block";
}
registerClose.onclick = function() {
    registerModal.style.display = "none";
}
exchangeClose.onclick = function() {
    exchangeModal.style.display = "none";
}
window.onclick = function(event) {
    if (event.target == registerModal) {
        registerModal.style.display = "none";
    }
    if (event.target == exchangeModal) {
        exchangeModal.style.display = "none";
    }
}

// Loader Handling
function showLoader() {
    document.getElementById('loader').style.display = 'block';
}

function hideLoader() {
    document.getElementById('loader').style.display = 'none';
}

// Chat Handling
function addMessageToChat(message, type) {
    const chatMessages = document.getElementById('chat-messages');
    const messageElement = document.createElement('div');
    messageElement.classList.add('chat-message', type);
    messageElement.textContent = message;
    chatMessages.appendChild(messageElement);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Form Submissions
document.getElementById('register-form').addEventListener('submit', async function(event) {
    event.preventDefault();
    showLoader();
    const email = document.getElementById('register-email').value;
    const response = await fetch('/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email })
    });
    const data = await response.json();
    hideLoader();
    alert(data.message);
    registerModal.style.display = 'none';
});

document.getElementById('exchange-form').addEventListener('submit', async function(event) {
    event.preventDefault();
    showLoader();
    const email = document.getElementById('exchange-email').value;
    const recipientEmail = document.getElementById('exchange-recipient-email').value;
    const response = await fetch('/exchange', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email, recipient_email: recipientEmail })
    });
    const data = await response.json();
    hideLoader();
    if (response.status === 200) {
        alert('Derived Key: ' + data.key);
    } else {
        alert(data.message);
    }
    exchangeModal.style.display = 'none';
});

document.getElementById('send-form').addEventListener('submit', async function(event) {
    event.preventDefault();
    showLoader();
    const email = document.getElementById('send-email').value;
    const recipientEmail = document.getElementById('send-recipient-email').value;
    const message = document.getElementById('send-message').value;
    const response = await fetch('/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email, recipient_email: recipientEmail, message: message })
    });
    const data = await response.json();
    hideLoader();
    if (response.status === 200) {
        addMessageToChat('Me: ' + message, 'sent');
    }
    alert(data.message);
});
