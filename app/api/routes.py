from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import StreamingResponse
from typing import List
from app.schemas import (
    ExtractRequestSchema, ExtractResponseSchema,
    InvoiceCreateSchema, InvoiceUpdateSchema, InvoiceResponseSchema,
    ServiceSchema, HealthResponseSchema
)
from app.services.extractor import ExtractionService
from app.services.pricing import PricingService
from app.services.invoice import InvoiceService
from app.services.pdf import PDFService
from app.models import InvoiceStatus


router = APIRouter()

# Initialize services
pricing_service = PricingService()
extraction_service = ExtractionService(pricing_service)
invoice_service = InvoiceService()
pdf_service = PDFService()


@router.get("/health", response_model=HealthResponseSchema)
async def health_check():
    """Health check endpoint for Render."""
    return HealthResponseSchema(status="ok")


@router.get("/api/services", response_model=List[ServiceSchema])
async def get_services():
    """Get all services from the pricing catalogue."""
    services = pricing_service.get_all_services()
    return [ServiceSchema(
        id=s.id,
        service_name=s.service_name,
        description=s.description,
        unit=s.unit,
        unit_price=s.unit_price,
        tax_rate=s.tax_rate
    ) for s in services]


@router.post("/api/extract", response_model=ExtractResponseSchema)
async def extract_invoice_data(request: ExtractRequestSchema):
    """Extract invoice information from natural language."""
    try:
        result = extraction_service.extract(request.text)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/api/invoices", response_model=InvoiceResponseSchema)
async def create_invoice(schema: InvoiceCreateSchema):
    """Create a new invoice."""
    try:
        invoice = invoice_service.create_invoice(schema)
        return _invoice_to_response(invoice)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/api/invoices", response_model=List[InvoiceResponseSchema])
async def get_invoices():
    """Get all invoices."""
    try:
        invoices = invoice_service.get_all_invoices()
        return [_invoice_to_response(inv) for inv in invoices]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/invoices/{invoice_id}", response_model=InvoiceResponseSchema)
async def get_invoice(invoice_id: str):
    """Get a specific invoice by ID."""
    invoice = invoice_service.get_invoice(invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return _invoice_to_response(invoice)


@router.put("/api/invoices/{invoice_id}", response_model=InvoiceResponseSchema)
async def update_invoice(invoice_id: str, schema: InvoiceUpdateSchema):
    """Update an invoice."""
    try:
        invoice = invoice_service.update_invoice(invoice_id, schema)
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")
        return _invoice_to_response(invoice)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/api/invoices/{invoice_id}/approve", response_model=InvoiceResponseSchema)
async def approve_invoice(invoice_id: str):
    """Approve an invoice."""
    try:
        invoice = invoice_service.approve_invoice(invoice_id)
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")
        return _invoice_to_response(invoice)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/api/invoices/{invoice_id}/pdf")
async def get_invoice_pdf(invoice_id: str):
    """Generate and download invoice PDF."""
    invoice = invoice_service.get_invoice(invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    try:
        pdf_buffer = pdf_service.generate_invoice_pdf(invoice)
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={invoice.invoice_number}.pdf"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")


def _invoice_to_response(invoice) -> InvoiceResponseSchema:
    """Convert invoice model to response schema."""
    from app.schemas import CustomerSchema, InvoiceItemSchema

    return InvoiceResponseSchema(
        id=invoice.id,
        invoice_number=invoice.invoice_number,
        invoice_date=invoice.invoice_date,
        due_date=invoice.due_date,
        customer=CustomerSchema(
            name=invoice.customer.name,
            email=invoice.customer.email,
            phone=invoice.customer.phone,
            address=invoice.customer.address
        ),
        items=[
            InvoiceItemSchema(
                service_id=item.service_id,
                service_name=item.service_name,
                description=item.description,
                quantity=item.quantity,
                unit_price=item.unit_price,
                tax_rate=item.tax_rate
            )
            for item in invoice.items
        ],
        subtotal=invoice.subtotal,
        discount=invoice.discount,
        tax=invoice.tax,
        total=invoice.total,
        notes=invoice.notes,
        status=invoice.status
    )
