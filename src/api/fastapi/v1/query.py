from fastapi import APIRouter, Body, Depends, HTTPException, status

from src.schemas.query_request import QueryRequest
from src.schemas.query_response import QueryResponse
from src.use_cases.query import QueryUseCase

router = APIRouter(tags=["query"], prefix="/query")


@router.post("/", status_code=status.HTTP_200_OK, response_model=QueryResponse)
async def read_query(
    request: QueryRequest = Body(...), usecase: QueryUseCase = Depends()
):
    try:
        best_doc = await usecase.find_best_document(request.query)

        ai_response = await usecase.get_ai_response(request.query, best_doc["text"])

        return QueryResponse(response=ai_response)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc
