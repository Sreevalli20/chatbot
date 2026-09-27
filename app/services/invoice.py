import sqlite3
import uuid
import os
from datetime import datetime, timedelta
from typing import List, Optional
from app.models import Invoice, Customer, InvoiceItem, InvoiceStatus
from app.schemas import InvoiceCreateSchema, InvoiceUpdateSchema


class InvoiceService:
    def __init__(self, db_path: str = "data/invoices.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        os.makedirs("data", exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS invoices (id TEXT PRIMARY KEY, invoice_number TEXT UNIQUE NOT NULL, invoice_date TEXT NOT NULL, due_date TEXT NOT NULL, customer_name TEXT NOT NULL, customer_email TEXT NOT NULL, customer_phone TEXT, customer_address TEXT, subtotal REAL NOT NULL, discount REAL DEFAULT 0, tax REAL NOT NULL, total REAL NOT NULL, notes TEXT, status TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS invoice_items (id TEXT PRIMARY KEY, invoice_id TEXT NOT NULL, service_id TEXT, service_name TEXT NOT NULL, description TEXT NOT NULL, quantity INTEGER NOT NULL, unit_price REAL NOT NULL, tax_rate REAL NOT NULL, amount REAL NOT NULL, FOREIGN KEY (invoice_id) REFERENCES invoices (id))''')
        conn.commit()
        conn.close()

    def _generate_invoice_number(self) -> str:
        year = datetime.now().year
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''SELECT COUNT(*) FROM invoices WHERE invoice_number LIKE ?''', (f'INV-{year}-%',))
        count = cursor.fetchone()[0]
        conn.close()
        sequence = count + 1
        return f'INV-{year}-{sequence:04d}'

    def create_invoice(self, schema: InvoiceCreateSchema) -> Invoice:
        invoice_id = str(uuid.uuid4())
        invoice_number = self._generate_invoice_number()
        now = datetime.now()
        due_date = schema.due_date or (now + timedelta(days=30))
        items = [InvoiceItem(service_id=item.service_id, service_name=item.service_name, description=item.description, quantity=item.quantity, unit_price=item.unit_price, tax_rate=item.tax_rate) for item in schema.items]
        invoice = Invoice(invoice_number=invoice_number, invoice_date=now, due_date=due_date, customer=Customer(name=schema.customer.name, email=schema.customer.email, phone=schema.customer.phone, address=schema.customer.address), items=items, discount=schema.discount, notes=schema.notes, status=InvoiceStatus.REVIEW)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO invoices (id, invoice_number, invoice_date, due_date, customer_name, customer_email, customer_phone, customer_address, subtotal, discount, tax, total, notes, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (invoice_id, invoice.invoice_number, invoice.invoice_date.isoformat(), invoice.due_date.isoformat(), invoice.customer.name, invoice.customer.email, invoice.customer.phone, invoice.customer.address, invoice.subtotal, invoice.discount, invoice.tax, invoice.total, invoice.notes, invoice.status.value, now.isoformat(), now.isoformat()))
        for item in invoice.items:
            item_id = str(uuid.uuid4())
            cursor.execute('''INSERT INTO invoice_items (id, invoice_id, service_id, service_name, description, quantity, unit_price, tax_rate, amount) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', (item_id, invoice_id, item.service_id, item.service_name, item.description, item.quantity, item.unit_price, item.tax_rate, item.amount))
        conn.commit()
        conn.close()
        invoice.id = invoice_id
        return invoice

    def get_invoice(self, invoice_id: str) -> Optional[Invoice]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''SELECT * FROM invoices WHERE id = ?''', (invoice_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return None
        cursor.execute('''SELECT * FROM invoice_items WHERE invoice_id = ?''', (invoice_id,))
        item_rows = cursor.fetchall()
        conn.close()
        invoice = Invoice(invoice_number=row[1], invoice_date=datetime.fromisoformat(row[2]), due_date=datetime.fromisoformat(row[3]), customer=Customer(name=row[4], email=row[5], phone=row[6], address=row[7]), items=[InvoiceItem(service_id=item[2], service_name=item[3], description=item[4], quantity=item[5], unit_price=item[6], tax_rate=item[7]) for item in item_rows], discount=row[9], notes=row[12], status=InvoiceStatus(row[13]))
        invoice.id = row[0]
        return invoice

    def get_all_invoices(self) -> List[Invoice]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''SELECT id FROM invoices ORDER BY created_at DESC''')
        rows = cursor.fetchall()
        conn.close()
        invoices = []
        for row in rows:
            invoice = self.get_invoice(row[0])
            if invoice:
                invoices.append(invoice)
        return invoices

    def update_invoice(self, invoice_id: str, schema: InvoiceUpdateSchema) -> Optional[Invoice]:
        invoice = self.get_invoice(invoice_id)
        if not invoice:
            return None
        if schema.customer:
            invoice.customer.name = schema.customer.name
            invoice.customer.email = schema.customer.email
            invoice.customer.phone = schema.customer.phone
            invoice.customer.address = schema.customer.address
        if schema.items:
            invoice.items = [InvoiceItem(service_id=item.service_id, service_name=item.service_name, description=item.description, quantity=item.quantity, unit_price=item.unit_price, tax_rate=item.tax_rate) for item in schema.items]
        if schema.discount is not None:
            invoice.discount = schema.discount
        if schema.notes is not None:
            invoice.notes = schema.notes
        if schema.status:
            invoice.status = schema.status
        invoice.calculate_totals()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''UPDATE invoices SET customer_name = ?, customer_email = ?, customer_phone = ?, customer_address = ?, subtotal = ?, discount = ?, tax = ?, total = ?, notes = ?, status = ?, updated_at = ? WHERE id = ?''', (invoice.customer.name, invoice.customer.email, invoice.customer.phone, invoice.customer.address, invoice.subtotal, invoice.discount, invoice.tax, invoice.total, invoice.notes, invoice.status.value, datetime.now().isoformat(), invoice_id))
        cursor.execute('''DELETE FROM invoice_items WHERE invoice_id = ?''', (invoice_id,))
        for item in invoice.items:
            item_id = str(uuid.uuid4())
            cursor.execute('''INSERT INTO invoice_items (id, invoice_id, service_id, service_name, description, quantity, unit_price, tax_rate, amount) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', (item_id, invoice_id, item.service_id, item.service_name, item.description, item.quantity, item.unit_price, item.tax_rate, item.amount))
        conn.commit()
        conn.close()
        return invoice

    def approve_invoice(self, invoice_id: str) -> Optional[Invoice]:
        return self.update_invoice(invoice_id, InvoiceUpdateSchema(status=InvoiceStatus.APPROVED))
