import pygame

from ui.components.panel import Panel


class Dashboard:
    def __init__(self, rect, theme):
        self.theme = theme
        self.panel = Panel(rect, theme, title="Métricas en vivo")
        self.rect = self.panel.rect

    def draw(self, surface, metrics):
        self.panel.draw(surface)
        theme = self.theme
        rows = [
            ("Tiempo", f"{metrics['sim_time']:.1f} s"),
            ("Llegada  lambda", f"{metrics['arrival_rate']:.1f}"),
            ("Servicio  mu", f"{metrics['service_rate']:.1f}"),
            ("Tráfico  rho", f"{metrics['rho']:.2f}"),
            ("En sistema  L", f"{metrics['l']:.2f}"),
            ("En cola  Lq", f"{metrics['lq']:.2f}"),
            ("Espera  Wq", f"{metrics['wq']:.3f} s"),
            ("Estancia  W", f"{metrics['w']:.3f} s"),
            ("Procesados", f"{metrics['packets_processed']}"),
            ("Perdidos", f"{metrics['packets_lost']}"),
            ("Pérdida", f"{metrics['loss_rate']:.2f} %"),
            ("Costo global", f"${metrics['total_cost']:.2f}"),
        ]
        label_font = theme.label_font(14)
        value_font = theme.mono_font(15)
        y = self.panel.content_top()
        for label, value in rows:
            label_surface = label_font.render(label, True, theme.text_muted)
            value_surface = value_font.render(value, True, theme.text_primary)
            surface.blit(label_surface, (self.rect.x + 18, y))
            surface.blit(value_surface, value_surface.get_rect(topright=(self.rect.right - 18, y - 1)))
            y += 26
