/* =====================================================
   Helpers
===================================================== */

function getCookie(name) {
    const cookies =
        document.cookie.split(";");

    for (const cookie of cookies) {
        const trimmedCookie =
            cookie.trim();

        if (
            trimmedCookie.startsWith(
                name + "="
            )
        ) {
            return decodeURIComponent(
                trimmedCookie.substring(
                    name.length + 1
                )
            );
        }
    }

    return null;
}


async function apiFetch(
    url,
    options = {}
) {
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
        window.location.href =
            "/login/";

        return null;
    }


    return response;
}


/* =====================================================
   Formatting
===================================================== */

function formatFileSize(bytes) {
    if (bytes === 0) {
        return "0 B";
    }


    const units = [
        "B",
        "KB",
        "MB",
        "GB",
    ];

    const index = Math.floor(
        Math.log(bytes) /
        Math.log(1024)
    );

    const size =
        bytes /
        Math.pow(
            1024,
            index
        );


    return (
        `${size.toFixed(
            index === 0 ? 0 : 1
        )} ${units[index]}`
    );
}


function formatDate(dateString) {
    const date =
        new Date(dateString);


    return date.toLocaleDateString(
        undefined,
        {
            year: "numeric",
            month: "short",
            day: "numeric",
        }
    );
}


function getFileTypeLabel(fileType) {
    switch (
        fileType.toLowerCase()
    ) {
        case "pdf":
            return "PDF";

        case "txt":
            return "TXT";

        case "md":
            return "MD";

        default:
            return fileType.toUpperCase();
    }
}


/* =====================================================
   Documents
===================================================== */

async function loadDocuments() {
    const loading =
        document.getElementById(
            "library-loading"
        );

    const emptyState =
        document.getElementById(
            "library-empty-state"
        );

    const list =
        document.getElementById(
            "document-list"
        );


    loading.classList.remove(
        "d-none"
    );

    emptyState.classList.add(
        "d-none"
    );

    list.innerHTML = "";


    try {
        const response = await apiFetch(
            "/api/documents/"
        );


        if (
            !response ||
            !response.ok
        ) {
            throw new Error(
                "Failed to load documents."
            );
        }


        const documents =
            await response.json();


        renderDocuments(
            documents
        );

    } catch (error) {
        console.error(
            "Load documents error:",
            error
        );

        list.innerHTML = `
            <div class="alert alert-danger">
                Failed to load documents.
            </div>
        `;

    } finally {
        loading.classList.add(
            "d-none"
        );
    }
}


function renderDocuments(documents) {
    const list =
        document.getElementById(
            "document-list"
        );

    const emptyState =
        document.getElementById(
            "library-empty-state"
        );

    const count =
        document.getElementById(
            "document-count"
        );


    list.innerHTML = "";


    count.textContent =
        documents.length === 1
            ? "1 document"
            : `${documents.length} documents`;


    if (documents.length === 0) {
        emptyState.classList.remove(
            "d-none"
        );

        return;
    }


    emptyState.classList.add(
        "d-none"
    );


    for (
        const documentData
        of documents
    ) {
        list.appendChild(
            createDocumentElement(
                documentData
            )
        );
    }
}


/* =====================================================
   Document Element
===================================================== */

function createDocumentElement(
    documentData
) {
    const element =
        document.createElement(
            "div"
        );

    element.className =
        "document-item";


    /* File icon */

    const icon =
        document.createElement(
            "div"
        );

    icon.className =
        "document-icon";

    icon.textContent =
        getFileTypeLabel(
            documentData.file_type
        );


    /* Information */

    const info =
        document.createElement(
            "div"
        );

    info.className =
        "document-info";


    const title =
        document.createElement(
            "div"
        );

    title.className =
        "document-title";

    title.textContent =
        documentData.title;


    const filename =
        document.createElement(
            "div"
        );

    filename.className =
        "document-filename";

    filename.textContent =
        documentData.original_filename;


    const metadata =
        document.createElement(
            "div"
        );

    metadata.className =
        "document-metadata";

    metadata.textContent =
        [
            getFileTypeLabel(
                documentData.file_type
            ),

            formatFileSize(
                documentData.file_size
            ),

            formatDate(
                documentData.created_at
            ),
        ].join(" · ");


    info.appendChild(
        title
    );

    info.appendChild(
        filename
    );

    info.appendChild(
        metadata
    );


    /* Actions */

    const actions =
        document.createElement(
            "div"
        );

    actions.className =
        "document-actions";


    const renameButton =
        document.createElement(
            "button"
        );

    renameButton.type =
        "button";

    renameButton.className =
        "btn btn-sm btn-outline-secondary";

    renameButton.textContent =
        "Rename";


    renameButton.addEventListener(
        "click",
        async () => {
            await renameDocument(
                documentData
            );
        }
    );


    const deleteButton =
        document.createElement(
            "button"
        );

    deleteButton.type =
        "button";

    deleteButton.className =
        "btn btn-sm btn-outline-danger";

    deleteButton.textContent =
        "Delete";


    deleteButton.addEventListener(
        "click",
        async () => {
            await deleteDocument(
                documentData
            );
        }
    );


    actions.appendChild(
        renameButton
    );

    actions.appendChild(
        deleteButton
    );


    element.appendChild(
        icon
    );

    element.appendChild(
        info
    );

    element.appendChild(
        actions
    );


    return element;
}


