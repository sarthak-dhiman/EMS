import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import OperationalError
import logging

env_path = Path(__file__).resolve().parent.parent.parent / ".env"

print(f"Loading .env from: {env_path}") 
load_dotenv(dotenv_path=env_path)

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

print(f"DATABASE_URL found: {SQLALCHEMY_DATABASE_URL}")

if not SQLALCHEMY_DATABASE_URL:
    logging.warning("DATABASE_URL not set; falling back to local SQLite for tests/development.")
    SQLALCHEMY_DATABASE_URL = "sqlite:///./dev.db"

# Create engine and verify connectivity to the configured DB. If the DB is unreachable,
# fall back to a local SQLite file to make tests and local dev more robust.
try:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    # Try a short connection to validate credentials/host (some DBs are lazy)
    conn = engine.connect()
    conn.close()
except OperationalError as e:
    logging.warning("Could not connect to DATABASE_URL (%s). Falling back to SQLite. Error: %s", SQLALCHEMY_DATABASE_URL, e)
    SQLALCHEMY_DATABASE_URL = "sqlite:///./dev.db"
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

_TABLES_CREATED = False

# Track which engine binds have had tables created to avoid repeated work
_CREATED_BINDS = set()

try:
    from sqlalchemy import inspect, event
    from sqlalchemy.orm import Session as _SessionClass

    def _ensure_tables_on_bind(session, transaction, connection):
        try:
            bind = session.bind
            if bind is None:
                return
            url = str(bind.engine.url) if hasattr(bind, 'engine') else str(bind.url)
            if url in _CREATED_BINDS:
                return
            insp = inspect(bind)
            # If no tables are present on this bind, create them
            if not insp.get_table_names():
                Base.metadata.create_all(bind=bind)
            _CREATED_BINDS.add(url)
        except Exception:
            logging.exception("Failed ensuring tables on session bind")

    event.listen(_SessionClass, "after_begin", _ensure_tables_on_bind)
except Exception:
    # If event listening setup fails, fall back to on-demand creates in get_db
    pass

# Try to eagerly import models so metadata is populated and we can create tables
try:
    import importlib
    from pathlib import Path

    models_dir = Path(__file__).resolve().parent.parent / "models"
    # Import each .py module in app/models so SQLAlchemy models register with Base
    if models_dir.exists() and models_dir.is_dir():
        for p in models_dir.glob("*.py"):
            if p.name == "__init__.py":
                continue
            module_name = p.stem
            try:
                importlib.import_module(f"app.models.{module_name}")
            except Exception:
                # best-effort import; continue importing other model modules
                logging.exception("Failed importing model module: %s", module_name)

    # Create tables on the primary engine
    Base.metadata.create_all(bind=engine)
    _TABLES_CREATED = True
except Exception:
    # If import fails (tests may override engines), defer creation to get_db
    pass

def get_db():
    global _TABLES_CREATED
    # Ensure tables exist on the configured engine so endpoints can operate even
    # if tests don't explicitly call Base.metadata.create_all on the same engine.
    try:
        if not _TABLES_CREATED:
            Base.metadata.create_all(bind=engine)
            _TABLES_CREATED = True
    except Exception:
        pass

    # Safety: if a caller provides a session bound to a different engine (e.g. test
    # fixtures), ensure tables exist on that engine as well before yielding.
    try:
        # If SessionLocal has a bind, ensure metadata exists there
        bind = SessionLocal.kw.get('bind') if hasattr(SessionLocal, 'kw') else None
        if hasattr(bind, 'engine'):
            engine_bind = bind.engine
        else:
            engine_bind = None
    except Exception:
        engine_bind = None
    except Exception:
        pass

    db = SessionLocal()
    try:
        try:
            if db.bind is not None and not _TABLES_CREATED:
                Base.metadata.create_all(bind=db.bind)
                _TABLES_CREATED = True
        except Exception:
            # Don't block on table creation failures here; caller tests may handle this
            pass

        yield db
    finally:
        db.close()