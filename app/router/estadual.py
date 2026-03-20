from fastapi import APIRouter, Depends
from fastapi.responses import Response

from app.utils.dependencies import get_tools
from app.services.estadual import Estadual
from app.schemas import EstadualRequest

router = APIRouter(prefix="/estadual")


@router.post("")
async def estadual(data: EstadualRequest, tools=Depends(get_tools)):
    page, context = tools
    pdf_buffer = await Estadual.execute_scrap(
        page=page, context=context, cnpj=data.cnpj, uf=data.uf
    )
    return Response(content=pdf_buffer, media_type="application/pdf")
