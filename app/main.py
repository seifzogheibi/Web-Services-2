from fastapi import FastAPI

app = FastAPI(
    title="Nutrition API",
    version="1.0.0",
    description="REST API for foods, meals, and nutrition analytics.",
)

@app.get("/test")
def test():
    return {"status": "okay"}