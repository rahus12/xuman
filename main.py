from fastapi import FastAPI
from controllers.services_controller import router as services_router
from controllers.bookings_controller import router as bookings_router
from controllers.users_controller import router as users_router
from controllers.auth_controller import router as auth_router
from controllers.email_controller import router as email_router
from controllers.password_reset_controller import router as password_reset_router
from controllers.payments_controller import router as payments_router
from controllers.notifications_controller import router as notifications_router
from rate_limiter import limiter, rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

import uvicorn
import os
from dotenv import load_dotenv

app = FastAPI(title="Service Marketplace API", version="1.0.0")

# Add rate limiting to the app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

@app.get("/")
async def root():
    return {"message": "Service Marketplace API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Include routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(services_router)
app.include_router(bookings_router)
app.include_router(email_router)
app.include_router(password_reset_router)
app.include_router(payments_router)
app.include_router(notifications_router)

if __name__ == "__main__":
    
    # Load environment variables
    load_dotenv()
    
    # Get host and port from environment variables
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    
    uvicorn.run(app, host=host, port=port)
