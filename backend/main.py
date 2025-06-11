from fastapi import FastAPI, Request, Response, HTTPException, Form
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

@app.options("/auth/login")
async def login_options():
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Credentials": "true",
        }
    )

@app.post("/auth/login")
async def login(request: Request):
    print(f"Login request received")
    
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
    
    demo_username = "admin@cardioai.pro"
    demo_password = "admin123"
    
    if username == demo_username and password == demo_password:
        response_data = {
            "access_token": "demo_token_12345",
            "token_type": "bearer",
            "user": {"username": demo_username, "role": "admin"}
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
