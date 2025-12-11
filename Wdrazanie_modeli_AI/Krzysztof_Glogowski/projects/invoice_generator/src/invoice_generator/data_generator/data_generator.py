import os
import random
import re
from datetime import date, timedelta

import pandas as pd
from faker import Faker

from invoice_generator.model.model import Company, InvoiceDetails, LineItem

Faker.seed(41)
fake = Faker()

products = pd.read_csv("invoice_generator/resources/product/products.csv", encoding="utf-8")


def generate_invoice_details() -> InvoiceDetails:
    credit_terms = 14
    return InvoiceDetails(
        invoice_nr=generate_invoice_number(),
        revision=random.randint(0, 9),
        customer_id=generate_alphanumeric(9),
        invoice_date=date.today(),
        credit_terms=credit_terms,
        due_date=date.today() + timedelta(credit_terms),
        order_nr=generate_alphanumeric(12),
        sales_order_nr=generate_alphanumeric(7),
        shipper_list_nr=generate_alphanumeric(8),
        tax_rate=random.randint(0, 13),
        tax_code=generate_alphanumeric(11).upper(),
        barcode=random.randint(1_000_000_000, 9_999_999_999),
        delivery_date=date.today(),
        carrier=fake.company(),
    )


def generate_company_data(locale: str) -> Company:
    name = fake.company()
    name_without_whitespaces = re.sub(r"\s+", "", name).replace(",", ".").lower()
    street, city = fake.address().split("\n")
    return Company(
        name=name,
        street=street,
        city=city,
        phone=fake.phone_number(),
        email=f"contact@{name_without_whitespaces}.{locale.lower()}",
        motto=fake.catch_phrase(),
        contact_person=f"{fake.name()} {fake.last_name()}",
        logo_path=os.path.abspath(
            f"invoice_generator/resources/logo/logo_{random.randint(1, 12)}.png"
        ),
        bank_account=generate_bank_account(),
        gln=f"GLN {generate_alphanumeric(13)}",
    )


def generate_line_item() -> LineItem:
    product = products.sample(1).iloc[0]
    quantity = random.randint(1, 100)
    unit_price = round(product.unit_price, 2)
    net_amount = round(quantity * unit_price, 2)
    net_weight = random.randint(1, 5) - random.randint(0, 1) * 0.5
    return LineItem(
        item_code=product.product_id,
        item_name=product.product_name,
        quantity=quantity,
        unit=product.unit,
        unit_price=unit_price,
        net_amount=net_amount,
        net_weight=net_weight,
        gross_weight=net_weight + round(random.uniform(0.1, 0.509), 2),
    )


def generate_invoice_number() -> str:
    return f"INV/{date.today().strftime('%d-%m-%Y')}/{generate_alphanumeric(6)}"


def generate_alphanumeric(length: int) -> str:
    return fake.password(
        length=length,
        special_chars=False,
        digits=True,
        upper_case=True,
        lower_case=False,
    )


def generate_bank_account() -> str:
    bank_account_parts = [random.randint(10, 99)]
    for i in range(6):
        bank_account_parts.append(random.randint(1000, 9999))

    return f"XX{bank_account_parts[0]} {bank_account_parts[1]} {bank_account_parts[2]} {bank_account_parts[3]} {bank_account_parts[4]} {bank_account_parts[5]} {bank_account_parts[6]}"
