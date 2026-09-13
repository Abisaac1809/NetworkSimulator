import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from services.config_service import ConfigService
from services.queue_solver import QueueSolver
from services.inventory_solver import InventorySolver
from services.transport_solver import TransportSolver
from services.ai_service import AIService
from services.report_service import ReportService
from ui.app import App


def main():
    config = ConfigService()
    queue_solver = QueueSolver()
    inventory_solver = InventorySolver()
    transport_solver = TransportSolver()
    ai_service = AIService(config)
    report_service = ReportService(config, ai_service)

    app = App(config, queue_solver, inventory_solver, transport_solver, report_service)
    app.run()


if __name__ == "__main__":
    main()
