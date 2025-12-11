import random

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph, Table

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


def generate_invoice_type_0(filename: str) -> None:
    onepager = bool(random.randint(0, 1))

    invoice = Canvas(filename, FORMAT)
    invoice.setTitle("Invoice_type_A")

    invoice_data = {
        "company": generate_company_data("com"),
        "invoice_details": generate_invoice_details(),
    }

    subtotal_fp, taxable_fp = generate_first_page(invoice, invoice_data, onepager)

    if not onepager:
        generate_second_page(invoice, invoice_data, subtotal_fp, taxable_fp)

    invoice.save()


def generate_first_page(
    invoice: Canvas, invoice_data: dict, onepager: bool = True
) -> tuple[float, float]:
    subtotal, taxable = 0.0, 0.0
    if onepager:
        generate_first_page_for_onepager(invoice, invoice_data)
    else:
        subtotal, taxable = generate_first_page_for_multipager(invoice, invoice_data)

    invoice.showPage()

    return subtotal, taxable


def generate_first_page_for_onepager(invoice: Canvas, invoice_data: dict) -> None:
    height_list = [
        HEIGHT * 0.15,
        HEIGHT * 0.10,
        HEIGHT * 0.5,
        HEIGHT * 0.15,
        HEIGHT * 0.10,
    ]

    line_items_table, subtotal, taxable = generate_line_items_table(height_list[2], 18)

    main_table = Table(
        [
            [generate_header(invoice_data, height_list[0])],
            [generate_bill_to(height_list[1])],
            [line_items_table],
            [generate_summary(height_list[3], subtotal, taxable)],
            [generate_footer(invoice_data)],
        ],
        colWidths=WIDTH,
        rowHeights=height_list,
    )

    main_table.setStyle(
        [
            # ('GRID', (0, 0), (-1, -1), 0, colors.black),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]
    )

    main_table.wrapOn(invoice, 0, 0)
    main_table.drawOn(invoice, MARGIN, MARGIN)


def generate_first_page_for_multipager(invoice: Canvas, invoice_data: dict) -> tuple[float, float]:
    height_list = [HEIGHT * 0.15, HEIGHT * 0.10, HEIGHT * 0.65, HEIGHT * 0.10]

    line_items_table, subtotal, taxable = generate_line_items_table(height_list[2], 24)

    main_table = Table(
        [
            [generate_header(invoice_data, height_list[0])],
            [generate_bill_to(height_list[1])],
            [line_items_table],
            [generate_footer(invoice_data)],
        ],
        colWidths=WIDTH,
        rowHeights=height_list,
    )

    main_table.setStyle(
        [
            # ('GRID', (0, 0), (-1, -1), 0, colors.black),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]
    )

    main_table.wrapOn(invoice, 0, 0)
    main_table.drawOn(invoice, MARGIN, MARGIN)

    return subtotal, taxable


def generate_second_page(
    invoice: Canvas, invoice_data: dict, subtotal_fp: float, taxable_fp: float
):
    height_list = [HEIGHT * 0.15, HEIGHT * 0.6, HEIGHT * 0.15, HEIGHT * 0.10]

    line_items_table, subtotal_sp, taxable_sp = generate_line_items_table(height_list[1], 24)

    main_table = Table(
        [
            [generate_header(invoice_data, height_list[0])],
            [line_items_table],
            [generate_summary(height_list[2], subtotal_fp + subtotal_sp, taxable_fp + taxable_sp)],
            [generate_footer(invoice_data)],
        ],
        colWidths=WIDTH,
        rowHeights=height_list,
    )

    main_table.setStyle(
        [
            # ('GRID', (0, 0), (-1, -1), 0, colors.black),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]
    )

    main_table.wrapOn(invoice, 0, 0)
    main_table.drawOn(invoice, MARGIN, MARGIN)

    invoice.showPage()


def generate_header(invoice_data: dict, height: float) -> Table:
    company: Company = invoice_data["company"]
    invoice_details: InvoiceDetails = invoice_data["invoice_details"]
    header = Table(
        [
            [company.name, "", "INVOICE"],
            [company.motto, "", ""],
            [company.street, "DATE", invoice_details.invoice_date],
            [company.city, "INVOICE #", invoice_details.invoice_nr],
            [f"Phone {company.phone}", "CUSTOMER_ID", invoice_details.customer_id],
            [f"Email: {company.email}", "DUE DATE", invoice_details.due_date],
        ],
        colWidths=[WIDTH * 0.62, WIDTH * 0.15, WIDTH * 0.23],
        rowHeights=[
            height / 7 * 2,
            height / 7,
            height / 7,
            height / 7,
            height / 7,
            height / 7,
        ],
    )

    header.setStyle(
        [
            # ('GRID', (0, 0), (-1, -1), 0, colors.red),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (2, 2), (2, -1), "RIGHT"),
            ("FONTNAME", (0, 0), (2, 0), "Helvetica-Bold"),
            ("ALIGN", (0, 0), (2, 1), "CENTER"),
            ("FONTSIZE", (0, 0), (0, 0), 20),
            # ('TEXTCOLOR', (0, 0), (0, 0), colors.blue),
            ("BOTTOMPADDING", (0, 0), (0, 0), 15),
            ("FONTSIZE", (2, 0), (2, 0), 16),
            ("BOTTOMPADDING", (2, 0), (2, 0), 10),
        ]
    )

    return header


def generate_bill_to(height: float) -> Table:
    company = generate_company_data("pl")
    bill_to = Table(
        [
            [""],
            ["BILL TO", ""],
            [company.name, ""],
            [company.street, ""],
            [company.city, ""],
            [company.phone, ""],
        ],
        colWidths=[WIDTH * 0.3, WIDTH * 0.7],
        rowHeights=height / 6,
    )

    bill_to.setStyle(
        [
            # ('GRID', (0, 0), (-1, -1), 0, colors.blue),
            ("GRID", (0, 1), (0, 1), 0, colors.black),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
        ]
    )

    return bill_to


def generate_line_items_table(height, item_nr: int) -> tuple[Table, float, float]:
    items = [_generate_single_list_item() for _ in range(item_nr)]

    subtotal, taxable = _calculate_subtotal_and_taxable(items)

    items.insert(0, ["DESCRIPTION", "TAXED", "AMOUNT"])
    items.insert(0, ["", "", ""])

    line_items = Table(
        items,
        colWidths=[WIDTH * 0.7, WIDTH * 0.1, WIDTH * 0.2],
        rowHeights=height // (item_nr + 2),
    )

    line_items.setStyle(
        [
            ("GRID", (0, 1), (-1, -1), 0, colors.black),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (0, 0), (-1, 1), "CENTER"),
            ("ALIGN", (1, 0), (1, -1), "CENTER"),
            ("ALIGN", (2, 2), (2, -1), "RIGHT"),
            ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
        ]
    )

    return line_items, subtotal, taxable


def _generate_single_list_item() -> list[str]:
    line_item = generate_line_item()
    return [
        line_item.item_name,
        "X" if bool(random.randint(0, 1)) else "",
        f"{line_item.quantity * line_item.net_amount: .2f}",
    ]


def _calculate_subtotal_and_taxable(list_items: list[list[str]]) -> tuple[float, float]:
    subtotal, taxable = 0.0, 0.0
    for list_item in list_items:
        amount = float(list_item[2])
        taxed = bool(list_item[1] == "X")
        subtotal += amount
        if taxed:
            taxable += amount

    return subtotal, taxable


def generate_summary(height: float, subtotal: float, taxable: float) -> Table:
    summary = Table(
        [
            [
                _generate_other_comments(WIDTH * 0.7),
                _generate_summary_table(subtotal, taxable),
            ],
        ],
        colWidths=[WIDTH * 0.7, WIDTH * 0.3],
        rowHeights=height,
    )

    summary.setStyle(
        [
            # ('GRID', (0, 0), (-1, -1), 0, colors.red),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ]
    )

    return summary


def _generate_other_comments(width) -> Table:
    other_comments = Table(
        [
            ["OTHER COMMENTS"],
            ["1. Total payment due in 30 days"],
            ["2. Please include the invoice number on your check"],
            [""],
            [""],
        ],
        colWidths=width,
    )

    other_comments.setStyle(
        [
            ("BOX", (0, 0), (-1, -1), 0, colors.black),
            ("GRID", (0, 0), (0, 0), 0, colors.black),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ]
    )

    return other_comments


def _generate_summary_table(subtotal: float, taxable: float) -> Table:
    tax_rate = random.randint(5, 12)
    tax_due = taxable * tax_rate / 100
    total = subtotal + tax_due

    summary_table = Table(
        [
            ["Subtotal", "", f"{subtotal: .2f}"],
            ["Taxable", "", f"{taxable: .2f}"],
            ["Tax rate", "", f"{tax_rate: .2f}%"],
            ["Tax due", "", f"{tax_due: .2f}"],
            ["Other", "", "-"],
            ["TOTAL", "$", f"{total: .2f}"],
        ]
    )

    summary_table.setStyle(
        [
            # ('GRID', (0, 0), (-1, -1), 0, colors.black),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (2, 0), (2, -1), "RIGHT"),
            ("LINEBELOW", (0, 4), (-1, 4), 1, colors.black),
        ]
    )

    return summary_table


def generate_footer(footer_and_header_data: dict) -> list[Paragraph]:
    company = footer_and_header_data["company"]

    footer_paragraph_1_style = ParagraphStyle(name="footer_paragraph_1", alignment=TA_CENTER)
    footer_paragraph_1 = Paragraph(
        """
    If you have any questions about this invoice, please contact
    """,
        footer_paragraph_1_style,
    )

    footer_paragraph_2_style = ParagraphStyle(name="footer_paragraph_2", alignment=TA_CENTER)
    footer_paragraph_2 = Paragraph(
        f"""
        {company.contact_person}, ☎ {company.phone},  ✉ {company.email}
        """,
        footer_paragraph_2_style,
    )

    footer_paragraph_3_style = ParagraphStyle(name="footer_paragraph_3", alignment=TA_CENTER)
    footer_paragraph_3 = Paragraph(
        """
        <b>
        Thank You For Your Business!
        </b>
        """,
        footer_paragraph_3_style,
    )

    return [footer_paragraph_1, footer_paragraph_2, footer_paragraph_3]
