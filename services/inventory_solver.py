import math


class InventorySolver:
    def holding_cost(self, occupancy, holding_rate, delta_time):
        return occupancy * holding_rate * delta_time

    def shortage_cost(self, lost_packets, penalty):
        return lost_packets * penalty

    def saturation(self, occupancy, capacity):
        if capacity <= 0:
            return 0.0
        return min(1.0, occupancy / float(capacity))

    def needs_replenishment(self, occupancy, threshold):
        return occupancy <= threshold

    def optimal_batch(self, demand_rate, order_cost, holding_rate):
        if holding_rate <= 0 or demand_rate <= 0:
            return 0.0
        return math.sqrt((2.0 * demand_rate * order_cost) / holding_rate)

    def total_cost(self, holding_total, shortage_total):
        return holding_total + shortage_total
