from fastapi import APIRouter, Depends
from fastapi.params import Body

from app.services import Trabalhista
from app.utils.dependencies import get_tools
from app.utils.wrapper import handle_scraping_request
from app.schemas import BaseCndRequest

router = APIRouter(prefix="/trabalhista")


@router.post("")
@handle_scraping_request
async def trabalhista(data: BaseCndRequest, tools=Depends(get_tools)):
    page, context = tools
    return await Trabalhista.execute_scrap(page=page, context=context, cnpj=data.cnpj)


