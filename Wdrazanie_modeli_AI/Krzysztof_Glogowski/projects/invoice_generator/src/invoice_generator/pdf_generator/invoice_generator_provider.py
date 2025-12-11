from typing import Callable

from invoice_generator.pdf_generator.type_0_generator.invoice_typ_0_generator import (
    generate_invoice_type_0,
)
from invoice_generator.pdf_generator.type_1_generator.invoice_type_1_generator import (
    generate_invoice_type_1,
)
from invoice_generator.pdf_generator.type_2_generator.invoice_type_2_generator import (
    generate_invoice_type_2,
)
from invoice_generator.pdf_generator.type_3_generator.invoice_type_3_generator import (
    generate_invoice_type_3,
)

_LABEL_TO_GENERATOR_DICT = {
    0: generate_invoice_type_0,
    1: generate_invoice_type_1,
    2: generate_invoice_type_2,
    3: generate_invoice_type_3,
}


def provide_pdf_generator(label: int) -> Callable[[str], None]:
    generator = _LABEL_TO_GENERATOR_DICT.get(label)

    if generator is None:
        raise ValueError(
            f"Unsupported label: {label}. Supported labels are {list(_LABEL_TO_GENERATOR_DICT.keys())}."
        )

    return generator
