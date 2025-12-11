from dataclasses import dataclass
from datetime import date


@dataclass
class Company:
    name: str
    street: str
    city: str
    phone: str
    email: str
    motto: str | None
    contact_person: str
    logo_path: str
    bank_account: str
    gln: str


@dataclass
class InvoiceDetails:
    invoice_nr: str
    revision: int
    customer_id: str
    invoice_date: date
    credit_terms: int
    due_date: date
    order_nr: str
    sales_order_nr: str
    shipper_list_nr: str
    tax_rate: int
    tax_code: str
    barcode: int
    delivery_date: date
    carrier: str


@dataclass
class LineItem:
    item_code: str
    item_name: str
    quantity: int
    unit: str
    unit_price: float
    net_amount: float
    net_weight: float
    gross_weight: float
