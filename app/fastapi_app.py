# from fastapi import FastAPI

# from app.api.routes import router


# app = FastAPI(
#     title="SAP AI Agent RAG API",
#     description=(
#         "Document Question Answering using "
#         "SAP HANA Vector Engine and SAP AI Core"
#     ),
#     version="1.0.0",
# )


# @app.get("/")
# def root():
#     return {
#         "message": "SAP AI Agent RAG API is running"
#     }


# app.include_router(router)
from fastapi import FastAPI

from app.api.routes import router


app = FastAPI(
    title="SAP AI Agent RAG API",
    description=(
        "Document Question Answering using "
        "SAP HANA Vector Engine and SAP AI Core"
    ),
    version="1.0.0",
)


@app.get("/")
def root():
    return {
        "message": "SAP AI Agent RAG API is running"
    }


app.include_router(router)