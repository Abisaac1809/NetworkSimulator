import numpy as np

try:
    from scipy.optimize import linear_sum_assignment
    _SCIPY_AVAILABLE = True
except ImportError:
    _SCIPY_AVAILABLE = False


class TransportSolver:
    def __init__(self, blocked_cost=1e9):
        self.blocked_cost = blocked_cost

    def build_cost_matrix(self, flows, targets, alpha):
        rows = len(flows)
        cols = len(targets)
        if rows == 0 or cols == 0:
            return np.zeros((0, 0))
        matrix = np.zeros((rows, cols), dtype=float)
        for i, flow in enumerate(flows):
            flow_size = flow.get("size", 1.0)
            for j, target in enumerate(targets):
                if not target.get("is_active", True):
                    matrix[i, j] = self.blocked_cost
                    continue
                latency = target.get("latency", 10.0)
                capacity = max(1, target.get("capacity", 1))
                occupancy = target.get("occupancy", 0)
                saturation = min(1.0, occupancy / float(capacity))
                matrix[i, j] = latency + alpha * saturation * 100.0 + flow_size * 0.1
        return matrix

    def solve_assignment(self, matrix):
        if _SCIPY_AVAILABLE:
            try:
                return linear_sum_assignment(matrix)
            except Exception:
                return self._greedy_assignment(matrix)
        return self._greedy_assignment(matrix)

    def _greedy_assignment(self, matrix):
        rows, cols = matrix.shape
        used_columns = set()
        selected_rows = []
        selected_cols = []
        for row in range(rows):
            best_column = -1
            best_value = float("inf")
            for column in range(cols):
                if column not in used_columns and matrix[row, column] < best_value:
                    best_value = matrix[row, column]
                    best_column = column
            if best_column != -1:
                used_columns.add(best_column)
                selected_rows.append(row)
                selected_cols.append(best_column)
        return np.array(selected_rows), np.array(selected_cols)

    def route(self, flows, targets, alpha):
        if not flows or not targets:
            return []
        matrix = self.build_cost_matrix(flows, targets, alpha)
        rows, cols = self.solve_assignment(matrix)
        assignments = []
        for row, column in zip(rows, cols):
            if matrix[row, column] >= self.blocked_cost * 0.5:
                continue
            assignments.append({
                "flow": flows[row],
                "target": targets[column],
                "cost": float(matrix[row, column]),
            })
        return assignments
