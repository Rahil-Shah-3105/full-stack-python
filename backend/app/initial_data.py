import logging

from sqlmodel import Session

from app.core.db import engine, init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init() -> None:
    logger.debug(">>> Entering init()")
    with Session(engine) as session:
        logger.error("Exception in init()", exc_info=True)
        init_db(session)
        logger.debug("<<< Exiting init()")


def main() -> None:
    logger.debug(">>> Entering main()")
    logger.info("Creating initial data")
    init()
    logger.info("Initial data created")
    logger.debug("<<< Exiting main()")


if __name__ == "__main__":
    main()
