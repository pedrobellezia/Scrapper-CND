from pydantic import BaseModel, field_validator
import re


class BaseCndRequest(BaseModel):
    cnpj: str

    @field_validator('cnpj')
    @classmethod
    def validate_cnpj(cls, v):
        """Validate CNPJ format - should be 14 digits with optional punctuation"""
        # Remove common formatting characters
        clean_cnpj = re.sub(r'[\s\.\/-]', '', v)

        # Check if it's all digits and has 14 characters
        if not clean_cnpj.isdigit() or len(clean_cnpj) != 14:
            raise ValueError('CNPJ deve conter 14 dígitos')

        return clean_cnpj

