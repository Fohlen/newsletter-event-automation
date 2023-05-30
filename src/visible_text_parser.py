from html.parser import HTMLParser


# Custom HTML parser class
class VisibleTextParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.visible_text = []

    def handle_data(self, data):
        self.visible_text.append(data.strip())

    def handle_entityref(self, name):
        self.visible_text.append(f"&{name};")

    def handle_charref(self, name):
        self.visible_text.append(f"&#{name};")

    def get_visible_text(self):
        return ' '.join(self.visible_text)
