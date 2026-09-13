import pygame

from ui.components.panel import Panel


class Legend:
    def __init__(self, rect, theme):
        self.theme = theme
        self.panel = Panel(rect, theme, title="Saturación de buffer")
        self.rect = self.panel.rect

    def draw(self, surface):
        self.panel.draw(surface)
        theme = self.theme
        entries = [
            (theme.saturation_low, "< 50%  estable"),
            (theme.saturation_medium, "50 – 80%  presión"),
            (theme.saturation_high, "> 80%  riesgo de descarte"),
        ]
        font = theme.label_font(13)
        y = self.panel.content_top()
        for color, text in entries:
            pygame.draw.circle(surface, color, (self.rect.x + 26, y + 8), 7)
            label = font.render(text, True, theme.text_primary)
            surface.blit(label, (self.rect.x + 44, y))
            y += 30
