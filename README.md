# AI Email Automation System

An AI-powered email processing system built with Django and Python.

## Goal

The system receives business emails, extracts structured information using an LLM, validates the extracted data, and prepares it for downstream systems such as CRM, ERP, or ticketing platforms.

## Current architecture

```text
Email
  ↓
Email Reader
  ↓
Email Parser
  ↓
Prompt
  ↓
LLM Service
  ↓
JSON
  ↓
Order Extractor
  ↓
Pydantic Validation
  ↓
Validated Order


git clone <repository-url>
cd "AI Email automation"

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

A Django-based AI email-processing pipeline that parses incoming email content, sends normalized text to an LLM for structured information extraction, validates the result with Pydantic, handles failures through controlled application errors, and is covered by automated unit, pipeline, and API tests.