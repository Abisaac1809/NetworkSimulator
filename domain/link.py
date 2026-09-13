class Link:
    def __init__(self, identifier, source_id, target_id, latency_ms):
        self.identifier = identifier
        self.source_id = source_id
        self.target_id = target_id
        self.latency_ms = latency_ms
        self.is_active = True
        self.packets_in_transit = []

    def toggle(self):
        self.is_active = not self.is_active
        return self.is_active
