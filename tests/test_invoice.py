import pytest
from app.services.invoice import InvoiceService
from app.schemas import InvoiceCreateSchema, CustomerSchema, InvoiceItemSchema, InvoiceUpdateSchema
from app.models import InvoiceStatus
import uuid


@pytest.fixture
def invoice_service():
    return InvoiceService(db_path="data/test_invoices.db")


@pytest.fixture
def sample_invoice_data():
    return InvoiceCreateSchema(
        customer=CustomerSchema(
            name="Test Customer",
            email="test@example.com",
            phone="+91-9876543210",
            address="123 Test Street"
        ),
        items=[
            InvoiceItemSchema(
                service_name="Website Design",
                description="Professional website design package",
                quantity=2,
                unit_price=25000.0,
                tax_rate=18.0
            ),
            InvoiceItemSchema(
                service_name="Logo Design",
                description="Professional logo design",
                quantity=1,
                unit_price=5000.0,
                tax_rate=18.0
            )
        ],
        discount=0.0,
        notes="Test invoice"
    )


def test_create_invoice(invoice_service, sample_invoice_data):
    """Test invoice creation."""
    invoice = invoice_service.create_invoice(sample_invoice_data)
    
    assert invoice is not None
    assert invoice.id is not None
    assert invoice.invoice_number.startswith("INV-2026-")
    assert invoice.customer.name == "Test Customer"
    assert invoice.customer.email == "test@example.com"
    assert len(invoice.items) == 2
    assert invoice.status == InvoiceStatus.REVIEW


def test_calculate_totals(invoice_service, sample_invoice_data):
    """Test invoice total calculations."""
    invoice = invoice_service.create_invoice(sample_invoice_data)
    
    # Subtotal: (2 * 25000) + (1 * 5000) = 55000
    assert invoice.subtotal == 55000.0
    
    # Tax: 55000 * 0.18 = 9900
    assert invoice.tax == 9900.0
    
    # Total: 55000 + 9900 = 64900
    assert invoice.total == 64900.0


def test_create_invoice_with_discount(invoice_service):
    """Test invoice creation with discount."""
    invoice_data = InvoiceCreateSchema(
        customer=CustomerSchema(
            name="Test Customer",
            email="test@example.com"
        ),
        items=[
            InvoiceItemSchema(
                service_name="Website Design",
                description="Professional website design package",
                quantity=1,
                unit_price=25000.0,
                tax_rate=18.0
            )
        ],
        discount=1000.0,
        notes="Test with discount"
    )
    
    invoice = invoice_service.create_invoice(invoice_data)
    
    # Subtotal: 25000
    assert invoice.subtotal == 25000.0
    
    # Tax: 25000 * 0.18 = 4500
    assert invoice.tax == 4500.0
    
    # Total: 25000 - 1000 + 4500 = 28500
    assert invoice.total == 28500.0
    assert invoice.discount == 1000.0


def test_get_invoice(invoice_service, sample_invoice_data):
    """Test retrieving an invoice by ID."""
    created_invoice = invoice_service.create_invoice(sample_invoice_data)
    retrieved_invoice = invoice_service.get_invoice(created_invoice.id)
    
    assert retrieved_invoice is not None
    assert retrieved_invoice.id == created_invoice.id
    assert retrieved_invoice.invoice_number == created_invoice.invoice_number
    assert retrieved_invoice.customer.name == created_invoice.customer.name


def test_get_nonexistent_invoice(invoice_service):
    """Test retrieving a non-existent invoice."""
    fake_id = str(uuid.uuid4())
    invoice = invoice_service.get_invoice(fake_id)
    
    assert invoice is None


def test_update_invoice(invoice_service, sample_invoice_data):
    """Test updating an invoice."""
    created_invoice = invoice_service.create_invoice(sample_invoice_data)
    
    update_data = InvoiceUpdateSchema(
        customer=CustomerSchema(
            name="Updated Customer",
            email="updated@example.com"
        ),
        discount=500.0,
        notes="Updated notes"
    )
    
    updated_invoice = invoice_service.update_invoice(created_invoice.id, update_data)
    
    assert updated_invoice is not None
    assert updated_invoice.customer.name == "Updated Customer"
    assert updated_invoice.customer.email == "updated@example.com"
    assert updated_invoice.discount == 500.0
    assert updated_invoice.notes == "Updated notes"


def test_approve_invoice(invoice_service, sample_invoice_data):
    """Test approving an invoice."""
    created_invoice = invoice_service.create_invoice(sample_invoice_data)
    
    approved_invoice = invoice_service.approve_invoice(created_invoice.id)
    
    assert approved_invoice is not None
    assert approved_invoice.status == InvoiceStatus.APPROVED


def test_get_all_invoices(invoice_service, sample_invoice_data):
    """Test retrieving all invoices."""
    # Create multiple invoices
    invoice_service.create_invoice(sample_invoice_data)
    invoice_service.create_invoice(sample_invoice_data)
    
    invoices = invoice_service.get_all_invoices()
    
    assert len(invoices) >= 2


def test_invoice_number_generation(invoice_service, sample_invoice_data):
    """Test that invoice numbers are generated correctly."""
    invoice1 = invoice_service.create_invoice(sample_invoice_data)
    invoice2 = invoice_service.create_invoice(sample_invoice_data)
    
    assert invoice1.invoice_number != invoice2.invoice_number
    assert invoice1.invoice_number.startswith("INV-2026-")
    assert invoice2.invoice_number.startswith("INV-2026-")
