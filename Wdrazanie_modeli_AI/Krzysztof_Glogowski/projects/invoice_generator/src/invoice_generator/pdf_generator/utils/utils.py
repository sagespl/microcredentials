from reportlab.platypus import Paragraph


class VerticalParagraph(Paragraph):
    """Paragraph that is printed vertically (rotated 90 degrees counterclockwise"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.horizontal_position = -self.style.leading

    def draw(self):
        """Draw text"""
        canvas = self.canv
        canvas.rotate(90)
        canvas.translate(1, self.horizontal_position)
        super().draw()

    def wrap(self, available_width, _):
        """Wrap text in table"""
        string_width = self.canv.stringWidth(
            self.getPlainText(), self.style.fontName, self.style.fontSize
        )
        self.horizontal_position = -(available_width + self.style.leading) / 2
        height, _ = super().wrap(availWidth=1 + string_width, availHeight=available_width)
        return self.style.leading, height
