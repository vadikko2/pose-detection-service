import asyncio
import logging
from concurrent.futures import process

from consumer.adapters import consumer_application
from consumer.service import points_handler

logging.basicConfig(level="DEBUG")

logger = logging.getLogger("kafka-consumer")

logging.getLogger("aiokafka").setLevel("ERROR")
logging.getLogger("asyncio").setLevel("ERROR")

CONSUMERS_NUMBER = 16


async def on_message(key: consumer_application.Key, value: consumer_application.Value) -> None:
    logger.info(f"Handled message key={key}, value={value}")


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    consumer = consumer_application.ConsumerApplication(
        bootstrap_servers=["host.docker.internal:29092", "host.docker.internal:29093"],
        group_id="test-consumer",
    )

    logger.info("Starting consumer")
    with process.ProcessPoolExecutor(max_workers=CONSUMERS_NUMBER) as pool:
        for consumer_number in range(CONSUMERS_NUMBER):
            loop.create_task(
                consumer.start(
                    consumer_name=f"consumer-{consumer_number + 1}",
                    topics=["test-kafka"],
                    handler=points_handler.PointsHandler(
                        pool_executor=process.ProcessPoolExecutor(max_workers=CONSUMERS_NUMBER),
                    ),
                    loop=loop,
                ),
            )

        loop.run_forever()
