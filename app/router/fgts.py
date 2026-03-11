from fastapi import APIRouter, Depends
from fastapi.params import Body

from app.utils.dependencies import get_tools
from app.services.fgts import Fgts
from app.utils.wrapper import handle_scraping_request
from app.schemas import BaseCndRequest

router = APIRouter(prefix="/fgts")


@router.post("")
@handle_scraping_request
async def fgts(data: BaseCndRequest, tools=Depends(get_tools)):
    page, context = tools
    return await Fgts.execute_scrap(page=page, context=context, cnpj=data.cnpj)


