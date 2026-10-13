# AI Email Automation | Django & Gemini AI

**AI-powered email processing that transforms unstructured messages into validated business data.**

## Overview

AI Email Automation is a Python and Django application that uses Google Gemini to extract structured information from email content, validates the results with Pydantic, and prepares data for CRM and ERP integrations.

The goal is to reduce manual data entry, improve data consistency, and automate repetitive business workflows.

## Key Features

* Email parsing and HTML cleanup
* Gemini AI-powered information extraction
* Pydantic schema validation
* Background job processing
* Retry handling and failure recovery
* Idempotency and duplicate prevention
* Stale-job recovery
* CRM and ERP integration interfaces
* Automated testing with pytest

## Technology Stack

* **Backend:** Python, Django
* **AI Integration:** Google Gemini
* **Data Validation:** Pydantic
* **Email Processing:** BeautifulSoup
* **Database:** SQLite or configured database
* **Testing:** pytest
* **Version Control:** Git and GitHub

## Architecture

```text
Email Content
     ↓
Parsing & HTML Cleanup
     ↓
Gemini AI Extraction
     ↓
Pydantic Validation
     ↓
Background Processing
     ↓
CRM / ERP Integration
```

## Installation

```bash
git clone <https://github.com/Malaminjagana/AI-Email-Automation.gitL>
cd "AI Email automation"

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
python manage.py migrate
python manage.py check
python manage.py runserver
```

Configure the required environment variables, including `GEMINI_API_KEY`, before testing AI-powered functionality.

## API Endpoints

| Endpoint           | Method | Purpose                   |
| ------------------ | ------ | ------------------------- |
| `/health/`         | GET    | Check API status          |
| `/emails/test/`    | GET    | Inspect sample email data |
| `/emails/analyze/` | POST   | Analyze email content     |

## Testing

```bash
python -m pytest -v
python manage.py check
```

## Skills Demonstrated Through This Project

* Python and Django backend engineering
* AI and LLM API integration
* Prompt engineering and structured extraction
* Data validation and error handling
* Background jobs and retry mechanisms
* Database modeling and migrations
* API integration and software architecture
* Automated testing and debugging
* Secure configuration and maintainable code

## Future Improvements

* Gmail and Microsoft 365 inbox integration
* Automated email ingestion and processing
* Monitoring dashboard and operational alerts
* Production deployment and CI/CD
* Expanded CRM and ERP integrations

## About the Developer

**Malamin Jagana — Full-Stack Engineer & AI Systems Developer**

I develop web applications, backend APIs, and AI-powered automation solutions using Python, Django, React, Angular, Node.js, and modern LLM technologies.

* **Portfolio:** https://malamin-profile.vercel.app/
* **LinkedIn:** https://www.linkedin.com/in/malamin-jagana/
* **GitHub:** https://github.com/malaminjagana

## Project Value

This project demonstrates my ability to combine AI integration with structured data validation, reliable backend workflows, automated testing, and business-system integration design.

My focus is building maintainable software that solves practical business problems and provides a foundation for scalable automation.
