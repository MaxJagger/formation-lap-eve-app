from fastapi import FastAPI

app = FastAPI()

@app.get("/users")
def get_users():
    return {
        "service": "user-service",
        "users": [
            {"id": 1, "name": "eve"},
            {"id": 2, "name": "lap"}
        ]
    }

