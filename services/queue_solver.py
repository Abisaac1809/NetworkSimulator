class QueueSolver:
    def utilization(self, arrival_rate, service_rate):
        if service_rate <= 0:
            return 1.0
        return arrival_rate / service_rate

    def metrics(self, arrival_rate, service_rate):
        rho = self.utilization(arrival_rate, service_rate)
        if rho >= 1.0:
            return {
                "rho": rho,
                "l": float("inf"),
                "lq": float("inf"),
                "w": float("inf"),
                "wq": float("inf"),
            }
        l = rho / (1.0 - rho)
        lq = (rho * rho) / (1.0 - rho)
        w = 1.0 / (service_rate - arrival_rate)
        wq = rho / (service_rate - arrival_rate)
        return {"rho": rho, "l": l, "lq": lq, "w": w, "wq": wq}

    def finite_capacity_metrics(self, arrival_rate, service_rate, capacity):
        rho = self.utilization(arrival_rate, service_rate)
        if capacity <= 0:
            return {"rho": rho, "blocking_probability": 1.0, "l": 0.0, "lq": 0.0, "throughput": 0.0}
        if abs(rho - 1.0) < 1e-9:
            p_zero = 1.0 / (capacity + 1)
            blocking = p_zero
            l = capacity / 2.0
        else:
            p_zero = (1.0 - rho) / (1.0 - rho ** (capacity + 1))
            blocking = p_zero * (rho ** capacity)
            numerator = 1.0 - (capacity + 1) * rho ** capacity + capacity * rho ** (capacity + 1)
            l = rho * numerator / ((1.0 - rho) * (1.0 - rho ** (capacity + 1)))
        effective_arrival = arrival_rate * (1.0 - blocking)
        lq = l - (effective_arrival / service_rate) if service_rate > 0 else l
        return {
            "rho": rho,
            "blocking_probability": blocking,
            "l": l,
            "lq": max(0.0, lq),
            "throughput": effective_arrival,
        }
