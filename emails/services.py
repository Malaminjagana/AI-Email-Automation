
from email import policy
from email.parser import BytesParser
from pathlib import Path

from bs4 import BeautifulSoup


class EmailReader:
    def read_file(self, file_path: str) -> bytes:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Email file not found: {file_path}"
            )

        return path.read_bytes()


class EmailParser:
    def parse(self, raw_email: bytes) -> dict:
        message = BytesParser(
            policy=policy.default
        ).parsebytes(raw_email)

        return {
            "message_id": message.get("Message-ID"),
            "sender": message.get("From"),
            "recipient": message.get("To"),
            "subject": message.get("Subject"),
            "date": message.get("Date"),
            "body": self._extract_body(message),
        }

    def _extract_body(self, message) -> str:
        # If the email contains multiple parts,
        # such as plain text and HTML.
        if message.is_multipart():

            # First, try to find a plain-text version.
            plain_text = self._extract_plain_text(message)

            if plain_text:
                return plain_text

            # If no plain text exists, try HTML.
            html = self._extract_html(message)

            if html:
                return self._clean_html(html)

            # No usable body was found.
            return ""

        # Handle a simple non-multipart email.
        content_type = message.get_content_type()

        if content_type == "text/plain":
            return message.get_content()

        if content_type == "text/html":
            return self._clean_html(
                message.get_content()
            )

        return ""

    def _extract_plain_text(self, message) -> str:
        for part in message.walk():
            if part.get_content_type() == "text/plain":
                return part.get_content()

        return ""

    def _extract_html(self, message) -> str:
        for part in message.walk():
            if part.get_content_type() == "text/html":
                return part.get_content()

        return ""

    def _clean_html(self, html: str) -> str:
        soup = BeautifulSoup(
            html,
            "html.parser"
        )

        return soup.get_text(
            separator="\n",
            strip=True
        )

