import re
from typing import List, Dict, Optional, Tuple
from app.schemas import CustomerSchema, InvoiceItemSchema, ExtractResponseSchema
from app.services.pricing import PricingService


class ExtractionService:
    def __init__(self, pricing_service: PricingService):
        self.pricing_service = pricing_service

    def extract(self, text: str) -> ExtractResponseSchema:
        """Extract invoice information from natural language text."""
        customer = self._extract_customer(text)
        items, unmatched = self._extract_services(text)
        notes = self._extract_notes(text)

        # Extract discount from notes
        discount = 0.0
        if notes and "discount" in notes.lower():
            discount_pattern = r'(\d+)%'
            discount_match = re.search(discount_pattern, notes)
            if discount_match:
                discount = float(discount_match.group(1))

        return ExtractResponseSchema(
            customer=customer,
            items=items,
            notes=notes,
            extraction_source="Smart local extraction",
            unmatched_services=unmatched,
            discount=discount
        )

    def _extract_customer(self, text: str) -> CustomerSchema:
        """Extract customer information from text."""
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text, re.IGNORECASE)
        email = emails[0] if emails else ""

        # Extract phone number (Indian format)
        phone_pattern = r'[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}'
        phones = re.findall(phone_pattern, text)
        phone = phones[0] if phones else None

        # Extract name - look for patterns like "for [Name]" or "[Name] needs"
        # Remove email and phone from text first
        text_clean = text
        for e in emails:
            text_clean = text_clean.replace(e, "")
        for p in phones:
            text_clean = text_clean.replace(p, "")

        # Try to extract name from common patterns
        name_patterns = [
            r'(?:for|invoice for|create invoice for)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+needs',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+@',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+\(',
        ]

        name = "Customer"
        for pattern in name_patterns:
            match = re.search(pattern, text_clean, re.IGNORECASE)
            if match:
                potential_name = match.group(1).strip()
                # Basic validation: should be 2-50 chars, mostly letters
                if 2 <= len(potential_name) <= 50 and potential_name.replace(" ", "").isalpha():
                    name = potential_name.title()
                    break

        return CustomerSchema(
            name=name,
            email=email if email else "customer@example.com",
            phone=phone
        )

    def _extract_services(self, text: str) -> Tuple[List[InvoiceItemSchema], List[str]]:
        """Extract services and quantities from text."""
        services = self.pricing_service.get_all_services()
        items = []
        unmatched = []

        # Build a mapping of service names to service data
        service_map = {}
        for service in services:
            service_map[service.service_name.lower()] = service
            # Also add common variations
            service_map[service.service_name.lower().replace(" ", "")] = service

        # Extract quantities and service mentions
        text_lower = text.lower()

        # Pattern for "X service" or "service X" where X is a number
        quantity_patterns = [
            r'(\d+)\s+([a-z\s]+(?:design|development|campaign|optimization|consultation|writing|photography|editing|marketing))',
            r'([a-z\s]+(?:design|development|campaign|optimization|consultation|writing|photography|editing|marketing))\s+(\d+)',
        ]

        # Track which services we've found
        found_services = {}

        for pattern in quantity_patterns:
            matches = re.finditer(pattern, text_lower)
            for match in matches:
                if pattern == quantity_patterns[0]:
                    quantity = int(match.group(1))
                    service_text = match.group(2).strip()
                else:
                    service_text = match.group(1).strip()
                    quantity = int(match.group(2))

                # Try to match against service catalogue
                matched_service = self._fuzzy_match_service(service_text, service_map)
                if matched_service:
                    if matched_service.service_name not in found_services:
                        found_services[matched_service.service_name] = {
                            'service': matched_service,
                            'quantity': quantity
                        }
                    else:
                        found_services[matched_service.service_name]['quantity'] += quantity

        # Also look for services without explicit quantities (assume 1)
        for service_name, service in service_map.items():
            if service_name in text_lower and service.service_name not in found_services:
                # Check if it's not part of a larger word
                pattern = r'\b' + re.escape(service_name) + r'\b'
                if re.search(pattern, text_lower):
                    found_services[service.service_name] = {
                        'service': service,
                        'quantity': 1
                    }

        # Convert to invoice items
        for service_name, data in found_services.items():
            service = data['service']
            quantity = data['quantity']
            items.append(InvoiceItemSchema(
                service_id=service.id,
                service_name=service.service_name,
                description=service.description,
                quantity=quantity,
                unit_price=service.unit_price,
                tax_rate=service.tax_rate
            ))

        # Try to identify unmatched services
        # Look for words that might be services but aren't in our catalogue
        potential_services = [
            'website', 'web', 'app', 'application', 'logo', 'social', 'media',
            'seo', 'marketing', 'content', 'photography', 'video', 'consulting',
            'consultation', 'design', 'development', 'campaign', 'optimization'
        ]

        for word in potential_services:
            if word in text_lower:
                # Check if we already matched something containing this word
                matched = any(word in item.service_name.lower() for item in items)
                if not matched:
                    unmatched.append(word.capitalize())

        return items, list(set(unmatched))

    def _fuzzy_match_service(self, service_text: str, service_map: Dict) -> Optional:
        """Fuzzy match service text against catalogue."""
        service_text_clean = service_text.strip().lower()

        # Direct match
        if service_text_clean in service_map:
            return service_map[service_text_clean]

        # Partial match - check if service_text is contained in or contains a catalogue entry
        for key, service in service_map.items():
            if service_text_clean in key or key in service_text_clean:
                return service

        # Word overlap match
        service_words = set(service_text_clean.split())
        for key, service in service_map.items():
            key_words = set(key.split())
            # If more than 50% of words match
            overlap = len(service_words & key_words)
            if overlap > 0 and overlap / max(len(service_words), len(key_words)) > 0.5:
                return service

        return None

    def _extract_notes(self, text: str) -> Optional[str]:
        """Extract notes or special instructions from text."""
        notes = []

        # Look for discount mentions
        discount_pattern = r'(?:discount|off)\s*(\d+)%'
        discount_match = re.search(discount_pattern, text, re.IGNORECASE)
        if discount_match:
            notes.append(f"Apply {discount_match.group(1)}% discount")

        # Look for urgency notes
        if re.search(r'\b(urgent|asap|immediately)\b', text, re.IGNORECASE):
            notes.append("Urgent request")

        return ' '.join(notes) if notes else None
