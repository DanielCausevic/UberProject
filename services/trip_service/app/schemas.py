from pydantic import BaseModel, Field, field_validator

class LatLng(BaseModel):
    lat: float = Field(ge=-90, le=90)
    lng: float = Field(ge=-180, le=180)

class CreateTripRequest(BaseModel):
    rider_id: str
    pickup: LatLng
    dropoff: LatLng
