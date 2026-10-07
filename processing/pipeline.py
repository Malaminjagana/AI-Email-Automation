import logging

from ai.extractor import OrderExtractor
from ai.llm import LLMService
from ai.prompts import EMAIL_ANALYSIS_PROMPT
from ai.retry import generate_with_retry
from emails.services import EmailParser, EmailReader
from processing.result import ProcessingResult
from integrations.crm import CRMService

logger = logging.getLogger(__name__)


class EmailProcessingPipeline:

    def __init__(self):
        self.reader = EmailReader()
        self.parser = EmailParser()
        self.llm = LLMService()
        self.extractor = OrderExtractor()
        self.crm = CRMService()
       

    def process_file(self, file_path: str):

        logger.info(
            "Starting email processing: %s",
            file_path,
        )

        try:

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

            ai_response = generate_with_retry(
                self.llm,
                prompt,
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
            crm_order = self.crm.create_order (
                order 
            )
            
            logger.info(
                "Oder sucesfully send to CRM."
            )

            logger.info(
                "Email processing completed successfully."
            )

            return {
                "email": email_data,
                "ai_response": ai_response,
                "validated_order": order,
            }
         
            

        except Exception:
            logger.exception(
                "Email processing failed: %s",
                file_path,
            )
            raise