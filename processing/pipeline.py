
import logging

from ai.extractor import OrderExtractor
from ai.llm import LLMService
from ai.prompts import EMAIL_ANALYSIS_PROMPT
from ai.retry import generate_with_retry
from emails.services import EmailParser, EmailReader
from integrations.crm import CRMService
from integrations.erp import ERPService
from processing.ports import ProcessingRecordStorePort
from processing.records import DatabaseProcessingRecordStore
from processing.result import ProcessingResult


logger = logging.getLogger(__name__)


class EmailProcessingPipeline:

    def __init__(
        self,
        reader=None,
        parser=None,
        llm=None,
        extractor=None,
        crm=None,
        erp=None,
        record_store: ProcessingRecordStorePort | None = None,
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

        self.record_store = (
            record_store
            if record_store is not None
            else DatabaseProcessingRecordStore()
        )

    def process_file(
        self,
        file_path: str,
    ) -> ProcessingResult | None:

        message_id = None
        claimed = False

        logger.info(
            "Starting email processing: %s",
            file_path,
        )

        try:

            raw_email = self.reader.read_file(file_path)

            logger.info("Email file read successfully.")

            email_data = self.parser.parse(raw_email)

            logger.info("Email parsed successfully.")

            message_id = email_data.get("message_id")

            if message_id:

                claimed = self.record_store.claim(message_id)

                if not claimed:

                    logger.info(
                        "Email is already processing or completed: %s",
                        message_id,
                    )

                    return None

            else:

                logger.warning(
                    "Email has no Message-ID; duplicate protection "
                    "cannot be applied: %s",
                    file_path,
                )

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

            if claimed and message_id:

                self.record_store.mark_completed(message_id)

                logger.info(
                    "Email marked as completed: %s",
                    message_id,
                )

            logger.info(
                "Email processing completed successfully."
            )

            return result

        except Exception as exc:

            if claimed and message_id:

                try:

                    self.record_store.mark_failed(
                        message_id,
                        exc,
                    )

                except Exception:

                    logger.exception(
                        "Could not persist the failure status "
                        "for email: %s",
                        message_id,
                    )

            logger.exception(
                "Email processing failed: %s",
                file_path,
            )

            raise