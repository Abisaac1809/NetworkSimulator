import threading

import pygame

from domain.network_simulation import NetworkSimulation
from ui.styles.theme import Theme
from ui.components.button import Button
from ui.components.panel import Panel
from ui.components.dashboard import Dashboard
from ui.components.legend import Legend
from ui.components.network_canvas import NetworkCanvas


class App:
    def __init__(self, config, queue_solver, inventory_solver, transport_solver, report_service):
        self.config = config
        self.report_service = report_service
        self.simulation = NetworkSimulation(config, queue_solver, inventory_solver, transport_solver)

        self.is_running = True
        self.export_in_progress = False
        self.export_status = "Presioná E para exportar el reporte"

        self.screen = None
        self.clock = None
        self.theme = None
        self.canvas = None
        self.dashboard = None
        self.legend = None
        self.controls_panel = None
        self.buttons = {}

    def run(self):
        pygame.init()
        pygame.display.set_caption("Simulador Dinámico de Redes · UJAP")
        self.screen = pygame.display.set_mode((self.config.screen_width, self.config.screen_height))
        self.clock = pygame.time.Clock()
        self.theme = Theme()
        self._build_layout()

        while self.is_running:
            delta_seconds = self.clock.tick(self.config.frames_per_second) / 1000.0
            self._handle_events()
            self.simulation.step(min(0.05, delta_seconds))
            self._draw()
            pygame.display.flip()

        pygame.quit()

    def _build_layout(self):
        width = self.config.screen_width
        height = self.config.screen_height
        sidebar_x = 1024
        sidebar_width = width - sidebar_x - 24

        self.canvas = NetworkCanvas((24, 80, sidebar_x - 48, height - 138), self.theme)
        self.dashboard = Dashboard((sidebar_x, 80, sidebar_width, 372), self.theme)
        self.controls_panel = Panel((sidebar_x, 464, sidebar_width, 176), self.theme, title="Controles")
        self.legend = Legend((sidebar_x, 652, sidebar_width, height - 652 - 34), self.theme)

        self.buttons = {
            "arrival_down": Button((sidebar_x + 18, 522, 130, 34), "λ  −", self.theme),
            "arrival_up": Button((sidebar_x + 156, 522, 130, 34), "λ  +", self.theme),
            "pause": Button((sidebar_x + 18, 564, 130, 34), "Pausar", self.theme),
            "export": Button((sidebar_x + 156, 564, 130, 34), "Exportar", self.theme, primary=True),
        }

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
            elif event.type == pygame.KEYDOWN:
                self._handle_key(event.key)
            self._handle_buttons(event)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._handle_canvas_click(event.pos)

    def _handle_key(self, key):
        if key == pygame.K_ESCAPE:
            self.is_running = False
        elif key == pygame.K_SPACE:
            self.simulation.toggle_pause()
        elif key == pygame.K_LEFT:
            self.simulation.adjust_arrival_rate(-self.config.arrival_rate_step)
        elif key == pygame.K_RIGHT:
            self.simulation.adjust_arrival_rate(self.config.arrival_rate_step)
        elif key == pygame.K_e:
            self._trigger_export()

    def _handle_buttons(self, event):
        if self.buttons["arrival_down"].handle_event(event):
            self.simulation.adjust_arrival_rate(-self.config.arrival_rate_step)
        if self.buttons["arrival_up"].handle_event(event):
            self.simulation.adjust_arrival_rate(self.config.arrival_rate_step)
        if self.buttons["pause"].handle_event(event):
            self.simulation.toggle_pause()
        if self.buttons["export"].handle_event(event):
            self._trigger_export()

    def _handle_canvas_click(self, position):
        for button in self.buttons.values():
            if button.rect.collidepoint(position):
                return
        link_id = self.canvas.link_at(self.simulation, position)
        if link_id:
            self.simulation.toggle_link(link_id)

    def _trigger_export(self):
        if self.export_in_progress:
            return
        self.export_in_progress = True
        self.export_status = "Generando reporte..."
        metrics = self.simulation.metrics_summary()
        thread = threading.Thread(target=self._run_export, args=(metrics,), daemon=True)
        thread.start()

    def _run_export(self, metrics):
        try:
            self.report_service.export(metrics)
            self.export_status = "Reporte guardado en reporte_simulacion.txt"
        except Exception as error:
            self.export_status = f"Error al exportar: {error}"
        finally:
            self.export_in_progress = False

    def _draw(self):
        self.screen.fill(self.theme.background)
        self._draw_top_bar()
        self.canvas.draw(self.screen, self.simulation)
        self.dashboard.draw(self.screen, self.simulation.metrics_summary())
        self._draw_controls()
        self.legend.draw(self.screen)
        self._draw_bottom_bar()

    def _draw_top_bar(self):
        theme = self.theme
        title_font = theme.label_font(22, bold=True)
        title = title_font.render("Simulador Dinámico de Redes", True, theme.text_primary)
        self.screen.blit(title, (24, 26))

        is_paused = self.simulation.is_paused
        status_text = "EN PAUSA" if is_paused else "EN EJECUCIÓN"
        status_color = theme.saturation_medium if is_paused else theme.saturation_low
        status_font = theme.label_font(13, bold=True)
        status = status_font.render(status_text, True, theme.text_inverted)
        pill = pygame.Rect(0, 0, status.get_width() + 28, 30)
        pill.topright = (self.config.screen_width - 24, 24)
        pygame.draw.rect(self.screen, status_color, pill, border_radius=15)
        self.screen.blit(status, status.get_rect(center=pill.center))

    def _draw_controls(self):
        self.controls_panel.draw(self.screen)
        theme = self.theme
        caption_font = theme.label_font(12)
        caption = caption_font.render(
            "Ajustá λ, pausá o exportá el reporte.",
            True, theme.text_muted)
        self.screen.blit(caption, (self.controls_panel.rect.x + 18, self.controls_panel.rect.y + 44))

        self.buttons["pause"].set_label("Reanudar" if self.simulation.is_paused else "Pausar")
        for button in self.buttons.values():
            button.draw(self.screen)

    def _draw_bottom_bar(self):
        theme = self.theme
        font = theme.label_font(13)
        shortcuts = font.render(
            "ESPACIO pausa   ←/→ ajusta λ   clic en enlace lo cae   E exporta   ESC salir",
            True, theme.text_muted)
        self.screen.blit(shortcuts, (24, self.config.screen_height - 28))

        status_font = theme.label_font(13)
        status = status_font.render(self.export_status, True, theme.text_primary)
        self.screen.blit(status, status.get_rect(topright=(self.config.screen_width - 24, self.config.screen_height - 28)))
