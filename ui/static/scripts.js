let currentChannel = '';
let channelSelected = false;
let eventSource = null;

function detectChannel(userInput) {
    const confluenceRegex = /confluence/i;
    const serviceNowRegex = /servicenow|service now/i;

    if (confluenceRegex.test(userInput)) {
        currentChannel = 'confluence';
        return 'Confluence';
    } else if (serviceNowRegex.test(userInput)) {
        currentChannel = 'sn';
        return 'Service Now';
    }
    return null;
}

function botMessage(message) {
    const chatbox = document.getElementById('chatbox');
    chatbox.innerHTML += `<div class="message bot"><img src="/static/bot_icon.png" alt="Bot">${message}</div>`;
    chatbox.scrollTop = chatbox.scrollHeight; // Scroll to the latest message
}

async function sendMessage() {
    const userInput = document.getElementById('userInput').value.trim();
    if (userInput === "") return;

    const chatbox = document.getElementById('chatbox');
    chatbox.innerHTML += `<div class="message user"><img src="/static/user_icon.png" alt="User">${userInput}</div>`;
    chatbox.scrollTop = chatbox.scrollHeight; // Scroll to the latest message

    document.getElementById('userInput').value = ''; // Clear input box

    // If the channel is not selected, check user's input for keywords
    if (!channelSelected) {
        const detectedChannel = detectChannel(userInput);

        if (detectedChannel) {
            channelSelected = true;
            botMessage(`You have selected ${detectedChannel}. Now you can ask me your questions.`);
        } else {
            botMessage('Could you please firstly tell me the exact knowledge base before asking anything else?');
        }
        return; // Exit the function since we don't proceed without channel selection
    }

    // Start streaming logs from the backend
    if (eventSource) {
        eventSource.close();  // Close previous event stream if one exists
    }

    eventSource = new EventSource(`http://localhost:5001/chat_logs/${currentChannel}`);
    eventSource.onmessage = function(event) {
        botMessage(event.data);  // Display the log as it comes in
        if (event.data.includes("Response ready!")) {
            eventSource.close();  // Close SSE after final log message
        }
    };

    // Get final response from the backend
    const response = await fetch(`http://localhost:5001/chat/${currentChannel}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ prompt: userInput })
    });

    const data = await response.json();
    botMessage(data.response);  // Display the final response

    eventSource.close();  // Close the event stream after getting the final response
}

// Start the conversation by asking for the channel
window.onload = function() {
    botMessage("Hello, welcome to Support Genius! May I know which knowledge base you want to ask about? Confluence or ServiceNow?");
};
