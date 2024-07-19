let currentPrompt = '';
let waitingMessageElement;
let reviewMessageElement;

async function sendMessage() {
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

    const response = await fetch('/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ prompt: userInput })
    });

    const data = await response.json();
    const reviewbox = document.getElementById('reviewbox');
    reviewMessageElement = document.createElement('div');
    reviewMessageElement.className = 'message bot';
    reviewMessageElement.innerHTML = `<img src="/static/bot_icon.png" alt="Bot">${data.response}`;
    reviewbox.appendChild(reviewMessageElement);
    reviewbox.scrollTop = reviewbox.scrollHeight; // 滚动到最新消息

    const reviewContainer = document.getElementById('review-container');
    const generatedResponse = document.getElementById('generated-response');
    generatedResponse.innerHTML = `<p>${data.response}</p>`;
    reviewContainer.style.display = 'flex';
}

async function reviewResponse(action) {
    const generatedResponse = document.getElementById('generated-response').innerText;

    const response = await fetch('/review', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            action: action,
            response: generatedResponse,
            user_prompt: currentPrompt
        })
    });

    const data = await response.json();
    const chatbox = document.getElementById('chatbox');

    // 移除等待消息
    chatbox.removeChild(waitingMessageElement);

    // 显示最终响应
    chatbox.innerHTML += `<div class="message bot"><img src="/static/bot_icon.png" alt="Bot">${data.response}</div>`;
    chatbox.scrollTop = chatbox.scrollHeight; // 滚动到最新消息

    // 添加标记
    if (action === 'approve') {
        reviewMessageElement.innerHTML += ` <span class="approved">(Approved)</span>`;
    } else {
        reviewMessageElement.innerHTML += ` <span class="rejected">(Rejected)</span>`;
    }

    const reviewContainer = document.getElementById('review-container');
    reviewContainer.style.display = 'none';
}
