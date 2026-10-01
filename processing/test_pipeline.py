#python3 -m processing.test_pipeline
from processing.pipeline import EmailProcessingPipeline


pipeline = EmailProcessingPipeline()


result = pipeline.process_file(
    "sample_emails/order.eml"
)


print("Email:")
print(result["email"])

print()

print("AI response:")
print(result["ai_response"])

print()

print("Validated order:")
print(result["validated_order"])