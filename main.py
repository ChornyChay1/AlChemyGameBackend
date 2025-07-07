from fastapi import FastAPI
from DB import SessionLocal
from user import router as user_router
from adventure import router as adventure_router
from topic import router as topic_router
from files import router as file_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Подключение маршрутов
app.include_router(user_router)
app.include_router(adventure_router)
app.include_router(topic_router)
app.include_router(file_router)
# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

if __name__ == "__main__":
    import asyncio
    import hypercorn.asyncio
    from hypercorn.config import Config
    import os
    
    os.makedirs("Data/files", exist_ok=True)
    os.makedirs("temp_files", exist_ok=True)
    config = Config()
    config.bind = ["127.0.0.1:8000"] 
    asyncio.run(hypercorn.asyncio.serve(app, config))

