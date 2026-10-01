import logging

from ai.extractor import OrderExtractor
from ai.llm import LLMService
from ai.prompts import EMAIL_ANALYSIS_PROMPT
from emails.services import EmailParser, EmailReader


logger = logging.getLogger(__name__)


class EmailProcessingPipeline:

    def __init__(self):
        self.reader = EmailReader()
        self.parser = EmailParser()
        self.llm = LLMService()
        self.extractor = OrderExtractor()

    def process_file(self, file_path: str):

        logger.info(
            "Starting email processing: %s",
            file_path,
        )

        raw_email = self.reader.read_file(
            file_path
        )

        logger.info(
            "Email file read successfully."
        )

        email_data = self.parser.parse(
            raw_email
        )

        logger.info(
            "Email parsed successfully."
        )

        prompt = EMAIL_ANALYSIS_PROMPT.format(
            email_content=email_data["body"]
        )

        logger.info(
            "Sending email content to LLM."
        )

        ai_response = self.llm.generate(
            prompt
        )

        logger.info(
            "LLM response received."
        )

        order = self.extractor.extract(
            ai_response
        )

        logger.info(
            "Order validated successfully."
        )

        return {
            "email": email_data,
            "ai_response": ai_response,
            "validated_order": order,
        }