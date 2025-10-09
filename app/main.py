from fastapi import FastAPI
from .routes import product_routes, order_routes, user_routes, agent_routes
from app.db.database import engine
from sqlmodel import SQLModel

app = FastAPI(title="Orders & Inventory Service")

SQLModel.metadata.create_all(engine)

# Include routers
app.include_router(product_routes.router)
app.include_router(order_routes.router)
app.include_router(user_routes.router)
app.include_router(agent_routes.router)



# Root endpoint
@app.get("/")
def root():
    return {"message": "Welcome to Orders & Inventory Service"}