from pydantic import BaseModel

class LatLng(BaseModel):
    lat: float
    lng: float

class CreateTripRequest(BaseModel):
    rider_id: str
    pickup: LatLng
    dropoff: LatLng
