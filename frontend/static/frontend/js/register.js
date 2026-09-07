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


const form = document.getElementById("register-form");
const errorMessage = document.getElementById("error-message");


form.addEventListener("submit", async (event) => {
    event.preventDefault();

    errorMessage.classList.add("d-none");

    const username =
        document.getElementById("username").value;

    const email =
        document.getElementById("email").value;

    const password =
        document.getElementById("password").value;

    const passwordConfirm =
        document.getElementById(
            "password-confirm"
        ).value;

    try {
        const response = await fetch(
            "/api/auth/register/",
            {
                method: "POST",

                credentials: "same-origin",

                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken"),
                },

                body: JSON.stringify({
                    username,
                    email,
                    password,
                    password_confirm: passwordConfirm,
                }),
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                JSON.stringify(data)
            );
        }

        window.location.href = "/login/";

    } catch (error) {
        errorMessage.textContent = error.message;
        errorMessage.classList.remove("d-none");
    }
});
