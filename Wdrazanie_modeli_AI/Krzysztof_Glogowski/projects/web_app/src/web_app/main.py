import io
import logging
from contextlib import asynccontextmanager
from typing import Annotated, Callable

import uvicorn
from fastapi import BackgroundTasks, FastAPI, File, UploadFile, APIRouter
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi_versionizer.versionizer import Versionizer, api_version
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.templating import Jinja2Templates

from web_app.antivirus.clamav.connector import ClamavConnector
from web_app.antivirus.clamav.scanner import AntivirusScanner
from web_app.database.valkey.client import ValkeyClient
from web_app.database.valkey.connector import ValkeyConnector
from web_app.service.mapper.document_mapper import to_model_input
from web_app.service.middleware.correlation import CorrelationIdMiddleware
from web_app.service.middleware.request_time import RequestProcessingTimeMiddleware
from web_app.service.validator.upload_file_validator import UploadFileValidator
from web_app.task.valkey import write_to_valkey
from web_app.utils.error import APIError
from web_app.utils.hash import calculate_hash
from web_app.utils.log import setup_logging_with_correlation_id
from web_app.model.document_classifier import DocumentClassifier
from web_app.config.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up...")
    valkey_connector = ValkeyConnector(host=settings.VALKEY_HOST, port=settings.VALKEY_PORT)
    clamav_connector = ClamavConnector(host=settings.CLAMAV_HOST, port=settings.CLAMAV_PORT)
    app.state.settings = settings
    app.state.validator = UploadFileValidator()
    app.state.clamav_connector = clamav_connector
    app.state.antivirus = AntivirusScanner(clamav_connector)
    app.state.valkey_connector = valkey_connector
    app.state.valkey_client = ValkeyClient(valkey_connector)
    app.state.model = DocumentClassifier.from_path(settings.MODEL_PATH)

    yield

    print("Shutting down...")
    app.state.valkey_connector.close()


setup_logging_with_correlation_id()

app = FastAPI(lifespan=lifespan)

app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(RequestProcessingTimeMiddleware)

templates = Jinja2Templates(directory="resources/templates")

predict_router = APIRouter(prefix="", tags=["Prediction"])


@app.exception_handler(APIError)
async def api_error_exception_handler(request: Request, exc: APIError):
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error"},
    )


@app.exception_handler(Exception)
async def unknown_exception_handler(request: Request, exc: Exception):
    logging.critical("Unhandled error occurred in the API.", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error"},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logging.warning(f"Validation didn't pass, details = {exc.errors()}")
    return await request_validation_exception_handler(request, exc)


async def predict_template(
    document: UploadFile, background_tasks: BackgroundTasks, predict_fn: Callable, has_prefix: str
) -> JSONResponse:
    document_bytes = await document.read()
    app.state.antivirus.scan(document_bytes)
    app.state.validator.validate(io.BytesIO(document_bytes))
    document_hash = f"{has_prefix}_{calculate_hash(document_bytes)}"
    prediction = app.state.valkey_client.read(document_hash)

    if prediction is None:
        model_input = to_model_input(document_bytes)
        prediction = predict_fn(*model_input)
        background_tasks.add_task(
            func=write_to_valkey,
            valkey_client=app.state.valkey_client,
            key=document_hash,
            value=prediction,
        )
        from_cache = "false"
    else:
        from_cache = "true"

    return JSONResponse(
        content={"prediction": prediction},
        headers={"X-Readed-From-Cache": from_cache},
    )


@api_version(1)
@predict_router.post("/predict")
async def predict_v1(
    document: Annotated[UploadFile, File(description="File as UploadFile")],
    background_tasks: BackgroundTasks,
) -> JSONResponse:
    return await predict_template(document, background_tasks, app.state.model.classify, "v1")


@api_version(2)
@predict_router.post("/predict")
async def predict_v2(
    document: Annotated[UploadFile, File(description="File as UploadFile")],
    background_tasks: BackgroundTasks,
) -> JSONResponse:
    return await predict_template(document, background_tasks, app.state.model.classify_proba, "v2")


app.include_router(predict_router)

versions = Versionizer(
    app=app,
    prefix_format="/v{major}",
    semantic_version_format="{major}",
    latest_prefix="/latest",
    include_versions_route=True,
    sort_routes=True,
).versionize()


@app.get("/")
async def main(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="upload_document.html",
        context={"APP_HOST": settings.APP_HOST},
    )


@app.get("/readiness")
def ready_check() -> JSONResponse:
    app.state.valkey_connector.is_alive()
    app.state.clamav_connector.is_alive()
    return JSONResponse(content={"status": "ready"})


@app.get("/health")
def health_check() -> JSONResponse:
    return JSONResponse(content={"status": "healthy"})


if __name__ == "__main__":
    uvicorn.run(
        app=app,
        host="0.0.0.0",
        port=8080,
        workers=1,
        reload=False,
    )
