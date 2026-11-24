import logging

from sqlalchemy import text

from backend.app.database.session import SessionLocal
from backend.app.services.cleanup_service import cleanup_database


logging.basicConfig(level=logging.INFO)

logger = logging.getLogger("tone_neuron.maintenance")


def main():

    with SessionLocal() as db:

        acquired = db.scalar(
            text("SELECT pg_try_advisory_xact_lock(7241001)")
        )

        if not acquired:
            logger.info("Another cleanup job is running.")
            return

        result = cleanup_database(db)

        logger.info(
            "Database cleanup completed: %s",
            result.model_dump_json(),
        )


if __name__ == "__main__":
    main()
