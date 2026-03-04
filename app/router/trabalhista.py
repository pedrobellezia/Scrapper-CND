from fastapi import APIRouter, Request, Depends
from app.services import Trabalhista
from app.utils.dependencies import get_tools

router = APIRouter(prefix="/trabalhista")


@router.get("/{cnpj}")
async def z(request: Request, cnpj, tools=Depends(get_tools)):
    page, context = tools
    return await Trabalhista.execute_scrap(page=page, context=context, cnpj=cnpj)
