
import logging

from ai.extractor import OrderExtractor
from ai.llm import LLMService
from ai.prompts import EMAIL_ANALYSIS_PROMPT
from ai.retry import generate_with_retry
from emails.services import EmailParser, EmailReader
from integrations.crm import CRMService
from integrations.erp import ERPService
from processing.idempotency import IdempotencyStore
from processing.ports import (
    EmailParserPort,
    EmailReaderPort,
    IdempotencyStorePort,
    LLMPort,
    OrderDestinationPort,
    OrderExtractorPort,
)
from processing.result import ProcessingResult


logger = logging.getLogger(__name__)


class EmailProcessingPipeline:

    def __init__(
        self,
        reader: EmailReaderPort | None = None,
        parser: EmailParserPort | None = None,
        llm: LLMPort | None = None,
        extractor: OrderExtractorPort | None = None,
        crm: OrderDestinationPort | None = None,
        erp: OrderDestinationPort | None = None,
        idempotency_store: IdempotencyStorePort | None = None,
    ):

        self.reader = (
            reader if reader is not None else EmailReader()
        )

        self.parser = (
            parser if parser is not None else EmailParser()
        )

        self.llm = (
            llm if llm is not None else LLMService()
        )

        self.extractor = (
            extractor
            if extractor is not None
            else OrderExtractor()
        )

        self.crm = (
            crm if crm is not None else CRMService()
        )

        self.erp = (
            erp if erp is not None else ERPService()
        )

        self.idempotency_store = (
            idempotency_store
            if idempotency_store is not None
            else IdempotencyStore()
        )

    def process_file(
        self,
        file_path: str,
    ) -> ProcessingResult | None:

        logger.info(
            "Starting email processing: %s",
            file_path,
        )

        try:

            raw_email = self.reader.read_file(file_path)

            logger.info("Email file read successfully.")

            email_data = self.parser.parse(raw_email)

            logger.info("Email parsed successfully.")

            message_id = email_data["message_id"]

            if (
                message_id
                and self.idempotency_store.has_been_processed(
                    message_id
                )
            ):

                logger.info(
                    "Email already processed: %s",
                    message_id,
                )

                return None

            prompt = EMAIL_ANALYSIS_PROMPT.format(
                email_content=email_data["body"]
            )

            logger.info("Sending email content to LLM.")

            ai_response = generate_with_retry(
                self.llm,
                prompt,
            )

            logger.info("LLM response received.")

            order = self.extractor.extract(ai_response)

            logger.info("Order validated successfully.")

            crm_order = self.crm.create_order(order)

            logger.info("Order successfully sent to CRM.")

            erp_order = self.erp.create_order(order)

            logger.info("Order successfully sent to ERP.")

            result = ProcessingResult(
                email=email_data,
                ai_response=ai_response,
                validated_order=order,
                crm_order=crm_order,
                erp_order=erp_order,
            )

            if message_id:

                self.idempotency_store.mark_as_processed(
                    message_id
                )

                logger.info(
                    "Email marked as processed: %s",
                    message_id,
                )

            logger.info(
                "Email processing completed successfully."
            )

            return result

        except Exception:

            logger.exception(
                "Email processing failed: %s",
                file_path,
            )

            raise