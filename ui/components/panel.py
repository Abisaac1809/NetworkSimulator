import pygame


class Panel:
    def __init__(self, rect, theme, title=None):
        self.rect = pygame.Rect(rect)
        self.theme = theme
        self.title = title

    def content_top(self):
        return self.rect.y + (48 if self.title else 18)

    def draw(self, surface):
        pygame.draw.rect(surface, self.theme.surface, self.rect, border_radius=14)
        pygame.draw.rect(surface, self.theme.border, self.rect, width=1, border_radius=14)
        if self.title:
            font = self.theme.label_font(12, bold=True)
            label = font.render(self.title.upper(), True, self.theme.text_muted)
            surface.blit(label, (self.rect.x + 18, self.rect.y + 18))
