from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import colorama
from colorama import Fore, Style
from .database import engine, Base
from .routers import policies as policies_router, portfolio as portfolio_router, quotes as quotes_router
from .core.middleware import RateLimitMiddleware
from .core.settings import settings

# Initialize colorama for proper Windows console colors
colorama.init(autoreset=True)

# Custom formatter for better log colors
class ColoredFormatter(logging.Formatter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def format(self, record):
        # Apply colors based on log level
        if record.levelno == logging.DEBUG:
            color = Fore.CYAN
        elif record.levelno == logging.INFO:
            color = Fore.GREEN  # INFO logs should be green, not red
        elif record.levelno == logging.WARNING:
            color = Fore.YELLOW
        elif record.levelno == logging.ERROR:
            color = Fore.RED
        elif record.levelno == logging.CRITICAL:
            color = Fore.MAGENTA
        else:
            color = Style.RESET_ALL
            
        # Format the message with color
        formatted = super().format(record)
        return f"{color}{formatted}{Style.RESET_ALL}"

# Configure logging with proper colors
def setup_logging():
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create colored formatter
    formatter = ColoredFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Clear existing handlers and add our colored handler
    root_logger.handlers.clear()
    root_logger.addHandler(console_handler)
    
    # Disable uvicorn's default colored logging to avoid conflicts
    logging.getLogger("uvicorn.access").handlers.clear()
    logging.getLogger("uvicorn").handlers.clear()

# Setup logging
setup_logging()

# Alembic is used for migrations, do not call Base.metadata.create_all here in production
app = FastAPI(title="Insurance Advisor V6", root_path=settings.BASE_PATH)

app.add_middleware(RateLimitMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(policies_router.router)
app.include_router(portfolio_router.router)
app.include_router(quotes_router.router)