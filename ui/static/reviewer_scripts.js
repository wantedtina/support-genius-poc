async function fetchPendingResponses() {
    const response = await fetch('/pending_reviews');
    const data = await response.json();
    const reviewbox = document.getElementById('reviewbox');

    // 保留已审核结果的元素
    const existingMessages = Array.from(reviewbox.getElementsByClassName('message'));

    // 清空当前的待审核列表
    reviewbox.innerHTML = '';

    data.reviews.forEach(review => {
        let reviewMessageElement = existingMessages.find(msg => msg.dataset.prompt === review.user_prompt);

        if (!reviewMessageElement) {
            // 创建新的待审核元素
            reviewMessageElement = document.createElement('div');
            reviewMessageElement.className = 'message bot';
            reviewMessageElement.setAttribute('data-prompt', review.user_prompt);
            reviewMessageElement.innerHTML = `<img src="/static/bot_icon.png" alt="Bot">${review.response}`;
        }

        reviewbox.appendChild(reviewMessageElement);
    });

    const reviewContainer = document.getElementById('review-container');
    const generatedResponse = document.getElementById('generated-response');

    // 检查是否有未审核的答案
    const pendingReview = data.reviews.find(review => {
        return !existingMessages.some(msg => msg.dataset.prompt === review.user_prompt && (msg.querySelector('.approved') || msg.querySelector('.rejected')));
    });

    if (pendingReview) {
        generatedResponse.innerHTML = `<p>${pendingReview.response}</p>`;
        generatedResponse.setAttribute('data-prompt', pendingReview.user_prompt);
        reviewContainer.style.display = 'flex';
    } else {
        generatedResponse.innerHTML = ''; // 清空答案框
        generatedResponse.removeAttribute('data-prompt');
        reviewContainer.style.display = 'none';
    }
}

async function reviewResponse(action) {
    const generatedResponse = document.getElementById('generated-response').innerText;
    const userPrompt = document.getElementById('generated-response').getAttribute('data-prompt');
    const reviewMessageElement = document.querySelector(`.message.bot[data-prompt="${userPrompt}"]`);

    const response = await fetch('/review', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            action: action,
            response: generatedResponse,
            user_prompt: userPrompt
        })
    });

    const data = await response.json();

    // 根据审核结果标记消息
    if (action === 'approve') {
        reviewMessageElement.innerHTML += ` <span class="approved">(Approved)</span>`;
        reviewMessageElement.classList.add('approved');
    } else {
        reviewMessageElement.innerHTML += ` <span class="rejected">(Rejected)</span>`;
        reviewMessageElement.classList.add('rejected');
    }

    // 清空答案框
    const generatedResponseContainer = document.getElementById('generated-response');
    generatedResponseContainer.innerHTML = '';
    generatedResponseContainer.removeAttribute('data-prompt');

    // 隐藏底部容器
    const reviewContainer = document.getElementById('review-container');
    reviewContainer.style.display = 'none';

    // 更新审核员界面的待审核列表
    fetchPendingResponses();
}

// 页面加载时获取待审核响应
window.onload = function() {
    fetchPendingResponses(); // 初次加载时获取待审核响应
    setInterval(fetchPendingResponses, 3000); // 每3秒刷新一次待审核响应
};
