from typing import List, Optional
from pydantic import BaseModel, Field


class Quantity(BaseModel):
    value: float = 0
    unit: str = "g"


class Macros(BaseModel):
    protein_g: float = 0
    carbs_g: float = 0
    fat_g: float = 0
    fibre_g: float = 0
    sugar_g: float = 0


class Micronutrients(BaseModel):
    sodium_mg: Optional[float] = None
    potassium_mg: Optional[float] = None
    calcium_mg: Optional[float] = None
    iron_mg: Optional[float] = None
    vitamin_c_mg: Optional[float] = None
    vitamin_d_mcg: Optional[float] = None
    folate_mcg: Optional[float] = None


class FoodItem(BaseModel):
    name: str
    category: Optional[str] = None
    estimated_quantity: Quantity
    calories_kcal: float = 0
    macros: Macros
    micronutrients: Micronutrients = Field(default_factory=Micronutrients)
    confidence: float = 0
    reasoning_summary: Optional[str] = ""
    assumptions: List[str] = Field(default_factory=list)


class Totals(BaseModel):
    calories_kcal: float = 0
    protein_g: float = 0
    carbs_g: float = 0
    fat_g: float = 0
    fibre_g: float = 0
    sugar_g: float = 0


class ImageMetadata(BaseModel):
    filename: str
    width: int = 0
    height: int = 0


class AnalyzeFoodResponse(BaseModel):
    request_id: str
    model_used: str
    train: bool
    status: str
    image_metadata: ImageMetadata
    items: List[FoodItem]
    totals: Totals
    accuracy_warnings: List[str] = Field(default_factory=list)
    improvement_questions: List[str] = Field(default_factory=list)


class CorrectionIn(BaseModel):
    prediction_item_id: str
    corrected_name: Optional[str] = None
    corrected_quantity_value: Optional[float] = None
    corrected_quantity_unit: Optional[str] = None
    corrected_calories_kcal: Optional[float] = None
    corrected_protein_g: Optional[float] = None
    corrected_carbs_g: Optional[float] = None
    corrected_fat_g: Optional[float] = None
    notes: Optional[str] = None
    corrected_by: Optional[str] = None
