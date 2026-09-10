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


        /* Menu wrapper */

        const menuWrapper =
            document.createElement("div");

        menuWrapper.className =
            "chat-menu-wrapper";


        /* Menu button */

        const menuButton =
            document.createElement("button");

        menuButton.type = "button";
        menuButton.className =
            "chat-menu-button";

        menuButton.textContent = "⋯";
        menuButton.title = "Chat options";


        /* Dropdown */

        const dropdown =
            document.createElement("div");

        dropdown.className =
            "chat-dropdown";


        /* Rename button */

        const renameButton =
            document.createElement("button");

        renameButton.type = "button";
        renameButton.className =
            "chat-dropdown-item";

        renameButton.textContent =
            "Rename";

        renameButton.addEventListener(
            "click",
            async (event) => {
                event.stopPropagation();

                dropdown.classList.remove(
                    "show"
                );

                await renameChat(
                    chat.id,
                    chat.title
                );
            }
        );


        /* Delete button */

        const deleteButton =
            document.createElement("button");

        deleteButton.type = "button";
        deleteButton.className =
            "chat-dropdown-item chat-dropdown-delete";

        deleteButton.textContent =
            "Delete";

        deleteButton.addEventListener(
            "click",
            async (event) => {
                event.stopPropagation();

                dropdown.classList.remove(
                    "show"
                );

                await deleteChat(
                    chat.id,
                    chat.title
                );
            }
        );


        /* Toggle menu */

        menuButton.addEventListener(
            "click",
            (event) => {
                event.stopPropagation();

                const wasOpen =
                    dropdown.classList.contains(
                        "show"
                    );

                closeAllChatMenus();

                if (!wasOpen) {
                    dropdown.classList.add(
                        "show"
                    );
                }
            }
        );


        dropdown.appendChild(
            renameButton
        );

        dropdown.appendChild(
            deleteButton
        );

        menuWrapper.appendChild(
            menuButton
        );

        menuWrapper.appendChild(
            dropdown
        );

        element.appendChild(
            title
        );

        element.appendChild(
            menuWrapper
        );

        chatList.appendChild(
            element
        );
    }
}


function closeAllChatMenus() {
    const dropdowns =
        document.querySelectorAll(
            ".chat-dropdown"
        );

    for (const dropdown of dropdowns) {
        dropdown.classList.remove(
            "show"
        );
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
        alert(
            "Failed to create chat."
        );

        return;
    }

    const chat =
        await response.json();

    currentChatId =
        chat.id;

    await loadChats();
    await loadMessages();

    document
        .getElementById(
            "message-input"
        )
        .focus();
}


async function selectChat(chatId) {
    currentChatId =
        chatId;

    closeAllChatMenus();

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

    if (newTitle === null) {
        return;
    }

    const cleanedTitle =
        newTitle.trim();

    if (!cleanedTitle) {
        return;
    }

    if (
        cleanedTitle === currentTitle
    ) {
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
   Delete Chat
===================================================== */

async function deleteChat(
    chatId,
    chatTitle
) {
    const confirmed = confirm(
        `Are you sure you want to delete "${chatTitle}"?`
    );

    if (!confirmed) {
        return;
    }

    const response = await apiFetch(
        `/api/chats/${chatId}/`,
        {
            method: "DELETE",
        }
    );

    if (!response || !response.ok) {
        alert(
            "Failed to delete chat."
        );

        return;
    }

    if (currentChatId === chatId) {
        currentChatId = null;

        clearChatView();
    }

    await loadChats();
}


function clearChatView() {
    const messages =
        document.getElementById(
            "messages"
        );

    const emptyState =
        document.getElementById(
            "empty-state"
        );

    messages.innerHTML = "";

    emptyState.style.display =
        "block";
}


/* =====================================================
   Markdown
===================================================== */

function renderMarkdown(markdownText) {
    const rawHtml =
        marked.parse(markdownText);

    return DOMPurify.sanitize(
        rawHtml,
        {
            USE_PROFILES: {
                html: true,
            },
        }
    );
}


/* =====================================================
   Syntax Highlighting
===================================================== */

function highlightCodeBlocks(container) {
    const codeBlocks =
        container.querySelectorAll(
            "pre code"
        );

    for (const block of codeBlocks) {
        hljs.highlightElement(
            block
        );
    }
}


/* =====================================================
   Copy Code Buttons
===================================================== */

function addCopyButtons(container) {
    const codeBlocks =
        container.querySelectorAll(
            "pre"
        );

    for (const pre of codeBlocks) {
        const code =
            pre.querySelector(
                "code"
            );

        if (!code) {
            continue;
        }

        pre.classList.add(
            "code-block-wrapper"
        );

        const button =
            document.createElement(
                "button"
            );

        button.type = "button";
        button.className =
            "copy-code-button";

        button.textContent =
            "Copy";

        button.addEventListener(
            "click",
            async () => {
                try {
                    await navigator.clipboard.writeText(
                        code.innerText
                    );

                    button.textContent =
                        "Copied!";

                    setTimeout(
                        () => {
                            button.textContent =
                                "Copy";
                        },
                        1500
                    );

                } catch (error) {
                    console.error(
                        "Copy failed:",
                        error
                    );

                    button.textContent =
                        "Failed";
                }
            }
        );

        pre.appendChild(
            button
        );
    }
}


/* =====================================================
   Messages
===================================================== */

async function loadMessages() {
    if (!currentChatId) {
        clearChatView();
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

    renderMessages(
        messages
    );
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

    emptyState.style.display =
        "none";

    for (const message of messages) {
        appendMessage(
            message
        );
    }

    scrollToBottom();
}


function appendMessage(message) {
    const container =
        document.getElementById(
            "messages"
        );

    const element =
        document.createElement(
            "div"
        );

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


    /* Role */

    const role =
        document.createElement(
            "div"
        );

    role.className =
        "message-role";

    role.textContent =
        message.role === "user"
            ? "You"
            : "AI";


    /* Content */

    const content =
        document.createElement(
            "div"
        );

    content.className =
        "message-content";


    if (message.role === "assistant") {
        content.innerHTML =
            renderMarkdown(
                message.content
            );
    } else {
        content.textContent =
            message.content;
    }


    element.appendChild(
        role
    );

    element.appendChild(
        content
    );

    container.appendChild(
        element
    );


    if (message.role === "assistant") {
        highlightCodeBlocks(
            content
        );

        addCopyButtons(
            content
        );
    }
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
    if (!currentChatId) {
        await createChat();
    }

    if (!currentChatId) {
        return;
    }


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


        if (
            !response ||
            !response.ok
        ) {
            throw new Error(
                "Failed to send message."
            );
        }


        const data =
            await response.json();


        appendMessage(
            data.assistant_message
        );


        await loadChats();

        scrollToBottom();

    } catch (error) {
        console.error(
            "Send message error:",
            error
        );

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
   New Chat
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
   Enter = Send
   Shift + Enter = New Line
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
   Close Chat Menus
===================================================== */

document.addEventListener(
    "click",
    () => {
        closeAllChatMenus();
    }
);


/* =====================================================
   Initial Page Load
===================================================== */

loadChats();
