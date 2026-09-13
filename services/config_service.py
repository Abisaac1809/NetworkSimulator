import os


class ConfigService:
    def __init__(self):
        self._load_environment()
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.base_dir = base_dir
        self.assets_dir = os.path.join(base_dir, "assets")
        self.report_txt_path = os.path.join(base_dir, "reporte_simulacion.txt")
        self.report_docx_path = os.path.join(base_dir, "informe_tecnico.docx")

        self.screen_width = 1360
        self.screen_height = 820
        self.frames_per_second = 60

        self.arrival_rate = 15.0
        self.service_rate = 18.0
        self.buffer_capacity = 50
        self.replenish_threshold = 10
        self.batch_size = 20
        self.holding_cost_rate = 0.5
        self.shortage_penalty = 10.0
        self.assignment_alpha = 15.0
        self.assignment_interval = 0.5

        self.arrival_rate_step = 1.0
        self.min_arrival_rate = 1.0
        self.max_arrival_rate = 60.0

        self.ai_provider = os.environ.get("API_PROVIDER", "GEMINI").upper()
        self.ai_model = os.environ.get("API_MODEL", "gemini-2.5-flash").strip()
        self.ai_request_timeout = 30
        self.ai_prompt = (
            "Analiza los siguientes resultados de desempeño de un simulador de red basado "
            "en teoría de colas e inventario. Evalúa la tasa de pérdida de paquetes, tiempos "
            "de espera y costos, e indica conclusiones detalladas y 3 recomendaciones de optimización."
        )

    def _load_environment(self):
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            env_path = os.path.join(os.getcwd(), ".env")
            if os.path.exists(env_path):
                with open(env_path, "r", encoding="utf-8") as handle:
                    for raw_line in handle:
                        line = raw_line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            key, value = line.split("=", 1)
                            os.environ.setdefault(key.strip(), value.strip().strip("\"'"))

    def gemini_api_key(self):
        return (os.environ.get("GEMINI_API_KEY", "").strip()
                or os.environ.get("API_KEY", "").strip())

    def has_gemini_key(self):
        key = self.gemini_api_key()
        return bool(key) and key != "tu_api_key_aqui"
