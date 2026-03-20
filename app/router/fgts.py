from fastapi import APIRouter, Depends
from fastapi.responses import Response

from app.utils.dependencies import get_tools
from app.services.fgts import Fgts
from app.schemas import BaseCndRequest

router = APIRouter(prefix="/fgts")


@router.post("")
async def fgts(data: BaseCndRequest, tools=Depends(get_tools)):
    page, context = tools
    pdf_buffer = await Fgts.execute_scrap(page=page, context=context, cnpj=data.cnpj)
    return Response(content=pdf_buffer, media_type="application/pdf")
