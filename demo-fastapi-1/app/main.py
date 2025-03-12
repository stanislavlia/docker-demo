from fastapi import FastAPI
from pydantic import BaseModel
from faker import Faker
import random

import logging

app = FastAPI()



faker = Faker()


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



#======================API SCHEMA FOR /predict============================

class ScoringFeaturesRequest(BaseModel):
    
    loan_usd: float
    person_age : int
    total_income_usd: float
    has_high_education: bool
    has_children : bool
    

class ScoringResponse(BaseModel):
    default_probability: float


#=========================ENDPOINTS=========================

@app.get("/")
def root():
    return {"message": "app is running",
            "status" : "healthy"}


@app.get("/user")
def get_random_user():

    name = faker.name()
    surname = faker.last_name()
    address = faker.address()
    email = faker.email()
    bod = faker.date_of_birth()
    ip_addr = faker.ipv4_public()

    logging.info(f"Generated user: {name} {surname}")

    return {"name" : name,
            "lastname" : surname,
            "address" : address,
            "email" : email,
            "date_of_birth" : bod.isoformat(),
            "ip_addr" : ip_addr}



@app.post("/predict")
def estimate_credit_scoring(request: ScoringFeaturesRequest):

    #call model
    estimate = decision_tree_ml_model(age=request.person_age,
                                      loan=request.loan_usd,
                                      income=request.person_age,
                                      education=request.has_high_education,
                                      children=request.has_children)
    
    logging.info(f"Estimated probability of default: {estimate}")
    
    return ScoringResponse(default_probability=estimate)