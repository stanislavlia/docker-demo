from fastapi import FastAPI
from pydantic import BaseModel
from faker import Faker
import random
import logging
from contextlib import asynccontextmanager

from db import create_table_if_not_exist, insert_prediction, read_all_predictions



# ------------------- ML Model -------------------
def decision_tree_ml_model(loan, age, income, education, children):
    """Some trained ML model that estimates risk of default"""
    if (loan / income) <= 0.5 or loan < 1000:
         return random.uniform(0.6, 0.9)
    if age > 25 and not children:
        if education:
            return 0.001
        return 0.1 + random.uniform(-0.02, 0.02)
    if income < 60_000 and children:
        if not education:
            return 0.91
        return 0.8 + random.uniform(-0.02, 0.02)
    if age > 70:
         return 0.9
    if children and not education:
         return random.uniform(0.7, 1)
    return random.uniform(0.4, 0.6)

# ------------------- API Schemas -------------------
class ScoringFeaturesRequest(BaseModel):
    loan_usd: float
    person_age: int
    total_income_usd: float
    has_high_education: bool
    has_children: bool

class ScoringResponse(BaseModel):
    default_probability: float

# ------------------- FastAPI Endpoints -------------------

#Server Startup handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("Server starting up: ensuring predictions table exists.")
    create_table_if_not_exist()
    yield

app = FastAPI(lifespan=lifespan)
faker = Faker()

@app.get("/")
def root():
    return {"message": "app is running", "status": "healthy"}

@app.get("/user")
def get_random_user():
    name = faker.name()
    surname = faker.last_name()
    address = faker.address()
    email = faker.email()
    bod = faker.date_of_birth()
    ip_addr = faker.ipv4_public()
    logging.info(f"Generated user: {name} {surname}")
    return {
        "name": name,
        "lastname": surname,
        "address": address,
        "email": email,
        "date_of_birth": bod.isoformat(),
        "ip_addr": ip_addr
    }

@app.post("/predict")
def estimate_credit_scoring(request: ScoringFeaturesRequest):
    estimate = decision_tree_ml_model(
        age=request.person_age,
        loan=request.loan_usd,
        income=request.total_income_usd,
        education=request.has_high_education,
        children=request.has_children
    )
    logging.info(f"Estimated probability of default: {estimate}")
    
    inserted_id = insert_prediction(
        loan_usd=request.loan_usd,
        person_age=request.person_age,
        total_income_usd=request.total_income_usd,
        has_high_education=request.has_high_education,
        has_children=request.has_children,
        default_probability=estimate
    )
    logging.info(f"Prediction record inserted with id: {inserted_id}")
    
    return ScoringResponse(default_probability=estimate)

@app.get("/predictions")
def get_all_predictions_endpoint():
    predictions = read_all_predictions()
    return {"predictions": predictions}
