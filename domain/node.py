class Node:
    def __init__(self, identifier, label, x, y, service_rate,
                 capacity, threshold, is_source=False, is_sink=False):
        self.identifier = identifier
        self.label = label
        self.x = x
        self.y = y
        self.service_rate = service_rate
        self.capacity = capacity
        self.threshold = threshold
        self.is_source = is_source
        self.is_sink = is_sink

        self.queue = []
        self.serving = None
        self.service_remaining = 0.0

        self.occupancy = 0
        self.processed = 0
        self.dropped = 0
        self.holding_cost = 0.0
        self.shortage_cost = 0.0

    def can_admit(self):
        return self.occupancy < self.capacity

    def admit(self, packet, now):
        self.occupancy += 1
        packet.queue_entered_at = now
        self.queue.append(packet)

    def release(self):
        if self.occupancy > 0:
            self.occupancy -= 1

    def saturation(self):
        if self.capacity <= 0:
            return 0.0
        return min(1.0, self.occupancy / float(self.capacity))

    def needs_replenishment(self):
        return self.occupancy <= self.threshold
