document.addEventListener("DOMContentLoaded", () => {
    // Stop early if the chat page bootstrap data or DOM hooks are missing.
    if (typeof chatBootstrap === "undefined") {
        return;
    }

    const bookingId = chatBootstrap.bookingId;
    const userId = chatBootstrap.userId;
    const messagesContainer = document.getElementById("messages");
    const chatForm = document.getElementById("chat-form");
    const chatInput = document.getElementById("chat-input");
    const chatStatus = document.getElementById("chat-status");
    const chatError = document.getElementById("chat-error");
    const chatSend = document.getElementById("chat-send");

    if (!messagesContainer || !chatForm || !chatInput || !chatStatus || !chatError || !chatSend) {
        return;
    }

    // Use the matching websocket scheme so chat works on both HTTP and HTTPS.
    const websocketScheme = window.location.protocol === "https:" ? "wss" : "ws";
    const chatSocket = new WebSocket(
        `${websocketScheme}://${window.location.host}/ws/chat/${bookingId}/`
    );

    function scrollToBottom() {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    function setStatus(message, tone) {
        chatStatus.textContent = message;
        chatStatus.dataset.tone = tone || "neutral";
    }

    function setComposerEnabled(enabled) {
        chatInput.disabled = !enabled;
        chatSend.disabled = !enabled;
    }

    function showError(message) {
        if (!message) {
            chatError.hidden = true;
            chatError.textContent = "";
            return;
        }

        chatError.hidden = false;
        chatError.textContent = message;
    }

    function removeEmptyState() {
        const emptyState = document.getElementById("chat-empty-state");
        if (emptyState) {
            emptyState.remove();
        }
    }

    function buildMessageElement(data) {
        const messageArticle = document.createElement("article");
        messageArticle.classList.add("message");

        const isCurrentUser = Number(data.sender_id) === Number(userId);
        messageArticle.classList.add(isCurrentUser ? "you" : "other");

        if (!isCurrentUser) {
            const avatar = document.createElement("div");
            avatar.className = "message-avatar";
            avatar.textContent = (data.sender_username || "?").charAt(0).toUpperCase();
            messageArticle.appendChild(avatar);
        }

        const stack = document.createElement("div");
        stack.className = "message-stack";

        const author = document.createElement("div");
        author.className = "message-author";
        author.textContent = isCurrentUser ? "You" : data.sender_username || "Guest";

        const bubble = document.createElement("div");
        bubble.className = "message-bubble";
        bubble.textContent = data.content || "";

        const meta = document.createElement("div");
        meta.className = "message-meta";
        meta.textContent = data.timestamp_label || data.timestamp || "";

        stack.appendChild(author);
        stack.appendChild(bubble);
        stack.appendChild(meta);
        messageArticle.appendChild(stack);

        return messageArticle;
    }

    chatSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        if (data.error) {
            showError(data.error);
            return;
        }

        removeEmptyState();
        messagesContainer.appendChild(buildMessageElement(data));
        showError("");
        scrollToBottom();
    };

    chatSocket.onopen = function() {
        setStatus("Active now", "connected");
        setComposerEnabled(true);
        showError("");
        chatInput.focus();
    };

    chatSocket.onclose = function() {
        setStatus("Connection lost", "disconnected");
        setComposerEnabled(false);
        showError("Chat disconnected. Refresh the page or restart the ASGI server.");
    };

    setStatus("Connecting...", "neutral");
    setComposerEnabled(false);
    scrollToBottom();

    chatForm.addEventListener("submit", (e) => {
        e.preventDefault();
        const message = chatInput.value.trim();
        if (message === "") return;
        if (chatSocket.readyState !== WebSocket.OPEN) {
            showError("Chat is still connecting. Please wait a moment and try again.");
            return;
        }

        chatSocket.send(JSON.stringify({
            "content": message
        }));
        chatInput.value = "";
        showError("");
        chatInput.focus();
    });
});
