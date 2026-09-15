from typing import Optional

from pydantic import BaseModel


class ProvinceResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str] = None
    image: Optional[str] = None

    model_config = {"from_attributes": True}
