from fastapi import APIRouter, Request, Depends
from app.utils.dependencies import get_tools
from app.services.fgts import Fgts

router = APIRouter(prefix="/fgts")


@router.get("/{cnpj}")
async def z(request: Request, cnpj, tools=Depends(get_tools)):
    page, context = tools
    return await Fgts.execute_scrap(page=page, context=context, cnpj=cnpj)
