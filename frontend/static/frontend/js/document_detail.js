function formatFileSize(bytes) {
    if (!bytes) {
        return "0 B";
    }

    const units = [
        "B",
        "KB",
        "MB",
        "GB",
    ];

    let size = bytes;
    let unitIndex = 0;

    while (
        size >= 1024 &&
        unitIndex < units.length - 1
    ) {
        size /= 1024;
        unitIndex += 1;
    }

    return `${size.toFixed(
        unitIndex === 0 ? 0 : 1
    )} ${units[unitIndex]}`;
}


async function loadDocument() {
    const page =
        document.querySelector(
            ".document-detail-page"
        );

    if (!page) {
        return;
    }

    const documentId =
        page.dataset.documentId;

    const loading =
        document.getElementById(
            "document-loading"
        );

    const errorBox =
        document.getElementById(
            "document-error"
        );

    const title =
        document.getElementById(
            "document-title"
        );

    const meta =
        document.getElementById(
            "document-meta"
        );

    const text =
        document.getElementById(
            "document-extracted-text"
        );

    const contentSection =
        document.getElementById(
            "document-content-section"
        );

    const downloadButton =
        document.getElementById(
            "document-download-button"
        );


    try {
        const response = await fetch(
            `/api/documents/${documentId}/`,
            {
                credentials: "same-origin",
            }
        );

        if (
            response.status === 401 ||
            response.status === 403
        ) {
            window.location.href =
                "/login/";

            return;
        }

        if (!response.ok) {
            throw new Error(
                "Failed to load document."
            );
        }

        const data =
            await response.json();


        title.textContent =
            data.title;


        const type =
            data.file_type
                ? data.file_type.toUpperCase()
                : "FILE";

        const size =
            formatFileSize(
                data.file_size
            );

        meta.textContent =
            `${type} · ${size}`;


        downloadButton.href =
            data.download_url ||
            `/api/documents/${documentId}/download/`;

        downloadButton.hidden =
            false;


        if (
            data.extraction_status === "ready" &&
            data.extracted_text
        ) {
            text.textContent =
                data.extracted_text;

        } else if (
            data.extraction_status === "failed"
        ) {
            text.textContent =
                "Text extraction failed for this document.";

        } else {
            text.textContent =
                "No extracted text is available for this document.";
        }


        contentSection.hidden =
            false;

    } catch (error) {
        console.error(
            "Document load error:",
            error
        );

        errorBox.textContent =
            "Could not load this document.";

        errorBox.hidden =
            false;

    } finally {
        loading.hidden =
            true;
    }
}


loadDocument();