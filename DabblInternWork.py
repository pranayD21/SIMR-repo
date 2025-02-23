import threading
import time
import os, sys
from db.notification_handler import NotificationHandler
from fastapi import FastAPI, HTTPException, Request
import db.services, ai.services, auth.services, webhooks.services, analytics.services
from fastapi.responses import JSONResponse
from utils import wrap_response
from logger import log_trace, logging

app = FastAPI()

# Middleware to wrap responses in a format the UI expects it
@app.middleware("http")
async def wrap_response(request: Request, call_next):
    response = await call_next(request)

    if isinstance(response, JSONResponse):
        # Wrap the JSON response
        content = response.body.decode()
        wrapped_content = {"data": content, "status": "success"}
        return JSONResponse(content=wrapped_content, status_code=response.status_code)
    return response

# Standardized middleware to handle error responses from REST APIs
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.status_code,
                "message": exc.detail,
            }
        }
    )

# Middleware to wrap responses in a format the UI expects it
@app.middleware("http")
async def wrap_response(request: Request, call_next):
    response = await call_next(request)
    
    if isinstance(response, JSONResponse):
        # Wrap the JSON response
        content = response.body.decode()
        wrapped_content = {"data": content, "status": "success"}
        return JSONResponse(content=wrapped_content, status_code=response.status_code)
    return response

# Standardized middleware to handle error responses from REST APIs
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.status_code,
                "message": exc.detail,
            }
        }
    )

app.include_router(db.services.router)
app.include_router(ai.services.router)
app.include_router(auth.services.router)
app.include_router(webhooks.services.router)
app.include_router(analytics.services.router)

# app.include_router(
#     admin.router,
#     responses={418: {"description": "I'm a teapot"}},
# )

# Background task to process scheduled notifications
def process_scheduled_notifications(db_session_maker):
    """
    Background task to send notifications when send_time <= current time.
    """
    while True:
        try:
            # Create a new DB session for this thread
            db = db_session_maker()

            # Create an instance of the NotificationHandler
            notification_handler = NotificationHandler()

            # Send notifications that are due (where send_time <= current time)
            notification_handler.send_scheduled_notifications(db)

        except Exception as e:
            print(f"Error processing notifications: {e}")
        finally:
            # Close the database session to avoid memory leaks
            db.close()

        # Sleep for a while before checking again (e.g., check every 60 seconds)
        time.sleep(60)

# Start the background thread when the FastAPI application starts
@app.on_event("startup")
def startup_event():
    # Start the thread for processing scheduled notifications
    thread = threading.Thread(target=process_scheduled_notifications, args=(db.database.SessionLocal,))
    thread.daemon = True  # Daemon thread will stop when the main program exits
    thread.start()

@app.get("/")
async def root():
    log_trace(logging.INFO, "Request received for root endpoint")
    return {"message": "Hello Dabbl Backend!"}

# @app.exception_handler(Exception)
# async def universal_exception_handler(request: Request, exc: Exception):
#     return JSONResponse(
#         status_code=500,
#         content=wrap_response(data=None, message="An internal error occurred", code=500, error=str(exc))
#     )
