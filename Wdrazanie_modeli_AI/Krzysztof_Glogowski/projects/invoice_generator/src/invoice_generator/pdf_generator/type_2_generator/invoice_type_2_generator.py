import random

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Image, Paragraph, Table

from invoice_generator.data_generator.data_generator import (
    generate_company_data,
    generate_invoice_details,
    generate_line_item,
)
from invoice_generator.model.model import Company, InvoiceDetails

MARGIN = 20
FORMAT = A4
WIDTH = A4[0] - 2 * MARGIN
HEIGHT = A4[1] - 2 * MARGIN
GAP_HEIGHT = 5


def generate_invoice_type_2(filename: str) -> None:
    onepager = bool(random.randint(0, 1))

    invoice = Canvas(filename, FORMAT)
    invoice.setTitle("Invoice_type_C")

    invoice_data = {
        "company": generate_company_data("com"),
        "recipient": generate_company_data("com"),
        "invoice_details": generate_invoice_details(),
    }
    totals = {"product_total": 0}

    generate_first_page(invoice, invoice_data, totals, onepager)

    if not onepager:
        generate_second_page(invoice, invoice_data, totals)

    invoice.save()


def generate_first_page(invoice: Canvas, invoice_data: dict, totals: dict, onepager: bool):
    pages_nr = 1 if onepager else 2
    height_list = [
        HEIGHT * 0.1,
        HEIGHT * 0.025,
        HEIGHT * 0.1,
        HEIGHT * 0.025,
        HEIGHT * 0.65,
        HEIGHT * 0.1,
    ]

    multi_sec = bool(random.randint(0, 1))

    if multi_sec:
        item_nr = 16
    else:
        item_nr = 20

    main_table = Table(
        [
            [generate_header(invoice_data, height_list[0])],
            [generate_title()],
            [generate_bill_to(invoice_data, height_list[2])],
            [generate_contact(invoice_data["company"])],
            [
                generate_line_items_table(
                    height_list[4],
                    item_nr,
                    1,
                    multi_sec,
                    invoice_data["invoice_details"],
                    totals,
                )
            ],
            [generate_footer(height_list[5], invoice_data, 1, pages_nr, onepager, totals)],
        ],
        colWidths=WIDTH,
        rowHeights=height_list,
    )

    main_table.setStyle(
        [
            # ('GRID', (0, 0), (-1, -1), 0, colors.blue),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ("VALIGN", (0, 1), (0, 1), "TOP"),
            ("TOPPADDING", (0, 1), (0, 1), 0),
            ("GRID", (0, 3), (0, 3), 1, colors.black),
            ("VALIGN", (0, 3), (0, 3), 1, "MIDDLE"),
        ]
    )

    main_table.wrapOn(invoice, 0, 0)
    main_table.drawOn(invoice, MARGIN, MARGIN)

    invoice.showPage()


def generate_second_page(invoice: Canvas, invoice_data, totals) -> None:
    pages_nr = 2
    height_list = [
        HEIGHT * 0.1,
        HEIGHT * 0.025,
        HEIGHT * 0.775,
        HEIGHT * 0.1,
    ]

    multi_sec = bool(random.randint(0, 1))

    if multi_sec:
        item_nr = 19
    else:
        item_nr = 23

    main_table = Table(
        [
            [generate_header(invoice_data, height_list[0])],
            [generate_title()],
            [
                generate_line_items_table(
                    height_list[2],
                    item_nr,
                    21,
                    multi_sec,
                    invoice_data["invoice_details"],
                    totals,
                )
            ],
            [generate_footer(height_list[3], invoice_data, pages_nr, pages_nr, True, totals)],
        ],
        colWidths=WIDTH,
        rowHeights=height_list,
    )

    main_table.setStyle(
        [
            # ('GRID', (0, 0), (-1, -1), 0, colors.blue),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ("VALIGN", (0, 1), (0, 1), "TOP"),
            ("TOPPADDING", (0, 1), (0, 1), 0),
        ]
    )

    main_table.wrapOn(invoice, 0, 0)
    main_table.drawOn(invoice, MARGIN, MARGIN)

    invoice.showPage()


def generate_header(invoice_data: dict, height: float) -> Table:
    company: Company = invoice_data["company"]

    width_list = [WIDTH * 0.2, WIDTH * 0.4, WIDTH * 0.4]

    logo = Image(company.logo_path, width_list[0] * 0.9, height * 0.9, kind="proportional")
    name = Paragraph(
        f"<b>{company.name}</b>",
        style=ParagraphStyle(name="company_name", alignment=TA_LEFT, fontSize=22),
    )

    header = Table(
        [[logo, name, generate_address(company, width_list[2], "RIGHT")]],
        colWidths=width_list,
        rowHeights=height,
    )

    header.setStyle(
        [
            # ('GRID', (0, 0), (-1, -1), 0, colors.red),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (0, 0), (0, 0), "CENTER"),
            ("BOTTOMPADDING", (1, 0), (1, 0), 20),
            ("VALIGN", (-1, 0), (-1, 0), "TOP"),
            ("TOPPADDING", (-1, 0), (-1, 0), 0),
        ]
    )

    return header


