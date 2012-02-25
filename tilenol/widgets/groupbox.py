from collections import namedtuple

from cairo import SolidPattern, ScaledFont
from zorro.di import dependency, has_dependencies

from tilenol.groups import GroupManager
from . import Widget


Padding = namedtuple('Padding', 'top right bottom left')


@has_dependencies
class Groupbox(Widget):

    gman = dependency(GroupManager, 'group-manager')


    def __init__(self, *,
            font_face="Consolas",
            font_size=18,
            inactive_color=SolidPattern(0.5, 0.5, 0.5),
            active_color=SolidPattern(1, 1, 1),
            padding=Padding(2, 2, 2, 2)):
        self.font_face = font_face
        self.font_size = font_size
        self.inactive_color = inactive_color
        self.active_color = active_color
        self.padding = padding


    def draw(self, canvas):
        canvas.select_font_face(self.font_face)
        canvas.set_font_size(self.font_size)
        x = self.padding.left
        between = self.padding.right + self.padding.left
        for g in self.gman.groups:
            canvas.set_source(self.active_color)
            canvas.move_to(x, self.padding.top)
            canvas.show_text(g)
            ext = canvas.text_extents(g)
            x += ext.width + between

    def size(self, canvas):
        canvas.select_font_face(self.font_face)
        canvas.set_font_size(self.font_size)
        width = 0
        height = 0
        for g in self.gman.groups:
            ext = canvas.text_extents()
            width += ext.width
            height = max(ext.height + self.padding.top + self.padding.bottom)
            width += self.padding.left + self.padding.right
        return width, height
