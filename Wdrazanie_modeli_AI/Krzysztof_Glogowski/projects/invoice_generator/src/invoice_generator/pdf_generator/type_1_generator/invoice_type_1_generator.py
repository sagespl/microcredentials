import random

from reportlab.graphics.barcode import code128
from reportlab.lib import colors
from reportlab.lib.colors import black
from reportlab.lib.enums import TA_CENTER
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
from invoice_generator.pdf_generator.utils.utils import VerticalParagraph

MARGIN = 20
FORMAT = A4
WIDTH = A4[0] - 2 * MARGIN
HEIGHT = A4[1] - 2 * MARGIN


def generate_invoice_type_1(filename: str) -> None:
    onepager = bool(random.randint(0, 1))

    invoice = Canvas(filename, FORMAT)
    invoice.setTitle("Invoice_type_B")

    invoice_data = {
        "company": generate_company_data("com"),
        "invoice_details": generate_invoice_details(),
    }

    totals = {
        "total_net_weight": 0,
        "total_gross_weight": 0,
        "total_net_amount": 0,
        "total_tax_amount": 0,
    }

    generate_first_page(invoice, invoice_data, totals, onepager)

    if not onepager:
        generate_second_page(invoice, invoice_data, totals)

    invoice.save()


def generate_first_page(
    invoice: Canvas, invoice_data: dict, totals: dict, onepager: bool = True
) -> None:
    if onepager:
        generate_first_page_for_onepager(invoice, invoice_data, totals)
    else:
        generate_first_page_for_multipager(invoice, invoice_data, totals)

    invoice.showPage()


