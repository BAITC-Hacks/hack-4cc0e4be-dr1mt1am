"""Thin, stateless HTTP layer. No simulation or scoring formulas."""

import os

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from ai.analyzer import analyze_simulation
from ai.models import AIAnalysisError, MissingAPIKeyError
from engine.simulator import simulate_scenario
from .schemas import ScenarioRequest
from .serializers import catalog_response, json_snapshot, simulation_response


def create_app() -> FastAPI:
    application = FastAPI(title="Akim for 5 Hours API", version="1.0.0")
    origin = os.environ.get("FRONTEND_ORIGIN", "").strip() or "http://localhost:5173"
    application.add_middleware(
        CORSMiddleware, allow_origins=[origin], allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"], allow_credentials=False,
    )

    @application.exception_handler(RequestValidationError)
    async def malformed_request(_request: Request, _error: RequestValidationError):
        # Do not echo arbitrary client input or allow client-generated score fields.
        return JSONResponse(status_code=422, content={"error": {
            "code": "INVALID_REQUEST", "message": "Некорректный формат запроса. Передайте только decisions с initiative_id и district.",
        }})

    @application.get("/api/health")
    def health():
        return {"status": "ok"}

    @application.get("/api/catalog")
    def catalog():
        return catalog_response()

    @application.post("/api/simulate")
    def simulate(request: ScenarioRequest):
        return simulation_response(simulate_scenario(request.to_decisions()))

    @application.post("/api/analyze")
    def analyze(request: ScenarioRequest):
        result = simulate_scenario(request.to_decisions())
        if not result.valid:
            return simulation_response(result)
        try:
            return json_snapshot(analyze_simulation(result))
        except MissingAPIKeyError:
            return JSONResponse(status_code=503, content={"error": {
                "code": "API_KEY_MISSING", "message": "AI-анализ недоступен: не настроен OPENAI_API_KEY.",
            }})
        except AIAnalysisError as error:
            return JSONResponse(status_code=502, content={"error": {
                "code": error.code,
                "message": "Не удалось получить AI-анализ. Результаты симуляции сохранены.",
            }})

    return application


app = create_app()
