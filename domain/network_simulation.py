import random

from domain.node import Node
from domain.link import Link
from domain.packet import Packet


class NetworkSimulation:
    def __init__(self, config, queue_solver, inventory_solver, transport_solver):
        self.config = config
        self.queue_solver = queue_solver
        self.inventory_solver = inventory_solver
        self.transport_solver = transport_solver

        self.arrival_rate = config.arrival_rate
        self.service_rate = config.service_rate
        self.buffer_capacity = config.buffer_capacity
        self.replenish_threshold = config.replenish_threshold
        self.batch_size = config.batch_size
        self.holding_cost_rate = config.holding_cost_rate
        self.shortage_penalty = config.shortage_penalty
        self.alpha = config.assignment_alpha

        self.sim_time = 0.0
        self.is_paused = False
        self.packet_counter = 0
        self.next_arrival_at = 0.0

        self.completed = []
        self.packets_lost = 0
        self.packets_generated = 0
        self.integral_in_system = 0.0
        self.integral_in_queue = 0.0
        self.last_dropped_at = -1.0

        self.nodes = {}
        self.links = {}
        self._build_topology()
        self._schedule_arrival()

    def _build_topology(self):
        self.nodes["GW"] = Node("GW", "Gateway", 110, 300, self.service_rate * 10, 9999, 0, is_source=True)
        self.nodes["R1"] = Node("R1", "Router 1", 350, 150, self.service_rate, self.buffer_capacity, self.replenish_threshold)
        self.nodes["R2"] = Node("R2", "Router 2", 350, 460, self.service_rate, self.buffer_capacity, self.replenish_threshold)
        self.nodes["R3"] = Node("R3", "Router 3", 600, 150, self.service_rate, self.buffer_capacity, self.replenish_threshold)
        self.nodes["R4"] = Node("R4", "Router 4", 600, 460, self.service_rate, self.buffer_capacity, self.replenish_threshold)
        self.nodes["S1"] = Node("S1", "Servidor A", 850, 210, self.service_rate * 1.5, self.buffer_capacity, self.replenish_threshold, is_sink=True)
        self.nodes["S2"] = Node("S2", "Servidor B", 850, 400, self.service_rate * 1.5, self.buffer_capacity, self.replenish_threshold, is_sink=True)

        definitions = [
            ("GW>R1", "GW", "R1", 12.0),
            ("GW>R2", "GW", "R2", 14.0),
            ("R1>R3", "R1", "R3", 10.0),
            ("R1>R4", "R1", "R4", 25.0),
            ("R2>R3", "R2", "R3", 22.0),
            ("R2>R4", "R2", "R4", 11.0),
            ("R3>S1", "R3", "S1", 8.0),
            ("R3>S2", "R3", "S2", 18.0),
            ("R4>S1", "R4", "S1", 19.0),
            ("R4>S2", "R4", "S2", 9.0),
        ]
        for identifier, source, target, latency in definitions:
            self.links[identifier] = Link(identifier, source, target, latency)

    def _schedule_arrival(self):
        if self.arrival_rate > 0:
            self.next_arrival_at = self.sim_time + random.expovariate(self.arrival_rate)
        else:
            self.next_arrival_at = self.sim_time + 1e9

    def toggle_pause(self):
        self.is_paused = not self.is_paused
        return self.is_paused

    def toggle_link(self, link_id):
        if link_id in self.links:
            return self.links[link_id].toggle()
        return False

    def adjust_arrival_rate(self, delta):
        target = self.arrival_rate + delta
        self.arrival_rate = min(self.config.max_arrival_rate, max(self.config.min_arrival_rate, target))

    def _active_links_from(self, node_id):
        return [link for link in self.links.values()
                if link.source_id == node_id and link.is_active]

    def _select_link(self, packet, candidate_links):
        if not candidate_links:
            return None
        targets = []
        for link in candidate_links:
            node = self.nodes[link.target_id]
            targets.append({
                "link_id": link.identifier,
                "latency": link.latency_ms,
                "capacity": node.capacity,
                "occupancy": node.occupancy,
                "is_active": link.is_active,
            })
        flows = [{"id": packet.identifier, "size": packet.size}]
        assignments = self.transport_solver.route(flows, targets, self.alpha)
        if assignments:
            return assignments[0]["target"]["link_id"]
        return random.choice(candidate_links).identifier

    def _generate_packet(self):
        self.packet_counter += 1
        self.packets_generated += 1
        packet = Packet(self.packet_counter, self.sim_time)
        link_id = self._select_link(packet, self._active_links_from("GW"))
        if link_id is None:
            self._register_loss()
            return
        packet.current_link = link_id
        packet.link_progress = 0.0
        self.links[link_id].packets_in_transit.append(packet)

    def _register_loss(self, node=None):
        self.packets_lost += 1
        self.last_dropped_at = self.sim_time
        if node is not None:
            node.dropped += 1
            node.shortage_cost += self.inventory_solver.shortage_cost(1, self.shortage_penalty)

    def _forward(self, node, packet):
        if node.is_sink:
            packet.departed_at = self.sim_time
            packet.wait_time = max(0.0, (packet.service_started_at or self.sim_time)
                                   - (packet.queue_entered_at or packet.created_at))
            self.completed.append(packet)
            return
        link_id = self._select_link(packet, self._active_links_from(node.identifier))
        if link_id is None:
            self._register_loss(node)
            return
        packet.current_link = link_id
        packet.current_node = None
        packet.link_progress = 0.0
        self.links[link_id].packets_in_transit.append(packet)

    def step(self, dt):
        if self.is_paused:
            return
        self.sim_time += dt
        while self.sim_time >= self.next_arrival_at:
            self._generate_packet()
            self._schedule_arrival()
        self._advance_links(dt)
        self._advance_nodes(dt)
        self._integrate_metrics(dt)

    def _advance_links(self, dt):
        for link in self.links.values():
            if not link.is_active:
                if link.packets_in_transit:
                    for _ in link.packets_in_transit:
                        self._register_loss()
                    link.packets_in_transit.clear()
                continue
            speed = 2.5 / max(0.2, link.latency_ms / 15.0)
            arrived = []
            for packet in link.packets_in_transit:
                packet.link_progress += speed * dt
                if packet.link_progress >= 1.0:
                    arrived.append(packet)
            for packet in arrived:
                link.packets_in_transit.remove(packet)
                node = self.nodes[link.target_id]
                if node.can_admit():
                    packet.current_link = None
                    packet.current_node = node.identifier
                    node.admit(packet, self.sim_time)
                else:
                    self._register_loss(node)

    def _advance_nodes(self, dt):
        for node in self.nodes.values():
            if node.is_source:
                continue
            node.holding_cost += self.inventory_solver.holding_cost(node.occupancy, self.holding_cost_rate, dt)
            if node.serving is None and node.queue:
                packet = node.queue.pop(0)
                node.serving = packet
                packet.service_started_at = self.sim_time
                node.service_remaining = random.expovariate(node.service_rate) if node.service_rate > 0 else 0.1
            if node.serving is not None:
                node.service_remaining -= dt
                if node.service_remaining <= 0:
                    served = node.serving
                    node.serving = None
                    node.release()
                    node.processed += 1
                    self._forward(node, served)

    def _integrate_metrics(self, dt):
        in_queue = sum(len(node.queue) for node in self.nodes.values() if not node.is_source)
        in_service = sum(1 for node in self.nodes.values()
                         if not node.is_source and node.serving is not None)
        self.integral_in_system += (in_queue + in_service) * dt
        self.integral_in_queue += in_queue * dt

    @property
    def packets_processed(self):
        return len(self.completed)

    @property
    def loss_rate(self):
        total = self.packets_processed + self.packets_lost
        return (self.packets_lost / total * 100.0) if total else 0.0

    @property
    def wq(self):
        if not self.completed:
            return 0.0
        return sum(packet.wait_time for packet in self.completed) / len(self.completed)

    @property
    def w(self):
        if not self.completed:
            return 0.0
        total = sum((packet.departed_at - packet.created_at)
                    for packet in self.completed if packet.departed_at)
        return total / len(self.completed)

    @property
    def l(self):
        return self.integral_in_system / self.sim_time if self.sim_time > 0 else 0.0

    @property
    def lq(self):
        return self.integral_in_queue / self.sim_time if self.sim_time > 0 else 0.0

    @property
    def holding_cost(self):
        return sum(node.holding_cost for node in self.nodes.values())

    @property
    def shortage_cost(self):
        return sum(node.shortage_cost for node in self.nodes.values())

    @property
    def total_cost(self):
        return self.holding_cost + self.shortage_cost

    def metrics_summary(self):
        analytic = self.queue_solver.metrics(self.arrival_rate, self.service_rate)
        return {
            "sim_time": round(self.sim_time, 2),
            "arrival_rate": round(self.arrival_rate, 2),
            "service_rate": round(self.service_rate, 2),
            "buffer_capacity": self.buffer_capacity,
            "replenish_threshold": self.replenish_threshold,
            "batch_size": self.batch_size,
            "alpha": self.alpha,
            "packets_processed": self.packets_processed,
            "packets_lost": self.packets_lost,
            "loss_rate": round(self.loss_rate, 2),
            "wq": round(self.wq, 4),
            "w": round(self.w, 4),
            "l": round(self.l, 2),
            "lq": round(self.lq, 2),
            "rho": round(analytic["rho"], 3),
            "theoretical_l": analytic["l"],
            "theoretical_wq": analytic["wq"],
            "holding_cost": round(self.holding_cost, 2),
            "shortage_cost": round(self.shortage_cost, 2),
            "total_cost": round(self.total_cost, 2),
        }
