# Smart Invoice Challenge

A FastAPI-based invoice generation system with natural language extraction capabilities.

## Features

- **Natural Language Extraction**: Extract invoice details from conversational text
- **Invoice Management**: Create, update, approve, and retrieve invoices
- **PDF Generation**: Generate professional PDF invoices
- **RESTful API**: Full CRUD operations for invoices
- **Health Check**: Endpoint for monitoring

## Tech Stack

- **FastAPI**: Modern web framework for building APIs
- **Pydantic**: Data validation using Python type annotations
- **ReportLab**: PDF generation
- **Jinja2**: Template engine
- **SQLite**: Database for invoice storage

## Installation

```bash
pip install -r requirements.txt
```

## Running the Application

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

### Health Check
- `GET /health` - Health check endpoint

### Services
- `GET /api/services` - Get all available services

### Extraction
- `POST /api/extract` - Extract invoice data from natural language

### Invoices
- `POST /api/invoices` - Create a new invoice
- `GET /api/invoices` - Get all invoices
- `GET /api/invoices/{invoice_id}` - Get a specific invoice
- `PUT /api/invoices/{invoice_id}` - Update an invoice
- `POST /api/invoices/{invoice_id}/approve` - Approve an invoice
- `GET /api/invoices/{invoice_id}/pdf` - Generate PDF for an invoice

## Testing

Run the test suite:

```bash
pytest tests/ -v
```

## Project Structure

```
chatbot/
├── app/
│   ├── api/
│   │   └── routes.py       # API endpoints
│   ├── services/
│   │   ├── extractor.py    # Natural language extraction
│   │   ├── invoice.py      # Invoice business logic
│   │   ├── pdf.py          # PDF generation
│   │   └── pricing.py      # Service pricing catalogue
│   ├── main.py             # FastAPI application
│   ├── models.py           # Data models
│   └── schemas.py          # Pydantic schemas
├── tests/
│   ├── test_extractor.py   # Extraction service tests
│   └── test_invoice.py     # Invoice service tests
├── templates/
│   └── invoice.html        # PDF template
├── data/
│   └── invoices.db         # SQLite database
└── requirements.txt        # Python dependencies
```

## License

MIT License
