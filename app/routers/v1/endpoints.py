# pylint: disable=duplicate-code
from fastapi import APIRouter, HTTPException
from .mongodb_engine import MongoDB, SearchParameters
from .utils import get_version, logger

version = get_version(__name__)

router = APIRouter(
    prefix=f"/{version}/movies",
    responses={404: {"description": "Not found"}},
    tags=[version],
)

mongodb = MongoDB(db_name="movielens1m", collection_name="movie")


@router.get("/search")
async def search_movie(q: str = None, genre: str = None,
                       skip: int = None, limit: int = 30,
                       order_by="release_year"):

    params = SearchParameters(
        search_text=q,
        genre=genre,
        skip=skip,
        order_by=order_by,
        limit=limit
    )

    try:
        response = mongodb.search(params)
    # pylint:disable=unused-argument,broad-exception-caught,unexpected-keyword-arg
    except Exception as exception:
        logger.error(exception)
        return HTTPException(status_code=500, detail=str(exception))
    return response
