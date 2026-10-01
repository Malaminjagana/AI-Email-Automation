EMAIL_ANALYSIS_PROMPT = """
You are an AI assistant that extracts order information from business emails.

Extract the following fields:

- customer
- product
- quantity
- delivery_location

Rules:

1. Return ONLY valid JSON.
2. Do not include markdown.
3. Do not include explanations.
4. Do not invent information.
5. If a value is not present in the email, use null.

Expected format:

{{
    "customer": "...",
    "product": "...",
    "quantity": 0,
    "delivery_location": "..."
}}

Email:
{email_content}
"""