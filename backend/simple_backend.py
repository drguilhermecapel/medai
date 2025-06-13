import os

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI(title="SPEI Medical Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "SPEI Medical System API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "spei-medical-api"}

@app.post("/auth/login")
async def login(request: Request):
    print("Login request received")

    content_type = request.headers.get("content-type", "")

    if "application/json" in content_type:
        data = await request.json()
        username = data.get("username")
        password = data.get("password")
    else:
        form_data = await request.form()
        username = form_data.get("username")
        password = form_data.get("password")

    print(f"Login attempt: username={username}")

    demo_username_1 = os.getenv("DEMO_USERNAME_1")
    demo_password_1 = os.getenv("DEMO_PASSWORD_1")
    demo_username_2 = os.getenv("DEMO_USERNAME_2")
    demo_password_2 = os.getenv("DEMO_PASSWORD_2")

    if ((demo_username_1 and demo_password_1 and username == demo_username_1 and password == demo_password_1) or
        (demo_username_2 and demo_password_2 and username == demo_username_2 and password == demo_password_2)):
        response_data = {
            "access_token": "demo_token_12345",
            "token_type": "bearer",
            "user": {"username": username, "role": "admin"}
        }
        print("Login successful")
        response = JSONResponse(content=response_data)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
        response.headers["Access-Control-Allow-Credentials"] = "false"
        return response
    else:
        print("Login failed: Invalid credentials")
        raise HTTPException(status_code=401, detail="Invalid credentials")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
