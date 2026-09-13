class Packet:
    def __init__(self, identifier, created_at, size=1.0):
        self.identifier = identifier
        self.created_at = created_at
        self.size = size
        self.current_link = None
        self.current_node = None
        self.link_progress = 0.0
        self.queue_entered_at = None
        self.service_started_at = None
        self.departed_at = None
        self.wait_time = 0.0
