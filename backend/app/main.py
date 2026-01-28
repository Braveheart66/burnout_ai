from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import BurnoutDatabase
from app.schemas import CheckoutRequest
from ml.predict import predict_burnout

app = FastAPI(title="Burnout AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

db = BurnoutDatabase()

@app.on_event("startup")
def startup():
    db.setup_database()

@app.post("/checkout")
def checkout(req: CheckoutRequest):
    score, label = predict_burnout(req.dict())
    db.save_checkout(
        req.email,
        req.department,
        req.dict(),
        score,
        label,
        req.reflection or ""
    )
    return {"score": score, "label": label}

@app.get("/dept/aggregates")
def dept(start: str, end: str):
    return db.department_aggregates(start, end).to_dict("records")

@app.get("/org/aggregates")
def org(start: str, end: str):
    return db.org_aggregates(start, end).to_dict("records")