def generate_title() -> Paragraph:
    title = Paragraph(
        "<b>INVOICE</b>",
        style=ParagraphStyle(name="title", alignment=TA_CENTER, fontSize=15),
    )
    return title


def generate_bill_to(invoice_data: dict, height: float) -> Table:
    recipient = invoice_data["recipient"]
    invoice_details = invoice_data["invoice_details"]

    col_width = WIDTH / 3
    height_list = [height * 0.2, height * 0.8]
    bill_to = Table(
        [
            ["BILL TO", "SHIP TO", "DETAILS"],
            [
                generate_address(recipient, col_width, "LEFT"),
                generate_address(recipient, col_width, "LEFT"),
                generate_details(invoice_details, col_width, height_list[1]),
            ],
        ],
        colWidths=col_width,
        rowHeights=height_list,
    )

    bill_to.setStyle(
        [
            # ('GRID', (0, 0), (-1, -1), 0, colors.red),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ("GRID", (0, 0), (-1, 0), 1, colors.black),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("LEFTPADDING", (0, 0), (-1, 0), 5),
            ("TOPPADDING", (0, 1), (1, 1), 0),
            ("VALIGN", (0, 1), (1, 1), "TOP"),
        ]
    )

    return bill_to


def generate_details(invoice_details: InvoiceDetails, width: float, height: float) -> Table:
    width_list = [width * 0.25, width * 0.75]
    details = Table(
        [
            ["Number", invoice_details.invoice_nr],
            ["Date", invoice_details.invoice_date],
            ["Due Date", invoice_details.due_date],
            ["Currency", "EUR"],
        ],
        colWidths=width_list,
        rowHeights=height / 4,
    )

    details.setStyle(
        [
            # ('GRID', (0, 0), (-1, -1), 0, colors.yellow),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME", (1, 0), (1, 0), "Helvetica-Bold"),
            ("ALIGN", (0, 0), (0, -1), "LEFT"),
            ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ]
    )

    return details


def generate_contact(company: Company) -> Paragraph:
    contact = Paragraph(
        f"<b>AR Contact: {company.contact_person} Phone: {company.phone} Email: {company.email}</b>",
        style=ParagraphStyle(name="contact", alignment=TA_CENTER, fontSize=10),
    )

    return contact


