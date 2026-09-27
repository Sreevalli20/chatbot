# InvoiceAI - Smart Invoice Automation

A FastAPI-based invoice generation system with natural language extraction capabilities that transforms customer requests into professional invoices.

## Challenge Workflow

This application implements the complete invoice automation challenge:

1. **Customer Requirement** - User enters natural language description of invoice needs
2. **AI/Smart Extraction** - System extracts customer details, services, quantities from text
3. **Service Price Lookup** - Matches requested services against catalogue to retrieve real prices
4. **Invoice Generation** - Creates invoice with dynamic calculations (subtotal, tax, total)
5. **Review/Approval** - User can review and approve the invoice before finalization
6. **Professional PDF** - Generates downloadable PDF with actual invoice data

## Features

- **Natural Language Extraction**: Extracts customer name, email, phone, services, and quantities from conversational text
- **Dynamic Service Matching**: Fuzzy matches user requests against service catalogue
- **Real Price Lookup**: Uses actual service prices from CSV catalogue (no hardcoded prices)
- **Dynamic Calculations**: Automatically calculates line totals, subtotal, tax, and grand total
- **Invoice Management**: Create, update, approve, and retrieve invoices
- **PDF Generation**: Generates professional PDF invoices using ReportLab
- **Web Interface**: User-friendly UI for the complete invoice workflow
- **RESTful API**: Full CRUD operations for invoices
- **Health Check**: Endpoint for monitoring

## Tech Stack

- **FastAPI**: Modern web framework for building APIs
- **Pydantic**: Data validation using Python type annotations
- **ReportLab**: PDF generation
- **Jinja2**: Template engine for HTML templates
- **SQLite**: Database for invoice storage
- **JavaScript**: Frontend interactivity

## Service Catalogue

The application uses a service catalogue stored in `data/services.csv` containing:

- Website Design (₹25,000/project)
- Website Development (₹50,000/project)
- Logo Design (₹5,000/project)
- Social Media Campaign (₹15,000/campaign)
- SEO Optimization (₹20,000/project)
- Mobile App Development (₹80,000/project)
- UI/UX Design (₹30,000/project)
- Content Writing (₹2/word)
- Product Photography (₹5,000/hour)
- Video Editing (₹3,000/hour)
- Digital Marketing (₹25,000/month)
- Business Consultation (₹5,000/hour)

All services have 18% tax rate.

## Installation

```bash
pip install -r requirements.txt
```

**Python Version**: Python 3.8+

## Running the Application

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Or for development with auto-reload:

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Testing

Run the test suite:

```bash
pytest tests/ -v
```

The test suite includes:
- Customer extraction tests
- Service extraction with quantities
- Fuzzy matching tests
- Unknown service handling
- Invoice creation and calculation tests
- Approval workflow tests
- PDF generation verification

## API Endpoints

### Health Check
- `GET /health` - Health check endpoint

### Web Interface
- `GET /` - Main application UI

### Services
- `GET /api/services` - Get all available services from catalogue

### Extraction
- `POST /api/extract` - Extract invoice data from natural language text
  - Input: `{"text": "customer request"}`
  - Output: Customer info, matched services, unmatched services, discount info

### Invoices
- `POST /api/invoices` - Create a new invoice
- `GET /api/invoices` - Get all invoices
- `GET /api/invoices/{invoice_id}` - Get a specific invoice
- `PUT /api/invoices/{invoice_id}` - Update an invoice
- `POST /api/invoices/{invoice_id}/approve` - Approve an invoice
- `GET /api/invoices/{invoice_id}/pdf` - Generate and download PDF for an invoice

## Invoice Calculation

The application performs dynamic calculations:

1. **Line Amount**: `quantity × unit_price`
2. **Subtotal**: Sum of all line amounts
3. **Tax**: Sum of `(line_amount × tax_rate / 100)` for each item
4. **Total**: `subtotal - discount + tax`

All calculations are performed server-side using actual catalogue prices.

## PDF Generation

PDFs are generated using ReportLab with:
- Company branding
- Invoice number and dates
- Customer details
- Itemized service list with quantities and prices
- Tax calculations
- Final totals
- Payment terms

## Render Deployment

The application is deployed on Render at: https://invoiceai-3xim.onrender.com

**Build Command**:
```bash
pip install -r requirements.txt
```

**Start Command**:
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## Demo Instructions

1. Open the application at `http://localhost:8000` (or the Render URL)
2. Enter a natural language request, for example:
   - "Create an invoice for Rahul Sharma, rahul@example.com. He needs 2 website design packages and 1 logo design."
   - "Generate an invoice for Priya Mehta, priya@example.com. She needs 3 social media campaigns and one SEO optimization service."
3. Click "Generate Invoice" to extract information
4. Review the extracted customer details and services
5. Click "Proceed to Review" to create the invoice
6. Review the complete invoice with calculated totals
7. Edit customer details or discount if needed
8. Click "Approve & Generate PDF" to finalize and download the PDF

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
│   ├── index.html          # Main web interface
│   └── static/
│       ├── css/
│       │   └── style.css   # Styling
│       └── js/
│           └── app.js      # Frontend logic
├── data/
│   ├── services.csv        # Service pricing catalogue
│   └── invoices.db         # SQLite database (created on first run)
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Challenge Mapping

- ✅ Customer Requirement - Natural language input via web interface
- ✅ AI/Smart Extraction - Regex-based extraction with fuzzy matching
- ✅ Service Price Lookup - CSV-based catalogue lookup
- ✅ Invoice Generation - Dynamic invoice creation with real calculations
- ✅ Review/Approval - Interactive review interface with approval workflow
- ✅ Professional PDF - ReportLab-based PDF generation

## License

MIT License
