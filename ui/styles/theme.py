import pygame


class Theme:
    def __init__(self):
        pygame.font.init()
        self.background = (24, 26, 30)
        self.surface = (33, 36, 41)
        self.surface_raised = (44, 48, 55)
        self.border = (58, 63, 71)
        self.grid = (36, 39, 45)
        self.text_primary = (223, 227, 232)
        self.text_muted = (144, 150, 159)
        self.text_inverted = (24, 26, 30)

        self.saturation_low = (108, 163, 129)
        self.saturation_medium = (198, 170, 102)
        self.saturation_high = (198, 108, 104)

        self.packet = (206, 210, 216)
        self.packet_lost = (198, 108, 104)
        self.link_active = (78, 84, 94)
        self.link_down = (52, 56, 63)

        self._label_cache = {}
        self._mono_cache = {}
        self._label_family = self._resolve_family(
            ["Inter", "Helvetica Neue", "DejaVu Sans", "Arial"])
        self._mono_family = self._resolve_family(
            ["JetBrains Mono", "DejaVu Sans Mono", "Menlo", "Consolas", "monospace"])

    def _resolve_family(self, candidates):
        available = set(pygame.font.get_fonts())
        for name in candidates:
            normalized = name.lower().replace(" ", "")
            if normalized in available:
                return normalized
        return None

    def label_font(self, size, bold=False):
        key = (size, bold)
        if key not in self._label_cache:
            self._label_cache[key] = pygame.font.SysFont(self._label_family, size, bold=bold)
        return self._label_cache[key]

    def mono_font(self, size, bold=False):
        key = (size, bold)
        if key not in self._mono_cache:
            self._mono_cache[key] = pygame.font.SysFont(self._mono_family, size, bold=bold)
        return self._mono_cache[key]

    def saturation_color(self, ratio):
        if ratio < 0.5:
            return self.saturation_low
        if ratio <= 0.8:
            return self.saturation_medium
        return self.saturation_high
