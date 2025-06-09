from fastapi import FastAPI

app = FastAPI(title="SPEI Medical EMR")

@app.get("/")
def read_root():
    return {"message": "SPEI Medical EMR API"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "SPEI Medical EMR Backend"}
