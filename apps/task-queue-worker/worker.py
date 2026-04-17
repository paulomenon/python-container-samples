import time


def simulate_task(seconds: float) -> dict:
    """Background job: simulated work with sleep."""
    time.sleep(float(seconds))
    return {"status": "finished", "slept_seconds": float(seconds)}
