"""Worker: pop URLs from Redis, fetch pages, store title and HTTP status."""
import json
import logging
import os
import re

import redis
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("scraper-worker")

REDIS_URL = os.environ.get("REDIS_URL", "redis://127.0.0.1:6379/0")
QUEUE_KEY = "scraper:url_queue"
RESULTS_KEY = "scraper:results"


def extract_title(html: str) -> str | None:
    m = re.search(r"<title[^>]*>([^<]*)</title>", html, re.IGNORECASE | re.DOTALL)
    if not m:
        return None
    return re.sub(r"\s+", " ", m.group(1)).strip() or None


def main() -> None:
    r = redis.from_url(REDIS_URL, decode_responses=True)
    log.info("Worker started; blocking on queue %s", QUEUE_KEY)
    while True:
        item = r.blpop(QUEUE_KEY, timeout=5)
        if item is None:
            continue
        _, payload = item
        try:
            data = json.loads(payload)
            url = data["url"]
            job_id = data.get("job_id", "")
        except (json.JSONDecodeError, KeyError):
            log.warning("Bad queue payload: %s", payload)
            continue
        result_key = f"{job_id}:{url}" if job_id else url
        try:
            resp = requests.get(url, timeout=15, headers={"User-Agent": "distributed-web-scraper/1.0"})
            title = extract_title(resp.text) if resp.text else None
            record = {
                "url": url,
                "job_id": job_id,
                "status_code": resp.status_code,
                "title": title,
            }
        except requests.RequestException as e:
            record = {"url": url, "job_id": job_id, "status_code": None, "title": None, "error": str(e)}
        r.hset(RESULTS_KEY, result_key, json.dumps(record))
        log.info("scraped %s -> %s", url, record.get("status_code"))


if __name__ == "__main__":
    main()