/* =====================================================
   Upload Document
===================================================== */

async function uploadDocument(event) {
    event.preventDefault();


    const form =
        document.getElementById(
            "document-upload-form"
        );

    const titleInput =
        document.getElementById(
            "document-title"
        );

    const fileInput =
        document.getElementById(
            "document-file"
        );

    const uploadButton =
        document.getElementById(
            "upload-button"
        );

    const errorMessage =
        document.getElementById(
            "upload-error"
        );


    errorMessage.classList.add(
        "d-none"
    );


    if (
        !fileInput.files ||
        fileInput.files.length === 0
    ) {
        return;
    }


    const formData =
        new FormData();

    const title =
        titleInput.value.trim();


    if (title) {
        formData.append(
            "title",
            title
        );
    }


    formData.append(
        "file",
        fileInput.files[0]
    );


    uploadButton.disabled =
        true;

    uploadButton.textContent =
        "Uploading...";


    try {
        const response = await apiFetch(
            "/api/documents/",
            {
                method: "POST",
                body: formData,
            }
        );


        if (!response) {
            return;
        }


        if (!response.ok) {
            const errorData =
                await response.json();

            throw new Error(
                getApiErrorMessage(
                    errorData
                )
            );
        }


        form.reset();

        await loadDocuments();

    } catch (error) {
        console.error(
            "Upload document error:",
            error
        );


        errorMessage.textContent =
            error.message;

        errorMessage.classList.remove(
            "d-none"
        );

    } finally {
        uploadButton.disabled =
            false;

        uploadButton.textContent =
            "Upload";
    }
}


/* =====================================================
   Rename Document
===================================================== */

async function renameDocument(
    documentData
) {
    const newTitle = prompt(
        "Enter a new document title:",
        documentData.title
    );


    if (newTitle === null) {
        return;
    }


    const cleanedTitle =
        newTitle.trim();


    if (
        !cleanedTitle ||
        cleanedTitle ===
            documentData.title
    ) {
        return;
    }


    const formData =
        new FormData();

    formData.append(
        "title",
        cleanedTitle
    );


    const response = await apiFetch(
        `/api/documents/${documentData.id}/`,
        {
            method: "PATCH",
            body: formData,
        }
    );


    if (
        !response ||
        !response.ok
    ) {
        alert(
            "Failed to rename document."
        );

        return;
    }


    await loadDocuments();
}


/* =====================================================
   Delete Document
===================================================== */

async function deleteDocument(
    documentData
) {
    const confirmed = confirm(
        `Delete "${documentData.title}"?`
    );


    if (!confirmed) {
        return;
    }


    const response = await apiFetch(
        `/api/documents/${documentData.id}/`,
        {
            method: "DELETE",
        }
    );


    if (
        !response ||
        !response.ok
    ) {
        alert(
            "Failed to delete document."
        );

        return;
    }


    await loadDocuments();
}


/* =====================================================
   API Errors
===================================================== */

function getApiErrorMessage(
    errorData
) {
    if (
        typeof errorData === "string"
    ) {
        return errorData;
    }


    if (errorData.detail) {
        return errorData.detail;
    }


    if (
        errorData.file &&
        Array.isArray(
            errorData.file
        )
    ) {
        return errorData.file[0];
    }


    if (
        errorData.title &&
        Array.isArray(
            errorData.title
        )
    ) {
        return errorData.title[0];
    }


    return "Failed to upload document.";
}


/* =====================================================
   Upload Form
===================================================== */

document
    .getElementById(
        "document-upload-form"
    )
    .addEventListener(
        "submit",
        uploadDocument
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
   Initial Load
===================================================== */

loadDocuments();