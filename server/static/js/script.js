document.getElementById('send-button').addEventListener('click', sendMessage);

function sendMessage() {
    const messageInput = document.getElementById('message-input');
    const message = messageInput.value;
    if (message.trim() === '') return;

    fetch('/send_message', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            sender: 'User', // Replace with actual sender username
            recipient: 'ChatBot',
            message: message,
        }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.message === 'Message sent') {
            const messagesDiv = document.getElementById('messages');
            const newMessage = document.createElement('div');
            newMessage.textContent = `You: ${message}`;
            messagesDiv.appendChild(newMessage);
            messageInput.value = '';
        } else {
            alert('Error sending message');
        }
    });
}
