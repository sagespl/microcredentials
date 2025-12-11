import random
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Image, Table

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


def generate_invoice_type_3(filename: str) -> None:
    onepager = bool(random.randint(0, 1))

    invoice = Canvas(filename, FORMAT)
    invoice.setTitle("Invoice_type_D")

    invoice_data = {
        "company": generate_company_data("com"),
        "recipient": generate_company_data("com"),
        "invoice_details": generate_invoice_details(),
    }
    totals = {
        "total_net_amount": 0,
        "total_tax_amount": 0,
    }

    generate_first_page(invoice, invoice_data, totals, onepager)

    if not onepager:
        generate_second_page(invoice, invoice_data, totals)

    invoice.save()


def generate_first_page(invoice: Canvas, invoice_data: dict, totals: dict, onepager: bool) -> None:
    if onepager:
        generate_first_page_for_onepager(invoice, invoice_data, totals)
    else:
        generate_first_page_for_multipager(invoice, invoice_data, totals)

    invoice.showPage()


def generate_first_page_for_onepager(invoice, invoice_data, totals) -> None:
    height_list = [HEIGHT * 0.15, HEIGHT * 0.15, HEIGHT * 0.60, HEIGHT * 0.10]

    main_table = Table(
        [
            [generate_header(height_list[0], invoice_data)],
            [generate_invoice_details_table(height_list[1], invoice_data, 1, 1)],
            [
                generate_line_items_table(
                    height_list[2], 18, invoice_data["invoice_details"], totals
                )
            ],
            [generate_summary(height_list[3], totals, invoice_data["invoice_details"])],
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


def generate_first_page_for_multipager(invoice, invoice_data, totals) -> None:
    height_list = [HEIGHT * 0.15, HEIGHT * 0.15, HEIGHT * 0.70]

    main_table = Table(
        [
            [generate_header(height_list[0], invoice_data)],
            [generate_invoice_details_table(height_list[1], invoice_data, 1, 1)],
            [
                generate_line_items_table(
                    height_list[2], 21, invoice_data["invoice_details"], totals
                )
            ],
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


def generate_second_page(invoice, invoice_data, totals) -> None:
    generate_first_page_for_onepager(invoice, invoice_data, totals)


def generate_header(height: float, invoice_data: dict) -> Table:
    company = invoice_data["company"]
    recipient = invoice_data["recipient"]

    width_list = [WIDTH * 0.2, WIDTH * 0.4, WIDTH * 0.4]

    logo = Image(company.logo_path, width_list[0] * 0.9, height * 0.9, kind="proportional")

    header = Table(
        [
            [
                logo,
                generate_address(company, width_list[1], height / 2),
                generate_recipient_addresses(recipient, width_list[2], height),
            ]
        ],
        colWidths=width_list,
        rowHeights=height,
    )

    header.setStyle(
        [
            # ('GRID', (0, 0), (-1, -1), 0, colors.red),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ("ALIGN", (0, 0), (0, 0), "CENTER"),
            ("VALIGN", (0, 0), (1, 0), "MIDDLE"),
        ]
    )

    return header


def generate_address(company: Company, width: float, height: float) -> Table:
    address = Table(
        [
            [company.name],
            [company.street],
            [company.city],
            [f"Email: {company.email}"],
            [f"Phone: {company.phone}"],
        ],
        colWidths=width,
        rowHeights=height / 5,
    )

    address.setStyle(
        [
            # ('GRID', (0, 0), (-1, -1), 1, colors.green),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ]
    )

    return address


def generate_recipient_addresses(recipient: Company, width: float, height: float) -> Table:
    rows_height = height / 2
    recipient = Table(
        [
            [generate_recipient_address(recipient, width, rows_height, "Legal Invoice Address")],
            [generate_recipient_address(recipient, width, rows_height, "Destination of Goods")],
        ]
    )

    recipient.setStyle(
        [
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
        ]
    )

    return recipient


def generate_recipient_address(
    recipient: Company, width: float, height: float, title: str
) -> Table:
    address = Table(
        [
            [title],
            [recipient.name],
            [recipient.street],
            [recipient.city],
        ],
        colWidths=width,
        rowHeights=height / 4,
    )

    address.setStyle(
        [
            # ('GRID', (0, 0), (-1, -1), 1, colors.green),
            ("BOX", (0, 0), (-1, -1), 1, colors.black),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("FONTNAME", (0, 0), (0, 0), "Helvetica-Bold"),
        ]
    )

    return address


def generate_invoice_details_table(
    height: float, invoice_data: dict, current_page_nr: int, pages_nr: int
) -> Table:
    invoice_details: InvoiceDetails = invoice_data["invoice_details"]
    recipient = invoice_data["recipient"]
    recipient_city = recipient.city.split(",")[0]
    company = invoice_data["company"]

    cell_width = WIDTH / 12
    cell_height = height / 5

    document_type = _generate_document_type(cell_width * 6, cell_height * 2, invoice_details)
    invoice_number = _generate_cell_with_title(
        cell_width * 3, cell_height, "Invoice Nr", invoice_details.invoice_nr
    )
    invoice_date = _generate_cell_with_title(
        cell_width * 3, cell_height, "Date", invoice_details.invoice_date
    )
    page = _generate_cell_with_title(
        cell_width * 3, cell_height, "Pag.", f"{current_page_nr}/{pages_nr}"
    )

    customer_id = _generate_cell_with_title(
        cell_width * 3, cell_height, "Customer Code", invoice_details.customer_id
    )
    vat_code = _generate_cell_with_title(
        cell_width * 3, cell_height, "Tax Code", invoice_details.tax_code
    )

    payment = _generate_cell_with_title(
        cell_width * 6, cell_height, "Payment", "AS AGREED IN SIGNED CONTRACT"
    )
    order_nr = _generate_cell_with_title(
        cell_width * 2, cell_height, "Order Nr.", invoice_details.sales_order_nr
    )
    sales = _generate_cell_with_title(
        cell_width * 2, cell_height, "Sales Representative", "AGENT FOR EXPORT"
    )
    packages_nr = _generate_cell_with_title(
        cell_width * 2, cell_height, "N. Packages", random.randint(10, 50)
    )

    goods_delivered_to = _generate_cell_with_title(
        cell_width * 2, cell_height, "Good Delivered To", recipient_city
    )
    delivered_by = _generate_cell_with_title(cell_width * 3, cell_height, "Delivered By", "TRUCK")
    goods_appearance = _generate_cell_with_title(
        cell_width * 3, cell_height, "Goods Appearance", "Case"
    )
    customer_po_nr = _generate_cell_with_title(
        cell_width * 2, cell_height, "Customer PO Nr.", invoice_details.customer_id
    )
    delivery_nr = _generate_cell_with_title(
        cell_width * 3, cell_height, "Delivery Nr", invoice_details.shipper_list_nr
    )

    bank_account = _generate_cell_with_title(
        cell_width * 9, cell_height, "Bank Account", company.bank_account
    )
    goods_delivered_by = _generate_cell_with_title(
        cell_width * 2, cell_height, "Good Delivered By", company.name
    )

    details = Table(
        [
            [
                document_type,
                "",
                "",
                "",
                "",
                "",
                invoice_number,
                "",
                "",
                invoice_date,
                "",
                page,
            ],
            [
                "",
                "",
                "",
                "",
                "",
                "",
                customer_id,
                "",
                "",
                vat_code,
                "",
                "",
            ],
            [
                payment,
                "",
                "",
                "",
                "",
                order_nr,
                "",
                sales,
                "",
                "",
                packages_nr,
                "",
            ],
            [
                goods_delivered_to,
                "",
                "",
                delivered_by,
                "",
                goods_appearance,
                "",
                "",
                customer_po_nr,
                "",
                delivery_nr,
                "",
            ],
            [
                bank_account,
                "",
                "",
                "",
                "",
                "",
                "",
                goods_delivered_by,
                "",
                "",
                "",
                "",
            ],
        ],
        colWidths=cell_width,
        rowHeights=cell_height,
    )

    details.setStyle(
        [
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ("SPAN", (0, 0), (5, 1)),
            ("SPAN", (6, 0), (8, 0)),
            ("SPAN", (9, 0), (10, 0)),
            ("SPAN", (6, 1), (8, 1)),
            ("SPAN", (9, 1), (11, 1)),
            ("SPAN", (0, 2), (4, 2)),
            ("SPAN", (5, 2), (6, 2)),
            ("SPAN", (7, 2), (9, 2)),
            ("SPAN", (10, 2), (11, 2)),
            ("SPAN", (0, 3), (2, 3)),
            ("SPAN", (3, 3), (4, 3)),
            ("SPAN", (5, 3), (7, 3)),
            ("SPAN", (8, 3), (9, 3)),
            ("SPAN", (10, 3), (11, 3)),
            ("SPAN", (0, 4), (6, 4)),
            ("SPAN", (7, 4), (11, 4)),
        ]
    )

    return details


def _generate_document_type(width: float, height: float, invoice_details: InvoiceDetails) -> Table:
    document_type = Table(
        [
            ["DOCUMENT TYPE"],
            ["INVOICE"],
            [invoice_details.invoice_nr],
        ],
        colWidths=width,
        rowHeights=height / 3,
    )

    document_type.setStyle(
        [
            # ('GRID', (0, 0), (-1, -1), 1, colors.orange),
            ("BOX", (0, 0), (-1, -1), 1, colors.black),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ("VALIGN", (0, 0), (0, 0), "TOP"),
            ("VALIGN", (0, 1), (0, -1), "MIDDLE"),
            ("FONTSIZE", (0, 0), (0, 0), 8),
        ]
    )

    return document_type


def _generate_cell_with_title(width: float, height: float, title: str, value: Any) -> Table:
    cell_table = Table([[title], [value]], colWidths=width, rowHeights=height / 2)

    cell_table.setStyle(
        [
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ("FONTNAME", (0, 0), (0, 0), "Helvetica-Bold"),
        ]
    )

    return cell_table


def generate_line_items_table(
    height: float, item_nr: int, invoice_details: InvoiceDetails, totals: dict
) -> Table:
    items = [
        [
            "Item Code",
            "Item Name",
            "Unit",
            "Quantity",
            "Unit Price",
            "Total Amount",
            "Tax [%]",
        ]
    ]

    for _ in range(item_nr):
        line_item = generate_line_item()
        totals["total_net_amount"] += line_item.net_amount
        totals["total_tax_amount"] += line_item.net_amount * invoice_details.tax_rate / 100

        items.append(
            [
                line_item.item_code,
                line_item.item_name,
                line_item.unit,
                line_item.quantity,
                line_item.unit_price,
                round(line_item.net_amount, 2),
                invoice_details.tax_rate,
            ]
        )

    width_list = [
        WIDTH * 0.1,
        WIDTH * 0.45,
        WIDTH * 0.05,
        WIDTH * 0.1,
        WIDTH * 0.1,
        WIDTH * 0.13,
        WIDTH * 0.07,
    ]
    line_items = Table(items, rowHeights=height / (item_nr + 1), colWidths=width_list)

    line_items.setStyle(
        [
            # ('GRID', (0, 0), (-1, -1), 1, colors.orange),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BOX", (0, 0), (0, -1), 1, colors.black),
            ("BOX", (1, 0), (2, -1), 1, colors.black),
            ("BOX", (2, 0), (2, -1), 1, colors.black),
            ("BOX", (3, 0), (3, -1), 1, colors.black),
            ("BOX", (4, 0), (4, -1), 1, colors.black),
            ("BOX", (5, 0), (5, -1), 1, colors.black),
            ("BOX", (6, 0), (6, -1), 1, colors.black),
        ]
    )

    return line_items


def generate_summary(height: float, totals, invoice_details: InvoiceDetails) -> Table:
    total_net_amount = totals["total_net_amount"]
    total_tax_amount = totals["total_tax_amount"]
    summary = Table(
        [
            ["", "", "", ""],
            ["Goods Value", "Tax Rate [%]", "Tax Amount", "Total Invoice [EUR]"],
            [
                round(total_net_amount, 2),
                invoice_details.tax_rate,
                round(total_tax_amount, 2),
                round(total_net_amount + total_tax_amount, 2),
            ],
        ],
        colWidths=WIDTH / 4,
        rowHeights=height / 3,
    )

    summary.setStyle(
        [
            ("BOX", (0, 1), (-1, -1), 1, colors.black),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ]
    )

    return summary