def generate_line_items_table(
    height: float,
    item_nr: int,
    start_idx: int,
    multi_sec: bool,
    invoice_details: InvoiceDetails,
    totals: dict,
) -> Table:
    if multi_sec:
        item_nr_sec_1 = random.randint(3, item_nr - 3)
        item_nr_sec_2 = item_nr - item_nr_sec_1

        height_list = [
            GAP_HEIGHT,
            (height - 2 * GAP_HEIGHT) * item_nr_sec_1 / item_nr,
            GAP_HEIGHT,
            (height - 2 * GAP_HEIGHT) * item_nr_sec_2 / item_nr,
        ]
        items = [
            [""],
            [
                _generate_line_items_section(
                    height_list[1], item_nr_sec_1, start_idx, invoice_details, totals
                )
            ],
            [""],
            [
                _generate_line_items_section(
                    height_list[3],
                    item_nr_sec_2,
                    start_idx + item_nr_sec_1,
                    invoice_details,
                    totals,
                )
            ],
        ]
    else:
        height_list = [GAP_HEIGHT, height - GAP_HEIGHT]
        items = [
            [""],
            [
                _generate_line_items_section(
                    height_list[1], item_nr, start_idx, invoice_details, totals
                )
            ],
        ]

    line_items = Table(items, colWidths=WIDTH, rowHeights=height_list)

    line_items.setStyle(
        [
            # ('GRID', (0, 0), (-1, -1), 0, colors.red),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]
    )

    return line_items


def _generate_line_items_section(
    height: float,
    item_nr: int,
    start_idx: int,
    invoice_details: InvoiceDetails,
    totals: dict,
) -> Table:
    header_height = 30
    height_list = [header_height, GAP_HEIGHT, height - header_height - GAP_HEIGHT]

    section = Table(
        [
            [_generate_section_header(header_height, invoice_details)],
            [""],
            [_generate_line_items(height_list[2], item_nr, start_idx, totals)],
        ],
        colWidths=WIDTH,
        rowHeights=height_list,
    )

    section.setStyle(
        [
            # ('GRID', (0, 0), (-1, -1), 0, colors.darkgreen),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]
    )

    return section


def _generate_section_header(height: float, invoice_details: InvoiceDetails) -> Table:
    section_header = Table(
        [
            [
                "Sales Order No:",
                "DEL Note No:",
                "Delivery Date:",
                "Carrier",
                "Carrier Acc No:",
                "FOB Terms:",
            ],
            [
                invoice_details.sales_order_nr,
                invoice_details.shipper_list_nr,
                invoice_details.delivery_date,
                invoice_details.carrier,
                "",
                "",
            ],
        ],
        colWidths=WIDTH / 6,
        rowHeights=height / 2,
    )

    section_header.setStyle(
        [
            # ('GRID', (0, 0), (-1, -1), 0, colors.brown),
            ("GRID", (0, 0), (-1, 0), 1, colors.black),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ]
    )

    return section_header


def _generate_line_items(height: float, item_nr: int, start_idx: int, totals: dict) -> Table:
    items = [["NO.", "ITEM", "", "Shipped", "UOM", "UNIT PRICE", "EXT PRICE"]]
    for i in range(item_nr):
        line_item = generate_line_item()
        totals["product_total"] += line_item.net_amount
        items.append(
            [
                i + start_idx,
                line_item.item_code,
                line_item.item_name,
                line_item.quantity,
                "EACH",
                line_item.unit_price,
                line_item.net_amount,
            ]
        )

    width_list = [
        WIDTH * 0.05,
        WIDTH * 0.1,
        WIDTH * 0.45,
        WIDTH * 0.08,
        WIDTH * 0.08,
        WIDTH * 0.12,
        WIDTH * 0.12,
    ]
    items_table = Table(items, colWidths=width_list, rowHeights=height / (item_nr + 1))

    items_table.setStyle(
        [
            # ('GRID', (0, 0), (-1, -1), 0, colors.yellow),
            ("GRID", (0, 0), (-1, 0), 1, colors.black),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("SPAN", (1, 0), (2, 0)),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
            ("ALIGN", (3, 0), (-1, 0), "CENTER"),
        ]
    )

    return items_table


def generate_footer(
    height: float,
    invoice_data: dict,
    current_page_nr: int,
    pages_nr: int,
    include_totals: bool,
    totals: dict,
) -> Table:
    col_width = WIDTH / 3

    footer = Table(
        [
            [
                _generate_bank_details(height, col_width, invoice_data["company"]),
                f"{current_page_nr} of {pages_nr}",
                (
                    ""
                    if not include_totals
                    else _generate_totals(
                        height, col_width, invoice_data["invoice_details"], totals
                    )
                ),
            ]
        ],
        rowHeights=height,
        colWidths=col_width,
    )

    footer.setStyle(
        [
            # ('GRID', (0, 0), (-1, -1), 0, colors.red),
            ("LINEABOVE", (0, 0), (-1, 0), 1, colors.black),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ("ALIGN", (1, -1), (1, -1), "CENTER"),
        ]
    )

    return footer


def _generate_bank_details(height: float, width: float, company: Company) -> Table:
    bank_details = Table(
        [
            [""],
            ["BANK DETAILS"],
            [company.name],
            [company.gln],
            [company.bank_account],
        ],
        rowHeights=height / 5,
        colWidths=width,
    )

    bank_details.setStyle(
        [
            # ('GRID', (0, 0), (-1, -1), 0, colors.green),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ]
    )

    return bank_details


def _generate_totals(
    height: float, width: float, invoice_details: InvoiceDetails, totals: dict
) -> Table:
    product_total = totals["product_total"]
    tax_rate: int = invoice_details.tax_rate
    total_tax = product_total * tax_rate / 100
    totals = Table(
        [
            ["Product Total:", f"{product_total: .2f}"],
            ["", ""],
            ["", ""],
            ["Tax Total:", f"{total_tax: .2f}"],
            ["Total (EUR):", f"{product_total + total_tax:.2f}"],
        ],
        colWidths=width / 2,
        rowHeights=height / 5,
    )

    totals.setStyle(
        [
            # ('GRID', (0, 0), (-1, -1), 0, colors.green),
            ("ALIGN", (1, 0), (1, -1), "RIGHT"),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME", (-1, -1), (-1, -1), "Helvetica-Bold"),
        ]
    )

    return totals


def generate_address(company: Company, width: float, alignment: str) -> Table:
    address = Table(
        [
            [company.name],
            [company.street],
            [company.city],
        ],
        colWidths=width,
    )

    address.setStyle(
        [
            # ('GRID', (0, 0), (-1, -1), 1, colors.green),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("ALIGN", (0, 0), (-1, -1), alignment),
        ]
    )

    return address
