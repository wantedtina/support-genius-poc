let currentPrompt = '';
let waitingMessageElement;
let currentChannel = '';
let sendToReviewer = false;

function selectChannel(channel) {
    currentChannel = channel;
    document.getElementById('channel-selection').style.display = 'none';
    document.getElementById('user-input').style.display = 'flex';

    const chatbox = document.getElementById('chatbox');
    chatbox.innerHTML += `<div class="message bot"><img src="/static/bot_icon.png" alt="Bot">You have selected ${channel === 'confluence' ? 'Knowledge Query' : 'Service Now Query'}.</div>`;
}

function switchChannel() {
    currentChannel = '';
    document.getElementById('channel-selection').style.display = 'flex';
    document.getElementById('user-input').style.display = 'none';

    const chatbox = document.getElementById('chatbox');
    chatbox.innerHTML = ''; // 清除当前对话
}

async function sendMessage() {
    if (!currentChannel) {
        alert('Please select a channel first.');
        return;
    }

    const userInput = document.getElementById('userInput').value;
    if (userInput.trim() === "") return;

    currentPrompt = userInput;
    const chatbox = document.getElementById('chatbox');
    chatbox.innerHTML += `<div class="message user"><img src="/static/user_icon.png" alt="User">${userInput}</div>`;
    chatbox.scrollTop = chatbox.scrollHeight; // 滚动到最新消息

    // 显示等待消息
    waitingMessageElement = document.createElement('div');
    waitingMessageElement.className = 'message bot';
    waitingMessageElement.innerHTML = `<img src="/static/bot_icon.png" alt="Bot">Please wait for a while for your answer to generate<span class="dots">...</span>`;
    chatbox.appendChild(waitingMessageElement);
    chatbox.scrollTop = chatbox.scrollHeight; // 滚动到最新消息

    document.getElementById('userInput').value = '';

    // 获取开关状态
    sendToReviewer = document.getElementById('reviewerSwitch').checked;

    const response = await fetch(`/chat/${currentChannel}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ prompt: userInput, send_to_reviewer: sendToReviewer })
    });

    const data = await response.json();

    if (sendToReviewer) {
        // 将生成的响应发送到审核员界面
        await fetch('/review', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                action: 'pending',
                response: data.response,
                user_prompt: currentPrompt
            })
        });
    } else {
        // 直接显示响应
        chatbox.removeChild(waitingMessageElement); // 移除等待消息
        chatbox.innerHTML += `<div class="message bot"><img src="/static/bot_icon.png" alt="Bot">${data.response}</div>`;
        chatbox.scrollTop = chatbox.scrollHeight; // 滚动到最新消息
    }
}

// 轮询检查新的用户响应
async function checkUserResponses() {
    const response = await fetch('/user_responses');
    const data = await response.json();

    if (data.responses.length > 0) {
        data.responses.forEach(res => {
            const chatbox = document.getElementById('chatbox');
            chatbox.removeChild(waitingMessageElement); // 移除等待消息

            chatbox.innerHTML += `<div class="message bot"><img src="/static/bot_icon.png" alt="Bot">${res.response}</div>`;
            chatbox.scrollTop = chatbox.scrollHeight; // 滚动到最新消息
        });
    }
}

window.onload = function() {
    setInterval(checkUserResponses, 3000); // 每3秒检查一次新的用户响应
};
