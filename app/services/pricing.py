import csv
import os
from typing import List, Optional
from app.models import Service


class PricingService:
    def __init__(self, csv_path: str = "data/services.csv"):
        self.csv_path = csv_path
        self._services: List[Service] = []
        self._load_services()

    def _load_services(self):
        """Load services from CSV file."""
        if not os.path.exists(self.csv_path):
            # Create default services if file doesn't exist
            self._create_default_services()
            return

        try:
            with open(self.csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    service = Service(
                        id=row['id'],
                        service_name=row['service_name'],
                        description=row['description'],
                        unit=row['unit'],
                        unit_price=float(row['unit_price']),
                        tax_rate=float(row['tax_rate'])
                    )
                    self._services.append(service)
        except Exception as e:
            print(f"Error loading services: {e}")
            self._create_default_services()

    def _create_default_services(self):
        """Create default services if CSV doesn't exist."""
        default_services = [
            Service("S001", "Website Design", "Professional website design package", "project", 25000.0, 18.0),
            Service("S002", "Website Development", "Full-stack website development", "project", 50000.0, 18.0),
            Service("S003", "Logo Design", "Professional logo design", "project", 5000.0, 18.0),
            Service("S004", "Social Media Campaign", "Complete social media marketing campaign", "campaign", 15000.0, 18.0),
            Service("S005", "SEO Optimization", "Search engine optimization services", "project", 20000.0, 18.0),
            Service("S006", "Mobile App Development", "Native mobile app development", "project", 80000.0, 18.0),
            Service("S007", "UI/UX Design", "User interface and experience design", "project", 30000.0, 18.0),
            Service("S008", "Content Writing", "Professional content writing services", "word", 2.0, 18.0),
            Service("S009", "Product Photography", "Professional product photography", "hour", 5000.0, 18.0),
            Service("S010", "Video Editing", "Professional video editing", "hour", 3000.0, 18.0),
            Service("S011", "Digital Marketing", "Comprehensive digital marketing", "month", 25000.0, 18.0),
            Service("S012", "Business Consultation", "Business strategy consultation", "hour", 5000.0, 18.0),
        ]
        self._services = default_services

    def get_all_services(self) -> List[Service]:
        """Get all services."""
        return self._services

    def get_service_by_id(self, service_id: str) -> Optional[Service]:
        """Get a service by ID."""
        for service in self._services:
            if service.id == service_id:
                return service
        return None

    def get_service_by_name(self, service_name: str) -> Optional[Service]:
        """Get a service by name (case-insensitive)."""
        service_name_lower = service_name.lower()
        for service in self._services:
            if service.service_name.lower() == service_name_lower:
                return service
        return None

    def search_services(self, query: str) -> List[Service]:
        """Search services by name or description."""
        query_lower = query.lower()
        results = []
        for service in self._services:
            if (query_lower in service.service_name.lower() or
                query_lower in service.description.lower()):
                results.append(service)
        return results
