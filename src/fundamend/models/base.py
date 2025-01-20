from pydantic import BaseModel, ConfigDict


class FundamendBaseModel(BaseModel):
    """
    Base class for all models in the fundamend package. Defines all models as frozen.
    """

    model_config = ConfigDict(frozen=True)
