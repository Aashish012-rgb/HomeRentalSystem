(function () {
  const bootstrapEl = document.getElementById("chat-bootstrap");
  if (!bootstrapEl) {
    return;
  }

  const config = JSON.parse(bootstrapEl.textContent);
  const chatMessages = document.getElementById("chatMessages");
  const chatForm = document.getElementById("chatForm");
  const chatInput = document.getElementById("chatInput");
  const chatSendButton = document.getElementById("chatSendButton");
  const chatStatus = document.getElementById("chatStatus");
  const chatError = document.getElementById("chatError");
  const reconnectLimit = 5;
  const reconnectDelayMs = 1500;

  let socket = null;
  let reconnectAttempts = 0;
  let hasConnected = false;
  let manualClose = false;

  function setStatus(message, tone) {
    chatStatus.textContent = message;
    chatStatus.className = "small text-" + (tone || "muted");
  }

  function setSendEnabled(enabled) {
    chatSendButton.disabled = !enabled;
    chatInput.disabled = !enabled;
  }

  function showError(message) {
    if (!message) {
      chatError.textContent = "";
      chatError.classList.add("d-none");
      return;
    }

    chatError.textContent = message;
    chatError.classList.remove("d-none");
  }

  function removeEmptyState() {
    const emptyState = chatMessages.querySelector("[data-empty-state='true']");
    if (emptyState) {
      emptyState.remove();
    }
  }

  function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  function formatTimestamp(isoString) {
    const date = new Date(isoString);
    if (Number.isNaN(date.getTime())) {
      return isoString;
    }

    return date.toLocaleString(undefined, {
      month: "short",
      day: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  }

  function buildMessageElement(message) {
    const isMine = Number(message.sender_id) === Number(config.currentUserId);
    const wrapper = document.createElement("div");
    wrapper.className =
      "chat-message " +
      (isMine ? "chat-message--mine" : "chat-message--theirs") +
      " mb-3";

    const bubble = document.createElement("div");
    bubble.className = "chat-message__bubble";

    const author = document.createElement("div");
    author.className = "small fw-semibold mb-1";
    author.textContent = isMine ? "You" : message.sender_username;

    const body = document.createElement("div");
    body.textContent = message.content;

    const meta = document.createElement("div");
    meta.className = "chat-meta mt-1";
    meta.textContent = message.timestamp_label || formatTimestamp(message.timestamp);

    bubble.appendChild(author);
    bubble.appendChild(body);
    wrapper.appendChild(bubble);
    wrapper.appendChild(meta);
    return wrapper;
  }

  function appendMessage(message) {
    removeEmptyState();
    chatMessages.appendChild(buildMessageElement(message));
    scrollToBottom();
  }

  function buildWebSocketUrl() {
    const protocol = window.location.protocol === "https:" ? "wss" : "ws";
    return (
      protocol +
      "://" +
      window.location.host +
      "/ws/chat/" +
      encodeURIComponent(config.bookingId) +
      "/"
    );
  }

  function getCloseMessage(event) {
    if (event.code === 4401) {
      return "Please sign in again to use chat.";
    }

    if (event.code === 4403) {
      return "Chat is only available to the tenant and owner while the booking is accepted.";
    }

    return "WebSocket failed. Start the app with uvicorn HomeRental.asgi:application --reload instead of manage.py runserver.";
  }

  function handlePayload(rawPayload) {
    let payload;

    try {
      payload = JSON.parse(rawPayload);
    } catch (error) {
      showError("Received an invalid response from the chat server.");
      return;
    }

    if (payload.type === "chat.message" && payload.message) {
      appendMessage(payload.message);
      return;
    }

    if (payload.type === "chat.error") {
      showError(payload.message || "Something went wrong in chat.");
    }
  }

  function scheduleReconnect() {
    if (reconnectAttempts >= reconnectLimit) {
      setStatus("Disconnected from chat.", "danger");
      showError("Unable to reconnect to chat. Make sure the ASGI server is running with uvicorn.");
      return;
    }

    reconnectAttempts += 1;
    setStatus("Disconnected. Reconnecting...", "warning");
    window.setTimeout(connect, reconnectDelayMs * reconnectAttempts);
  }

  function connect() {
    if (socket && (socket.readyState === WebSocket.OPEN || socket.readyState === WebSocket.CONNECTING)) {
      return;
    }

    setStatus("Connecting to chat...", "muted");
    showError("");
    setSendEnabled(false);

    socket = new WebSocket(buildWebSocketUrl());

    socket.addEventListener("open", function () {
      reconnectAttempts = 0;
      hasConnected = true;
      setStatus("Connected to booking chat.", "success");
      showError("");
      setSendEnabled(true);
    });

    socket.addEventListener("message", function (event) {
      handlePayload(event.data);
    });

    socket.addEventListener("error", function () {
      if (!hasConnected) {
        setStatus("Unable to connect to chat.", "danger");
        showError(getCloseMessage({ code: 1006 }));
      }
    });

    socket.addEventListener("close", function (event) {
      setSendEnabled(false);

      if (manualClose) {
        return;
      }

      if (!hasConnected || event.code === 4401 || event.code === 4403) {
        setStatus("Unable to connect to chat.", "danger");
        showError(getCloseMessage(event));
        return;
      }

      scheduleReconnect();
    });
  }

  setSendEnabled(false);
  scrollToBottom();
  connect();

  chatForm.addEventListener("submit", function (event) {
    event.preventDefault();

    const message = chatInput.value.trim();
    if (!message) {
      return;
    }

    if (!socket || socket.readyState !== WebSocket.OPEN) {
      setStatus("Unable to send message.", "danger");
      showError("Chat is not connected yet. Make sure the ASGI server is running.");
      return;
    }

    showError("");
    socket.send(
      JSON.stringify({
        type: "chat.message",
        message: message,
      })
    );
    chatInput.value = "";
    chatInput.focus();
  });

  window.addEventListener("beforeunload", function () {
    manualClose = true;

    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.close(1000, "Page closed");
    }
  });
})();
