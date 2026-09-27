import pytest
from app.services.extractor import ExtractionService
from app.services.pricing import PricingService


@pytest.fixture
def pricing_service():
    return PricingService()


@pytest.fixture
def extraction_service(pricing_service):
    return ExtractionService(pricing_service)


def test_extract_customer_simple(extraction_service):
    """Test basic customer extraction."""
    text = "Create an invoice for Rahul Sharma, rahul@example.com"
    result = extraction_service.extract(text)
    
    assert result.customer.name == "Rahul Sharma"
    assert result.customer.email == "rahul@example.com"


def test_extract_customer_with_phone(extraction_service):
    """Test customer extraction with phone number."""
    text = "Create an invoice for Priya Mehta, priya@example.com, phone: +91-9876543210"
    result = extraction_service.extract(text)
    
    assert result.customer.name == "Priya Mehta"
    assert result.customer.email == "priya@example.com"
    assert result.customer.phone is not None


def test_extract_services_with_quantities(extraction_service):
    """Test service extraction with quantities."""
    text = "Create an invoice for Rahul Sharma, rahul@example.com. He needs 2 website design packages and 1 logo design."
    result = extraction_service.extract(text)
    
    assert len(result.items) == 2
    
    # Check Website Design
    website_item = next((item for item in result.items if "website" in item.service_name.lower()), None)
    assert website_item is not None
    assert website_item.quantity == 2
    assert website_item.unit_price == 25000.0
    
    # Check Logo Design
    logo_item = next((item for item in result.items if "logo" in item.service_name.lower()), None)
    assert logo_item is not None
    assert logo_item.quantity == 1
    assert logo_item.unit_price == 5000.0


def test_extract_services_single(extraction_service):
    """Test service extraction with single item."""
    text = "Priya Mehta, priya@example.com needs one mobile app development project and UI/UX design."
    result = extraction_service.extract(text)
    
    assert len(result.items) == 2
    
    # Check Mobile App Development
    mobile_item = next((item for item in result.items if "mobile" in item.service_name.lower()), None)
    assert mobile_item is not None
    assert mobile_item.quantity == 1
    assert mobile_item.unit_price == 80000.0
    
    # Check UI/UX Design
    ui_item = next((item for item in result.items if "ui" in item.service_name.lower()), None)
    assert ui_item is not None
    assert ui_item.quantity == 1
    assert ui_item.unit_price == 30000.0


def test_extract_unmatched_services(extraction_service):
    """Test that unknown services are reported as unmatched."""
    text = "Create an invoice for John Smith, john@example.com. He needs custom blockchain development and AI integration."
    result = extraction_service.extract(text)
    
    # Should have no matched items
    assert len(result.items) == 0
    
    # Should have unmatched services
    assert len(result.unmatched_services) > 0


def test_extract_urgent_note(extraction_service):
    """Test urgent request detection."""
    text = "Create an invoice for Rahul Sharma, rahul@example.com. This is urgent."
    result = extraction_service.extract(text)
    
    assert result.notes is not None
    assert "Urgent" in result.notes


def test_extraction_source(extraction_service):
    """Test that extraction source is set correctly."""
    text = "Create an invoice for Rahul Sharma, rahul@example.com"
    result = extraction_service.extract(text)
    
    assert result.extraction_source == "Smart local extraction"


def test_calculate_item_amounts(extraction_service):
    """Test that item amounts are calculated correctly."""
    text = "Create an invoice for Rahul Sharma, rahul@example.com. He needs 2 website design packages."
    result = extraction_service.extract(text)
    
    assert len(result.items) == 1
    item = result.items[0]
    
    # Amount should be quantity * unit_price
    expected_amount = 2 * 25000.0
    assert item.quantity * item.unit_price == expected_amount