def generate_first_page_for_onepager(invoice: Canvas, invoice_data: dict, totals: dict) -> None:
    height_list = [
        HEIGHT * 0.15,
        HEIGHT * 0.10,
        HEIGHT * 0.58,
        HEIGHT * 0.15,
        HEIGHT * 0.02,
    ]

    main_table = Table(
        [
            [generate_header(invoice_data, height_list[0])],
            [generate_recipient_table(height_list[1])],
            [
                generate_line_items_table(
                    height_list[2], 14, invoice_data["invoice_details"], totals, True
                )
            ],
            [generate_summary(height_list[3], totals, invoice_data)],
            [generate_footer(1, 1)],
        ],
        colWidths=WIDTH,
        rowHeights=height_list,
    )

    main_table.setStyle(
        [
            # ('GRID', (0, 0), (-1, -1), 0, colors.blue),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]
    )

    main_table.wrapOn(invoice, 0, 0)
    main_table.drawOn(invoice, MARGIN, MARGIN)


def generate_first_page_for_multipager(invoice: Canvas, invoice_data: dict, totals: dict) -> None:
    height_list = [HEIGHT * 0.15, HEIGHT * 0.10, HEIGHT * 0.70, HEIGHT * 0.05]

    main_table = Table(
        [
            [generate_header(invoice_data, height_list[0])],
            [generate_recipient_table(height_list[1])],
            [
                generate_line_items_table(
                    height_list[2], 17, invoice_data["invoice_details"], totals, False
                )
            ],
            [generate_footer(1, 2)],
        ],
        colWidths=WIDTH,
        rowHeights=height_list,
    )

    main_table.setStyle(
        [
            # ('GRID', (0, 0), (-1, -1), 0, colors.blue),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]
    )

    main_table.wrapOn(invoice, 0, 0)
    main_table.drawOn(invoice, MARGIN, MARGIN)


def generate_second_page(invoice: Canvas, invoice_data: dict, totals: dict):
    height_list = [HEIGHT * 0.15, HEIGHT * 0.66, HEIGHT * 0.15, HEIGHT * 0.04]

    main_table = Table(
        [
            [generate_header(invoice_data, height_list[0])],
            [
                generate_line_items_table(
                    height_list[1],
                    16,
                    invoice_data["invoice_details"],
                    totals,
                    True,
                    15,
                )
            ],
            [generate_summary(height_list[2], totals, invoice_data)],
            [generate_footer(2, 2)],
        ],
        colWidths=WIDTH,
        rowHeights=height_list,
    )

    main_table.setStyle(
        [
            # ('GRID', (0, 0), (-1, -1), 0, colors.blue),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]
    )

    main_table.wrapOn(invoice, 0, 0)
    main_table.drawOn(invoice, MARGIN, MARGIN)

    invoice.showPage()


def generate_header(invoice_data: dict, height: float) -> Table:
    company: Company = invoice_data["company"]
    invoice_details = invoice_data["invoice_details"]
    header = Table(
        [
            [
                _generate_left_header(WIDTH * 0.5, height, company),
                _generate_right_header(WIDTH * 0.5, height, invoice_details),
            ]
        ],
        colWidths=WIDTH * 0.5,
        rowHeights=height,
    )

    header.setStyle(
        [
            # ('GRID', (0, 0), (-1, -1), 0, colors.red),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]
    )

    return header


def _generate_left_header(width: float, height: float, company: Company) -> Table:
    width_table = [width * 0.35, width * 0.65]

    logo = Image(
        company.logo_path,
        width_table[0] * 0.9,
        height * 5 / 8 * 0.9,
        kind="proportional",
    )

    left_header = Table(
        [
            ["Seller", company.name],
            [logo, company.street],
            ["", company.city],
            ["", company.phone],
            ["", company.email],
            ["", ""],
            [company.bank_account, "(1, 6)"],
        ],
        colWidths=width_table,
        rowHeights=[height / 8] * 6 + [height / 4],
    )

    left_header.setStyle(
        [
            # ('GRID', (0, 0), (-1, -1), 0, colors.yellowgreen),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("FONTNAME", (1, 0), (1, 0), "Helvetica-Bold"),
            ("SPAN", (0, 6), (-1, 6)),
            ("SPAN", (0, 1), (0, 5)),
            ("ALIGN", (0, 1), (0, 5), "CENTER"),
        ]
    )

    return left_header


def _generate_right_header(width: float, height: float, invoice_details: InvoiceDetails) -> Table:
    barcode = code128.Code128(f"{invoice_details.barcode}", barWidth=1, barHeight=height / 3 * 0.8)

    header_right = Table(
        [
            ["", "", "Invoice", ""],
            [
                "Invoice no:",
                invoice_details.invoice_nr.split("/")[-1],
                "Invoice date:",
                invoice_details.invoice_date,
            ],
            ["Bill To:", "Sold To:", "Purchase Order:", ""],
            [
                invoice_details.customer_id,
                invoice_details.customer_id,
                invoice_details.order_nr,
                "",
            ],
            [barcode, "", "ORIGINAL", ""],
            ["", "", "", ""],
        ],
        colWidths=width / 4,
        rowHeights=height / 6,
    )

    header_right.setStyle(
        [
            # ('GRID', (0, 0), (-1, -1), 0, colors.yellowgreen),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("SPAN", (2, 0), (-1, 0)),
            ("ALIGN", (2, 0), (-1, 0), "CENTER"),
            ("FONTNAME", (2, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (2, 0), (-1, 0), 16),
            ("BOTTOMPADDING", (2, 0), (-1, 0), 10),
            ("SPAN", (2, 2), (-1, 2)),
            ("SPAN", (2, 3), (-1, 3)),
            ("SPAN", (2, 4), (-1, 5)),
            ("ALIGN", (2, 4), (-1, 5), "CENTER"),
            ("FONTNAME", (2, 4), (-1, 5), "Helvetica-Bold"),
            ("FONTSIZE", (2, 0), (-1, 0), 14),
            ("SPAN", (0, 4), (1, 5)),
            ("ALIGN", (0, 4), (1, 5), "CENTER"),
            ("ALIGN", (1, 1), (1, 1), "RIGHT"),
            ("ALIGN", (3, 1), (3, 1), "RIGHT"),
            ("ALIGN", (0, 3), (-1, 3), "RIGHT"),
            ("BOTTOMPADDING", (0, 2), (-1, 2), 0),
            ("VALIGN", (0, 2), (-1, 2), "BOTTOM"),
            ("BOX", (0, 1), (1, 1), 0, colors.black),
            ("BOX", (2, 1), (-1, 1), 0, colors.black),
            ("BOX", (0, 2), (0, 3), 0, colors.black),
            ("BOX", (1, 2), (1, 3), 0, colors.black),
            ("BOX", (2, 2), (-1, 3), 0, colors.black),
        ]
    )

    return header_right


def generate_recipient_table(height: float) -> Table:
    bill_sold_to = generate_company_data("com")
    ship_to = generate_company_data("com")

    recipients = Table(
        [
            [
                VerticalParagraph("<u>Bill To</u>"),
                _generate_recipient_data(bill_sold_to),
                VerticalParagraph("<u>Sold To</u>"),
                _generate_recipient_data(bill_sold_to),
                VerticalParagraph("<u>Ship To</u>"),
                _generate_recipient_data(ship_to),
            ]
        ],
        rowHeights=height,
        colWidths=[WIDTH / 24, WIDTH / 24 * 7] * 3,
    )

    recipients.setStyle(
        [
            # ('GRID', (0, 0), (-1, -1), 0, colors.yellowgreen),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]
    )

    return recipients


def _generate_recipient_data(recipient: Company) -> Table:
    recipient = Table([[recipient.name], [recipient.street], [recipient.city], [recipient.gln]])

    return recipient


def generate_line_items_table(
    height: float,
    item_nr: int,
    invoice_details: InvoiceDetails,
    totals: dict,
    with_summary: bool,
    start_idx: int = 1,
) -> Table:
    product_nr = item_nr - 2 if with_summary else item_nr - 1
    height_list = (
        [height / item_nr, height / item_nr * product_nr, height / item_nr]
        if with_summary
        else [height / item_nr, height / item_nr * product_nr]
    )

    items = [
        [_generate_line_items_header(height_list[0], invoice_details)],
        [
            _generate_list_items(
                height_list[1], product_nr, invoice_details.tax_rate, totals, start_idx
            )
        ],
    ]

    if with_summary:
        items.append([_generate_line_items_summary(height_list[2], totals)])

    line_items = Table(items, rowHeights=height_list, colWidths=WIDTH)

    line_items.setStyle(
        [
            # ('GRID', (0, 0), (-1, -1), 0, colors.red),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ]
    )

    return line_items


def _generate_line_items_header(height: float, invoice_details: InvoiceDetails) -> Table:
    line_items_header = Table(
        [
            [
                "Sales order:",
                invoice_details.sales_order_nr,
                f"Rev: {invoice_details.revision}",
                "Shipper list:",
                invoice_details.shipper_list_nr,
                "Ship To:",
                invoice_details.customer_id,
                "Ship date:",
                invoice_details.invoice_date,
                "",
            ],
            [
                "Credit terms:",
                "",
                f"{invoice_details.credit_terms} days",
                "",
                "",
                "Remarks:",
                "N/A",
                "",
                "",
                "",
            ],
        ],
        rowHeights=height / 2,
        colWidths=WIDTH / 10,
    )

    line_items_header.setStyle(
        [
            # ('GRID', (0, 0), (-1, -1), 0, colors.yellowgreen),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BOX", (0, 0), (2, 0), 1, colors.black),
            ("BOX", (3, 0), (-1, 0), 1, colors.black),
            ("BOX", (0, 1), (4, 1), 1, colors.black),
            ("BOX", (5, 1), (-1, 1), 1, colors.black),
            ("ALIGN", (6, 0), (6, 0), "RIGHT"),
        ]
    )

    return line_items_header


def _generate_list_items(
    height: float, items_nr: int, tax_rate: int, totals: dict, start_idx: int
) -> Table:
    items = [
        [
            "No.",
            "Product Code",
            "Net wt",
            "Quantity",
            "Unit Price",
            "Net Amount",
            "Tax rate",
        ],
        ["", "Product name", "Gr wt", "", "", "", "Tax value"],
    ]

    for i in range(items_nr - 2):
        line_item = generate_line_item()
        items.append(
            [
                i + start_idx,
                line_item.item_code,
                line_item.net_weight,
                line_item.quantity,
                line_item.unit_price,
                line_item.net_amount,
                f"{tax_rate}%",
            ]
        )
        items.append(
            [
                "",
                line_item.item_name,
                round(line_item.gross_weight, 2),
                "",
                "",
                "",
                round(line_item.net_amount * tax_rate / 100, 2),
            ]
        )

    for i, item in enumerate(items[2:]):
        if i % 2 == 0:
            totals["total_net_weight"] += item[2]
            totals["total_net_amount"] += item[5]
        else:
            totals["total_gross_weight"] += item[2]
            totals["total_tax_amount"] += item[6]

    width_list = [
        WIDTH * 0.04,
        WIDTH * 0.48,
        WIDTH * 0.06,
        WIDTH * 0.08,
        WIDTH * 0.1,
        WIDTH * 0.12,
        WIDTH * 0.12,
    ]

    list_items = Table(items, rowHeights=height / len(items), colWidths=width_list)

    list_items.setStyle(
        [
            # ('GRID', (0, 0), (-1, -1), 0, colors.yellowgreen),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (2, 0), (-1, 1), "CENTER"),
            ("ALIGN", (0, 0), (0, 0), "LEFT"),
            ("ALIGN", (0, 2), (-1, -1), "RIGHT"),
            ("ALIGN", (1, 1), (1, 1), "RIGHT"),
            ("FONTNAME", (0, 0), (-1, 1), "Helvetica-Bold"),
        ]
    )

    list_items.setStyle(
        [("ALIGN", (1, i), (1, i), "LEFT") for i in range(len(items)) if i % 2 == 0]
    )

    list_items.setStyle(
        [("BOX", (0, i), (-1, i + 1), 1, colors.black) for i in range(len(items)) if i % 2 == 0]
    )

    list_items.setStyle([("BOX", (i, 0), (i, -1), 1, colors.black) for i in range(len(items[0]))])

    return list_items


def _generate_line_items_summary(height: float, totals: dict) -> Table:
    summary = Table(
        [
            [
                "Total net weight [kg]:",
                round(totals["total_net_weight"], 2),
                "Total:",
                round(totals["total_net_amount"], 2),
                round(totals["total_tax_amount"], 2),
            ],
            [
                "Total gross weight [kg]:",
                round(totals["total_gross_weight"], 2),
                "",
                "",
                "",
            ],
        ],
        rowHeights=height / 2,
        colWidths=[
            WIDTH * 0.44,
            WIDTH * 0.06,
            WIDTH * 0.18,
            WIDTH * 0.16,
            WIDTH * 0.16,
        ],
    )

    summary.setStyle(
        [
            # ('GRID', (0, 0), (-1, -1), 0, colors.yellowgreen),
            ("BOX", (0, 0), (-1, -1), 1, colors.black),
            ("BOX", (-1, 0), (-1, -1), 0.5, colors.black),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (1, 0), (1, -1), "RIGHT"),
            ("ALIGN", (3, 0), (-1, 0), "RIGHT"),
            ("ALIGN", (2, 0), (2, 0), "CENTER"),
        ]
    )

    return summary


def generate_summary(height: float, totals: dict, invoice_data: dict) -> Table:
    height_list = [height * 0.1, height * 0.45, height * 0.45]
    width_list = [WIDTH * 0.4, WIDTH * 0.1, WIDTH * 0.1, WIDTH * 0.4]
    summary = Table(
        [
            ["", "", "", ""],
            [
                _generate_summary_totals(totals, invoice_data["invoice_details"].tax_rate),
                "",
                "",
                _generate_summary_to_pay(totals),
            ],
            [
                _generate_summary_signatures(),
                "",
                _generate_summary_contact(invoice_data["company"]),
                "",
            ],
        ],
        colWidths=width_list,
        rowHeights=height_list,
    )

    summary.setStyle(
        [
            # ('GRID', (0, 0), (-1, -1), 0, colors.yellowgreen),
            ("SPAN", (0, 1), (2, 1)),
            ("SPAN", (2, -1), (-1, -1)),
            ("VALIGN", (2, -1), (-1, -1), "MIDDLE"),
            ("GRID", (2, -1), (-1, -1), 1, black),
            ("VALIGN", (0, 1), (0, -1), "MIDDLE"),
            ("VALIGN", (-1, 1), (-1, 1), "MIDDLE"),
            ("ALIGN", (-1, 1), (-1, 1), "RIGHT"),
            ("RIGHTPADDING", (-1, 1), (-1, 1), 0),
        ]
    )

    return summary


def _generate_summary_totals(totals: dict, tax_rate: int) -> Table:
    total_net_amount = totals["total_net_amount"]
    total_tax_amount = totals["total_tax_amount"]
    summary_totals = Table(
        [
            ["TAX BASE", "TAX RATE", "TAX AMOUNT", "GROSS AMOUNT"],
            [
                round(total_net_amount, 2),
                tax_rate,
                round(total_tax_amount, 2),
                round(total_net_amount + total_tax_amount, 2),
            ],
        ]
    )

    summary_totals.setStyle(
        [
            ("GRID", (0, 0), (-1, -1), 1, black),
            ("ALIGN", (0, -1), (-1, -1), "RIGHT"),
        ]
    )

    return summary_totals


def _generate_summary_to_pay(totals: dict) -> Table:
    total_net_amount = totals["total_net_amount"]
    total_tax_amount = totals["total_tax_amount"]
    gross_amount = round(total_net_amount + total_tax_amount, 2)
    to_pay = Table(
        [
            ["Gross Amount", "", f"{gross_amount} EUR"],
            ["To pay", "", f"{gross_amount} EUR"],
        ]
    )

    to_pay.setStyle(
        [
            ("BOX", (0, 0), (-1, 0), 1, black),
            ("BOX", (0, -1), (-1, -1), 1, black),
            ("ALIGN", (0, 0), (0, -1), "LEFT"),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("ALIGN", (-1, 0), (-1, -1), "RIGHT"),
        ]
    )

    return to_pay


def _generate_summary_signatures() -> Table:
    signatures = Table([["Authorized signature:", "Received, date"], ["", ""]])

    signatures.setStyle(
        [
            ("GRID", (0, 0), (-1, -1), 1, black),
        ]
    )

    return signatures


def _generate_summary_contact(company: Company) -> Paragraph:
    contact_style = ParagraphStyle(name="footer", alignment=TA_CENTER)
    contact = Paragraph(
        f"<b>Are you interested in an e-invoice? Contact us:\n{company.email}</b>",
        contact_style,
    )
    return contact


def generate_footer(current_page: int, pages_nr: int) -> Paragraph:
    footer_style = ParagraphStyle(name="footer", alignment=TA_CENTER)
    footer = Paragraph(f"Page {current_page} of {pages_nr}", footer_style)
    return footer
