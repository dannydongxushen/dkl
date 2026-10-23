# backend/main.py
import os
import sys
import socket
import subprocess
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api import router
from seeding.seed_sqlite import init_sqlite
from seeding.seed_chroma import init_chroma

def is_port_open(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(('127.0.0.1', port)) == 0

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Always run init functions; they contain logic to skip if data already exists
    print("\n--- Checking Database Status ---")
    init_sqlite()
    init_chroma()

    # Start Litefuse if not running
    litefuse_process = None
    if not is_port_open(23100):
        print("Starting Litefuse service...")
        try:
            subprocess.Popen(
                ["bash", os.path.expanduser("~/.litefuse/bin/start.sh")],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            print("Litefuse started in background.")
        except Exception as e:
            print(f"Failed to auto-start Litefuse: {e}")
    else:
        print("Litefuse is already running on port 23100.")
        
    yield
    
    if litefuse_process:
        print("Stopping Litefuse service...")
        litefuse_process.terminate()
        litefuse_process.wait()

app = FastAPI(
    title="ClinicPilot AI",
    description="AI-driven clinic assistant API",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")