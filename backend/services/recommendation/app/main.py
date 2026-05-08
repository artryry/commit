import asyncio
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")


async def _async_main() -> None:
    from db.session import init_db
    from kafka.runner import run_all
    from services.embedding_service import EmbeddingEncoder
    from services.profile_ingestion import ProfileIngestionService

    await init_db()
    embedding = EmbeddingEncoder()
    ingestion = ProfileIngestionService(embedding)
    logging.info("starting recommendation service (grpc + kafka)")
    await run_all(ingestion)


def main() -> None:
    asyncio.run(_async_main())


if __name__ == "__main__":
    main()
