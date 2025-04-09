import logging

from sqlmodel import Session

from src.config.db import engine, init_db
from src.config.initial_permissions import create_initial_permissions, create_initial_roles

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init() -> None:
    with Session(engine) as session:
        init_db(session)
        create_initial_permissions(session)
        create_initial_roles(session)


def main() -> None:
    logger.info("Creando datos iniciales")
    init()
    logger.info("Datos iniciales creados")


if __name__ == "__main__":
    main()