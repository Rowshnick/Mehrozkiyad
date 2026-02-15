# handlers/__init__.py

from .start import router as start_router
from .sajil_handlers import router as sajil_router
from .symbol_handlers import router as symbol_router
from .symbol_inline import router as symbol_inline_router
from .natal_fsm import router as natal_router
from .transits import router as transits_router

all_routers = [
    start_router,
    sajil_router,
    symbol_router,
    symbol_inline_router,
    natal_router,
    transits_router,
]
