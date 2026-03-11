from fastapi import APIRouter, Depends
from fastapi.params import Body

from app.utils.dependencies import get_tools
from app.services.municipal import Municipal
from app.utils.wrapper import handle_scraping_request
from app.schemas import BaseCndRequest

router = APIRouter(prefix="/municipal")


@router.post("")
@handle_scraping_request
async def municipal(data: BaseCndRequest, tools=Depends(get_tools)):
    page, context = tools
    return await Municipal.execute_scrap(page=page, context=context, cnpj=data.cnpj)

