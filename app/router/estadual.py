from fastapi import APIRouter, Request, Depends
from app.services import Estadual
from app.utils.dependencies import get_tools

router = APIRouter(prefix="/estadual")


@router.get("/{uf}/{cnpj}")
async def z(request: Request, cnpj, uf, tools=Depends(get_tools)):
    page, context = tools
    method = getattr(Estadual, uf)
    return await method(page=page, context=context, cnpj=cnpj)
