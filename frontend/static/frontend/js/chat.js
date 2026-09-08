let currentChatId = null;


function getCookie(name) {
    const cookies = document.cookie.split(";");

    for (const cookie of cookies) {
        const trimmedCookie = cookie.trim();

        if (trimmedCookie.startsWith(name + "=")) {
            return decodeURIComponent(
                trimmedCookie.substring(name.length + 1)
            );
        }
    }

    return null;
}


async function apiFetch(url, options = {}) {
    const headers = {
        ...(options.headers || {}),
    };

    if (
        options.method &&
        options.method !== "GET"
    ) {
        headers["X-CSRFToken"] =
            getCookie("csrftoken");
    }

    const response = await fetch(
        url,
        {
            credentials: "same-origin",
            ...options,
            headers,
        }
    );

    if (response.status === 401 ||
        response.status === 403) {

        window.location.href = "/login/";

        return null;
    }

    return response;
}


/* -----------------
   Chats
------------------ */


async function loadChats() {
    const response = await apiFetch(
        "/api/chats/"
    );

    if (!response) {
        return;
    }

    const chats = await response.json();

    renderChats(chats);
}


function renderChats(chats) {
    const chatList =
        document.getElementById("chat-list");

    chatList.innerHTML = "";

    for (const chat of chats) {

        const element =
            document.createElement("div");

        element.className = "chat-item";

        element.textContent = chat.title;

        element.dataset.chatId = chat.id;

        if (chat.id === currentChatId) {
            element.classList.add("active");
        }

        element.addEventListener(
            "click",
            () => selectChat(chat.id)
        );

        chatList.appendChild(element);
    }
}


async function createChat() {
    const response = await apiFetch(
        "/api/chats/",
        {
            method: "POST",

            headers: {
                "Content-Type": "application/json",
            },

            body: JSON.stringify({
                title: "New Chat",
            }),
        }
    );

    if (!response || !response.ok) {
        return;
    }

    const chat = await response.json();

    currentChatId = chat.id;

    await loadChats();
    await loadMessages();

    document
        .getElementById("message-input")
        .focus();
}


async function selectChat(chatId) {
    currentChatId = chatId;

    await loadChats();
    await loadMessages();
}


/* -----------------
   Messages
------------------ */


async function loadMessages() {
    if (!currentChatId) {
        return;
    }

    const response = await apiFetch(
        `/api/chats/${currentChatId}/messages/`
    );

    if (!response || !response.ok) {
        return;
    }

    const messages = await response.json();

    renderMessages(messages);
}


function renderMessages(messages) {
    const container =
        document.getElementById("messages");

    const emptyState =
        document.getElementById("empty-state");

    container.innerHTML = "";

    emptyState.style.display = "none";

    for (const message of messages) {
        appendMessage(message);
    }

    scrollToBottom();
}


function appendMessage(message) {
    const container =
        document.getElementById("messages");

    const element =
        document.createElement("div");

    element.classList.add("message");

    if (message.role === "user") {
        element.classList.add(
            "message-user"
        );
    } else {
        element.classList.add(
            "message-assistant"
        );
    }

    const role =
        document.createElement("div");

    role.className = "message-role";

    role.textContent =
        message.role === "user"
            ? "You"
            : "AI";


    const content =
        document.createElement("div");

    content.textContent =
        message.content;


    element.appendChild(role);
    element.appendChild(content);

    container.appendChild(element);
}


function scrollToBottom() {
    const container =
        document.getElementById("messages");

    container.scrollTop =
        container.scrollHeight;
}


/* -----------------
   Send message
------------------ */


async function sendMessage(content) {
    if (!currentChatId) {
        await createChat();
    }

    appendMessage({
        role: "user",
        content: content,
    });

    scrollToBottom();

    const sendButton =
        document.getElementById("send-button");

    sendButton.disabled = true;
    sendButton.textContent = "Thinking...";

    try {
        const response = await apiFetch(
            `/api/chats/${currentChatId}/messages/`,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json",
                },

                body: JSON.stringify({
                    content: content,
                }),
            }
        );

        if (!response || !response.ok) {
            throw new Error(
                "Failed to send message."
            );
        }

        const data = await response.json();

        appendMessage(
            data.assistant_message
        );
        await loadChats();

        scrollToBottom();

    } catch (error) {

        appendMessage({
            role: "assistant",
            content:
                "Something went wrong. Please try again.",
        });

    } finally {

        sendButton.disabled = false;
        sendButton.textContent = "Send";
    }
}


/* -----------------
   Events
------------------ */


document
    .getElementById("new-chat-button")
    .addEventListener(
        "click",
        createChat
    );


document
    .getElementById("message-form")
    .addEventListener(
        "submit",
        async (event) => {

            event.preventDefault();

            const input =
                document.getElementById(
                    "message-input"
                );

            const content =
                input.value.trim();

            if (!content) {
                return;
            }

            input.value = "";

            await sendMessage(content);
        }
    );


document
    .getElementById("logout-button")
    .addEventListener(
        "click",
        async () => {

            await apiFetch(
                "/api/auth/logout/",
                {
                    method: "POST",
                }
            );

            window.location.href =
                "/login/";
        }
    );


/* Initial page load */

loadChats();
