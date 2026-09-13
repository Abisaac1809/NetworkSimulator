import pygame


class Button:
    def __init__(self, rect, label, theme, primary=False):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.theme = theme
        self.primary = primary
        self.hovered = False

    def set_label(self, label):
        self.label = label

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(event.pos)
        return False

    def draw(self, surface):
        theme = self.theme
        if self.primary:
            background = theme.text_muted if self.hovered else theme.text_primary
            text_color = theme.text_inverted
        else:
            background = theme.surface_raised if self.hovered else theme.surface
            text_color = theme.text_primary
        pygame.draw.rect(surface, background, self.rect, border_radius=8)
        if not self.primary:
            pygame.draw.rect(surface, theme.border, self.rect, width=1, border_radius=8)
        font = theme.label_font(14, bold=self.primary)
        rendered = font.render(self.label, True, text_color)
        surface.blit(rendered, rendered.get_rect(center=self.rect.center))
