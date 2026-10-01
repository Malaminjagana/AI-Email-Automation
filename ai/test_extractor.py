from ai.extractor import (
    OrderExtractor,
    InvalidJSONError,
)


extractor = OrderExtractor()


bad_response = """
This is not JSON.
"""


try:
    extractor.extract(bad_response)

except InvalidJSONError as exc:
    print("Caught expected error:")
    print(exc)