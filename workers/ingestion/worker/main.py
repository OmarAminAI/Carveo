import logging
import os
import time

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def main(run_forever: bool = True) -> None:
    """Keep the worker process observable while ingestion adapters are not enabled."""
    mode = os.getenv("CARVEO_WORKER_MODE", "idle")
    logging.info("Carveo ingestion worker started in %s mode", mode)
    while run_forever:
        time.sleep(60)
        logging.info("Carveo ingestion worker is healthy")


if __name__ == "__main__":
    main()
