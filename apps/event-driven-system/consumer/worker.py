"""Subscribe to Redis ``events`` channel and log payloads."""
import json
import logging
import os

import redis

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("consumer")

REDIS_URL = os.environ.get("REDIS_URL", "redis://127.0.0.1:6379/0")
CHANNEL = "events"


def main() -> None:
    r = redis.from_url(REDIS_URL, decode_responses=True)
    pubsub = r.pubsub()
    pubsub.subscribe(CHANNEL)
    log.info("Subscribed to channel %r", CHANNEL)
    for message in pubsub.listen():
        if message["type"] != "message":
            continue
        raw = message["data"]
        try:
            parsed = json.loads(raw)
            log.info("event: %s", parsed)
        except json.JSONDecodeError:
            log.info("event (raw): %s", raw)


if __name__ == "__main__":
    main()
