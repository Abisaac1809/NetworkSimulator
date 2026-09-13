import pygame


class NetworkCanvas:
    def __init__(self, rect, theme):
        self.rect = pygame.Rect(rect)
        self.theme = theme
        self.node_radius = 26

    def _node_position(self, node):
        return (self.rect.x + node.x, self.rect.y + node.y)

    def _link_endpoints(self, simulation, link):
        source = self._node_position(simulation.nodes[link.source_id])
        target = self._node_position(simulation.nodes[link.target_id])
        return source, target

    def link_at(self, simulation, position):
        for link in simulation.links.values():
            source, target = self._link_endpoints(simulation, link)
            if self._distance_to_segment(position, source, target) <= 8:
                return link.identifier
        return None

    def _distance_to_segment(self, point, start, end):
        px, py = point
        ax, ay = start
        bx, by = end
        dx, dy = bx - ax, by - ay
        length_squared = dx * dx + dy * dy
        if length_squared == 0:
            return ((px - ax) ** 2 + (py - ay) ** 2) ** 0.5
        t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / length_squared))
        cx, cy = ax + t * dx, ay + t * dy
        return ((px - cx) ** 2 + (py - cy) ** 2) ** 0.5

    def draw(self, surface, simulation):
        self._draw_background(surface)
        self._draw_links(surface, simulation)
        self._draw_packets(surface, simulation)
        self._draw_nodes(surface, simulation)

    def _draw_background(self, surface):
        pygame.draw.rect(surface, self.theme.surface, self.rect, border_radius=14)
        pygame.draw.rect(surface, self.theme.border, self.rect, width=1, border_radius=14)
        spacing = 34
        clip = surface.get_clip()
        surface.set_clip(self.rect.inflate(-2, -2))
        for x in range(self.rect.x, self.rect.right, spacing):
            pygame.draw.line(surface, self.theme.grid, (x, self.rect.y), (x, self.rect.bottom))
        for y in range(self.rect.y, self.rect.bottom, spacing):
            pygame.draw.line(surface, self.theme.grid, (self.rect.x, y), (self.rect.right, y))
        surface.set_clip(clip)

    def _draw_links(self, surface, simulation):
        for link in simulation.links.values():
            source, target = self._link_endpoints(simulation, link)
            if link.is_active:
                pygame.draw.line(surface, self.theme.link_active, source, target, 2)
            else:
                self._draw_dashed_line(surface, source, target)

    def _draw_dashed_line(self, surface, start, end):
        segments = 18
        for index in range(segments):
            if index % 2 == 0:
                a = self._interpolate(start, end, index / segments)
                b = self._interpolate(start, end, (index + 1) / segments)
                pygame.draw.line(surface, self.theme.link_down, a, b, 2)

    def _interpolate(self, start, end, ratio):
        return (start[0] + (end[0] - start[0]) * ratio,
                start[1] + (end[1] - start[1]) * ratio)

    def _draw_packets(self, surface, simulation):
        for link in simulation.links.values():
            if not link.is_active:
                continue
            source, target = self._link_endpoints(simulation, link)
            for packet in link.packets_in_transit:
                position = self._interpolate(source, target, min(1.0, packet.link_progress))
                pygame.draw.circle(surface, self.theme.packet,
                                   (int(position[0]), int(position[1])), 4)

    def _draw_nodes(self, surface, simulation):
        label_font = self.theme.label_font(13, bold=True)
        detail_font = self.theme.mono_font(12)
        for node in simulation.nodes.values():
            x, y = self._node_position(node)
            if node.is_source:
                ring_color = self.theme.text_muted
            else:
                ring_color = self.theme.saturation_color(node.saturation())
            pygame.draw.circle(surface, self.theme.surface_raised, (x, y), self.node_radius)
            pygame.draw.circle(surface, ring_color, (x, y), self.node_radius, 3)

            label = label_font.render(node.label, True, self.theme.text_primary)
            surface.blit(label, label.get_rect(center=(x, y + self.node_radius + 14)))

            if not node.is_source:
                detail = detail_font.render(f"{node.occupancy}/{node.capacity}", True, self.theme.text_muted)
                surface.blit(detail, detail.get_rect(center=(x, y)))
