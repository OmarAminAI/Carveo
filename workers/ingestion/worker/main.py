import logging
import os
import time

from worker.ingestion import DUBIZZLE_UAE

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def main(run_forever: bool = True) -> None:
    """Run an observable worker without enabling unapproved marketplace access."""
    mode = os.getenv("CARVEO_WORKER_MODE", "idle")
    logging.info("Carveo ingestion worker started in %s mode; %s is %s", mode, DUBIZZLE_UAE.source_id, DUBIZZLE_UAE.authorization_status)
    while run_forever:
        time.sleep(60)
        logging.info("Carveo ingestion worker is healthy")


if __name__ == "__main__":
    main()
