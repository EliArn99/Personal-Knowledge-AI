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


const form = document.getElementById("login-form");
const errorMessage = document.getElementById("error-message");


form.addEventListener("submit", async (event) => {
    event.preventDefault();

    errorMessage.classList.add("d-none");

    const username =
        document.getElementById("username").value;

    const password =
        document.getElementById("password").value;

    try {
        const response = await fetch(
            "/api/auth/login/",
            {
                method: "POST",

                credentials: "same-origin",

                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken"),
                },

                body: JSON.stringify({
                    username,
                    password,
                }),
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail || "Login failed."
            );
        }

        window.location.href = "/chat/";

    } catch (error) {
        errorMessage.textContent = error.message;
        errorMessage.classList.remove("d-none");
    }
});
