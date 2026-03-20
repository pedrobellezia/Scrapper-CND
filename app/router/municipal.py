from fastapi import APIRouter, Depends
from fastapi.responses import Response

from app.utils.dependencies import get_tools
from app.services.municipal import Municipal
from app.schemas import MunicipalRequest

router = APIRouter(prefix="/municipal")


@router.post("")
async def municipal(
    data: MunicipalRequest,
    tools=Depends(get_tools),
):
    page, context = tools
    pdf_buffer = await Municipal.execute_scrap(
        page=page, context=context, cnpj=data.cnpj, uf=data.uf, municipio=data.municipio
    )
    return Response(content=pdf_buffer, media_type="application/pdf")
