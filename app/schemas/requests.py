from pydantic import BaseModel, field_validator, ConfigDict


class BaseCndRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    cnpj: str


class EstadualRequest(BaseCndRequest):
    uf: str

    @field_validator("uf")
    @classmethod
    def validate_uf(cls, v):
        return v.upper().strip()


class MunicipalRequest(BaseCndRequest):
    uf: str
    municipio: str

    @field_validator("uf")
    @classmethod
    def validate_uf(cls, v):
        return v.upper().strip()

    @field_validator("municipio")
    @classmethod
    def validate_municipio(cls, v):
        return v.lower().strip().replace(" ", "_")
