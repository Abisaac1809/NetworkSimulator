import requests


class AIService:
    def __init__(self, config):
        self.config = config

    def analyze(self, report_text, metrics):
        if self.config.has_gemini_key():
            remote = self._call_gemini(report_text)
            if remote:
                return remote
        return self._local_analysis(metrics)

    def _call_gemini(self, report_text):
        api_key = self.config.gemini_api_key()
        model = self.config.ai_model
        url = (f"https://generativelanguage.googleapis.com/v1beta/models/"
               f"{model}:generateContent?key={api_key}")
        prompt = (
            "Actúa como ingeniero senior de redes y analista de investigación de operaciones.\n"
            f"{self.config.ai_prompt}\n\n"
            f"--- REPORTE DE SIMULACIÓN ---\n{report_text}\n\n"
            "Entrega el análisis en prosa técnica, con una sección de conclusiones y "
            "exactamente tres recomendaciones numeradas de optimización."
        )
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.3, "maxOutputTokens": 4096},
        }
        try:
            print(f"[IA] Consultando Gemini ({model})...")
            response = requests.post(url, json=payload, timeout=self.config.ai_request_timeout)
            if response.status_code != 200:
                print(f"[IA] Respuesta HTTP {response.status_code}. Se usa el análisis local.")
                return None
            candidates = response.json().get("candidates", [])
            if not candidates:
                return None
            parts = candidates[0].get("content", {}).get("parts", [])
            text = "\n".join(part.get("text", "") for part in parts if "text" in part).strip()
            if not text:
                return None
            return self._wrap_remote(model, text)
        except requests.RequestException as error:
            print(f"[IA] Error de conexión: {error}. Se usa el análisis local.")
            return None

    def _wrap_remote(self, model, text):
        header = f"DIAGNÓSTICO DE IA · GEMINI {model.upper()}"
        return f"{header}\n{'-' * len(header)}\nPrompt enviado: {self.config.ai_prompt}\n\n{text}"

    def _local_analysis(self, metrics):
        rho = metrics.get("rho", 0.0)
        loss_rate = metrics.get("loss_rate", 0.0)
        wq = metrics.get("wq", 0.0)
        holding = metrics.get("holding_cost", 0.0)
        shortage = metrics.get("shortage_cost", 0.0)
        total = metrics.get("total_cost", 0.0)
        capacity = metrics.get("buffer_capacity", 0)
        threshold = metrics.get("replenish_threshold", 0)

        if rho < 0.7:
            regime = "capacidad holgada frente a la demanda actual"
        elif rho <= 0.9:
            regime = "punto de operación eficiente, cercano al límite recomendado"
        else:
            regime = "congestión severa con riesgo de inestabilidad de colas"

        if loss_rate == 0:
            loss_reading = "sin descartes: el buffer absorbe los picos de llegada"
        elif loss_rate <= 3.0:
            loss_reading = f"pérdida contenida ({loss_rate:.2f}%), dentro de una tolerancia razonable de QoS"
        else:
            loss_reading = f"pérdida elevada ({loss_rate:.2f}%) por desbordamiento recurrente de buffer"

        dominant = "penalización por descarte" if shortage > holding else "permanencia en memoria"
        shortage_share = (shortage / total * 100.0) if total > 0 else 0.0

        return "\n".join([
            "DIAGNÓSTICO LOCAL · MOTOR ANALÍTICO",
            "-----------------------------------",
            f"Prompt de referencia: {self.config.ai_prompt}",
            "",
            "Lectura del sistema",
            f"  · Intensidad de tráfico ρ = {rho:.2f} → {regime}.",
            f"  · Pérdida de paquetes: {loss_reading}.",
            f"  · Tiempo medio de espera en cola Wq = {wq:.4f} s.",
            "",
            "Costos",
            f"  · Almacenamiento: ${holding:.2f}",
            f"  · Penalización por ruptura: ${shortage:.2f} ({shortage_share:.1f}% del total)",
            f"  · Costo global: ${total:.2f}",
            "",
            "Recomendaciones",
            f"  1. Elevar el umbral de control de flujo s de {threshold} a {int(capacity * 0.35)} paquetes "
            "para anticipar ráfagas antes del desbordamiento.",
            f"  2. Sostener la intensidad de tráfico por debajo de ρ=0.80 aumentando μ o repartiendo carga "
            f"entre enlaces; hoy ρ={rho:.2f} y Wq={wq:.4f} s.",
            f"  3. Ponderar α en la asignación húngara para desviar flujos cuando la saturación supere el 70%, "
            f"reduciendo el costo dominante de {dominant}.",
        ])
