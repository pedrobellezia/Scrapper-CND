from fastapi import APIRouter, Request, Depends
from app.services import Municipal
from app.utils.dependencies import get_tools

router = APIRouter(prefix="/municipal")


@router.get("/{uf}/{municipio}/{cnpj}")
async def z(request: Request, cnpj, municipio, uf, tools=Depends(get_tools)):
    page, context = tools
    method = municipio + "_" + uf
    getattr(Municipal, method)
    return await method(page=page, context=context, cnpj=cnpj)
