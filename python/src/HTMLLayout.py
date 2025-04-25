import tkinter
from src.HTMLParser import Element
from src.CSS.CSSParser import CSSParser
import logging
from src.CSS import CSSConstants
logger = logging.getLogger(__name__)

# """Populates the given display list with the commands needed to style the HTMLElement tree according to the CSS rules"""
# def paint_tree(layout_object, display_list):
#     display_list.extend(layout_object.paint())

#     for child in layout_object.children:
#         paint_tree(child, display_list)


def style(node, rules):

    for property, default_value in CSSConstants.INHERITED_PROPERTIES.items():
        if node.parent:
            node.style[property] = node.parent.style[property]
        else:
            node.style[property] = default_value

    for selector, body in rules:
        if not selector.matches(node): continue
        for property, value in body.items():
            node.style[property] = value
    #style attributes should override stylesheets apparently
    if isinstance(node, Element) and "style" in node.attributes:
        parser = CSSParser()
        pairs = parser.parseStyleBody(node.attributes["style"])
        for property, value in pairs.items():
            node.style[property] = value

    if node.style["font-size"].endswith("%"):
        if node.parent:
            parent_font_size = node.parent.style["font-size"]
        else:
            parent_font_size = CSSConstants.INHERITED_PROPERTIES["font-size"]
        node_pct = float(node.style["font-size"][:-1]) / 100
        parent_px = float(parent_font_size[:-2])
        node.style["font-size"] = str(node_pct * parent_px) + "px"

    for child in node.children:
        style(child, rules)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    window = tkinter.Tk()
    #TODO: implement stup

