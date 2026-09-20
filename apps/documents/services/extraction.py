import logging

from pypdf import PdfReader
from pypdf.errors import PdfReadError


logger = logging.getLogger(__name__)


MAX_SOURCE_BYTES = 10 * 1024 * 1024
MAX_EXTRACTED_CHARS = 1_000_000
MAX_PDF_PAGES = 200


class DocumentExtractionError(Exception):
    """Raised when document text extraction fails."""
    pass


# =====================================================
# TXT / Markdown
# =====================================================

def extract_plain_text(file):
    try:
        content = file.read()

        text = content.decode(
            "utf-8-sig"
        )

    except UnicodeDecodeError as exc:
        raise DocumentExtractionError(
            "The document must use UTF-8 encoding."
        ) from exc

    return text.strip()


# =====================================================
# PDF
# =====================================================

def extract_pdf_text(file):
    reader = PdfReader(file)

    if reader.is_encrypted:
        raise DocumentExtractionError(
            "Password-protected PDFs "
            "are not supported."
        )

    if len(reader.pages) > MAX_PDF_PAGES:
        raise DocumentExtractionError(
            "PDF exceeds the maximum "
            "of 200 pages."
        )

    pages_text = []
    total_characters = 0

    for page in reader.pages:
        page_text = (
            page.extract_text() or ""
        ).strip()

        if not page_text:
            continue

        total_characters += len(
            page_text
        )

        if (
            total_characters >
            MAX_EXTRACTED_CHARS
        ):
            raise DocumentExtractionError(
                "Extracted text exceeds "
                "the maximum allowed length."
            )

        pages_text.append(
            page_text
        )

    return "\n\n".join(
        pages_text
    ).strip()


# =====================================================
# Document Text Extraction
# =====================================================

def extract_text_from_document(document):
    file_type = (
        document.file_type.lower()
    )

    if (
        document.file_size >
        MAX_SOURCE_BYTES
    ):
        raise DocumentExtractionError(
            "Document exceeds the "
            "10 MB extraction limit."
        )

    if file_type not in {
        "pdf",
        "txt",
        "md",
    }:
        raise DocumentExtractionError(
            "Unsupported document type."
        )

    try:
        with document.file.open("rb") as file:

            if file_type == "pdf":
                text = extract_pdf_text(
                    file
                )

            else:
                text = extract_plain_text(
                    file
                )

    except PdfReadError as exc:
        raise DocumentExtractionError(
            "The PDF could not be read. "
            "It may be damaged or invalid."
        ) from exc

    except OSError as exc:
        raise DocumentExtractionError(
            "The document file "
            "could not be opened."
        ) from exc

    if not text:
        raise DocumentExtractionError(
            "No readable text was found. "
            "Scanned PDFs may require OCR."
        )

    if (
        len(text) >
        MAX_EXTRACTED_CHARS
    ):
        raise DocumentExtractionError(
            "Extracted text exceeds "
            "the maximum allowed length."
        )

    return text


# =====================================================
# Process and Save
# =====================================================

def process_document(document):
    try:
        extracted_text = (
            extract_text_from_document(
                document
            )
        )

    except DocumentExtractionError as exc:

        document.extracted_text = ""

        document.extraction_status = (
            "failed"
        )

        document.extraction_error = (
            str(exc)
        )

    except Exception:

        logger.exception(
            "Unexpected extraction error "
            "for document %s",
            document.pk,
        )

        document.extracted_text = ""

        document.extraction_status = (
            "failed"
        )

        document.extraction_error = (
            "An unexpected extraction "
            "error occurred."
        )

    else:

        document.extracted_text = (
            extracted_text
        )

        document.extraction_status = (
            "ready"
        )

        document.extraction_error = ""

    document.save(
        update_fields=[
            "extracted_text",
            "extraction_status",
            "extraction_error",
            "updated_at",
        ]
    )