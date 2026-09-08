let currentChatId = null;


/* =====================================================
   Helpers
===================================================== */

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

    if (
        response.status === 401 ||
        response.status === 403
    ) {
        window.location.href = "/login/";
        return null;
    }

    return response;
}


/* =====================================================
   Chats
===================================================== */

async function loadChats() {
    const response = await apiFetch(
        "/api/chats/"
    );

    if (!response || !response.ok) {
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
        element.dataset.chatId = chat.id;

        if (chat.id === currentChatId) {
            element.classList.add("active");
        }


        /* Chat title */

        const title =
            document.createElement("span");

        title.className = "chat-title";
        title.textContent = chat.title;

        title.addEventListener(
            "click",
            () => selectChat(chat.id)
        );


        /* Chat menu button */

        const menuButton =
            document.createElement("button");

        menuButton.className =
            "chat-menu-button";

        menuButton.type = "button";

        menuButton.textContent = "⋯";

        menuButton.title = "Chat options";

        menuButton.addEventListener(
            "click",
            (event) => {
                event.stopPropagation();

                renameChat(
                    chat.id,
                    chat.title
                );
            }
        );


        element.appendChild(title);
        element.appendChild(menuButton);

        chatList.appendChild(element);
    }
}


async function createChat() {
    const response = await apiFetch(
        "/api/chats/",
        {
            method: "POST",

            headers: {
                "Content-Type":
                    "application/json",
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

    const input =
        document.getElementById(
            "message-input"
        );

    input.focus();
}


async function selectChat(chatId) {
    currentChatId = chatId;

    await loadChats();
    await loadMessages();
}


/* =====================================================
   Rename Chat
===================================================== */

async function renameChat(
    chatId,
    currentTitle
) {
    const newTitle = prompt(
        "Enter a new chat title:",
        currentTitle
    );

    // User pressed Cancel
    if (newTitle === null) {
        return;
    }

    const cleanedTitle =
        newTitle.trim();

    // Empty title
    if (!cleanedTitle) {
        return;
    }

    // Nothing changed
    if (cleanedTitle === currentTitle) {
        return;
    }

    const response = await apiFetch(
        `/api/chats/${chatId}/`,
        {
            method: "PATCH",

            headers: {
                "Content-Type":
                    "application/json",
            },

            body: JSON.stringify({
                title: cleanedTitle,
            }),
        }
    );

    if (!response || !response.ok) {
        alert(
            "Failed to rename chat."
        );

        return;
    }

    await loadChats();
}


/* =====================================================
   Messages
===================================================== */

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

    const messages =
        await response.json();

    renderMessages(messages);
}


function renderMessages(messages) {
    const container =
        document.getElementById(
            "messages"
        );

    const emptyState =
        document.getElementById(
            "empty-state"
        );

    container.innerHTML = "";

    emptyState.style.display = "none";

    for (const message of messages) {
        appendMessage(message);
    }

    scrollToBottom();
}


function appendMessage(message) {
    const container =
        document.getElementById(
            "messages"
        );

    const element =
        document.createElement("div");

    element.classList.add(
        "message"
    );


    if (message.role === "user") {
        element.classList.add(
            "message-user"
        );
    } else {
        element.classList.add(
            "message-assistant"
        );
    }


    /* Message role */

    const role =
        document.createElement("div");

    role.className =
        "message-role";

    role.textContent =
        message.role === "user"
            ? "You"
            : "AI";


    /* Message content */

    const content =
        document.createElement("div");

    content.className =
        "message-content";

    content.textContent =
        message.content;


    element.appendChild(role);
    element.appendChild(content);

    container.appendChild(element);
}


function scrollToBottom() {
    const container =
        document.getElementById(
            "messages"
        );

    container.scrollTop =
        container.scrollHeight;
}


/* =====================================================
   Send Message
===================================================== */

async function sendMessage(content) {
    /*
        If the user has not selected
        or created a chat yet,
        create one automatically.
    */

    if (!currentChatId) {
        await createChat();
    }

    if (!currentChatId) {
        return;
    }


    /*
        Show user's message immediately
        without waiting for the server.
    */

    appendMessage({
        role: "user",
        content: content,
    });

    scrollToBottom();


    const sendButton =
        document.getElementById(
            "send-button"
        );

    const input =
        document.getElementById(
            "message-input"
        );


    sendButton.disabled = true;
    input.disabled = true;

    sendButton.textContent =
        "Thinking...";


    try {
        const response = await apiFetch(
            `/api/chats/${currentChatId}/messages/`,
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json",
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
        console.error(error);

        appendMessage({
            role: "assistant",

            content:
                "Something went wrong. Please try again.",
        });

        scrollToBottom();

    } finally {
        sendButton.disabled = false;
        input.disabled = false;

        sendButton.textContent =
            "Send";

        input.focus();
    }
}


/* =====================================================
   New Chat Button
===================================================== */

document
    .getElementById(
        "new-chat-button"
    )
    .addEventListener(
        "click",
        createChat
    );


/* =====================================================
   Message Form
===================================================== */

document
    .getElementById(
        "message-form"
    )
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

            await sendMessage(
                content
            );
        }
    );


/* =====================================================
   Enter to Send
   Shift + Enter for new line
===================================================== */

document
    .getElementById(
        "message-input"
    )
    .addEventListener(
        "keydown",
        (event) => {
            if (
                event.key === "Enter" &&
                !event.shiftKey
            ) {
                event.preventDefault();

                document
                    .getElementById(
                        "message-form"
                    )
                    .requestSubmit();
            }
        }
    );


/* =====================================================
   Logout
===================================================== */

document
    .getElementById(
        "logout-button"
    )
    .addEventListener(
        "click",
        async () => {
            const response =
                await apiFetch(
                    "/api/auth/logout/",
                    {
                        method: "POST",
                    }
                );

            if (
                response &&
                response.ok
            ) {
                window.location.href =
                    "/login/";
            }
        }
    );


/* =====================================================
   Initial Page Load
===================================================== */

loadChats();
