import logging

from sqlmodel import Session

from app.core.db import engine, init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init() -> None:
    logger.error(">>> Entering init()", extra={"event.action": "init"})
    with Session(engine) as session:
        init_db(session)
        logger.warning("<<< Exiting init()", extra={"event.action": "init"})


def main() -> None:
    logger.error(">>> Entering main()", extra={"event.action": "main"})
    logger.info("Creating initial data")
    init()
    logger.info("Initial data created")
    logger.warning("<<< Exiting main()", extra={"event.action": "main"})


if __name__ == "__main__":
    main()
