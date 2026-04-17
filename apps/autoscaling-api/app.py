"""FastAPI service with a CPU-heavy endpoint for HPA / load testing."""
import os
import time

from fastapi import FastAPI, Query

app = FastAPI(title="Autoscaling CPU Demo")

MOD = 10**9 + 7


def fibonacci_mod(n: int) -> int:
    """Iterative Fibonacci F(n) modulo MOD; O(n) CPU, O(1) memory."""
    if n < 0:
        raise ValueError("n must be non-negative")
    a, b = 0, 1
    for _ in range(n):
        a, b = b % MOD, (a + b) % MOD
    return a


@app.get("/")
def root():
    return {
        "service": "autoscaling-api",
        "endpoints": {
            "/": "This page",
            "/compute": "CPU-intensive Fibonacci-style work (?n=)",
            "/health": "Liveness/readiness",
        },
        "fib_note": "GET /compute returns F(n) mod 1000000007 using an O(n) loop (suitable for large n).",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/compute")
def compute(n: int = Query(100_000, ge=0, le=2_000_000)):
    """Burn CPU roughly linear in n (for Kubernetes HPA demos)."""
    start = time.perf_counter()
    result = fibonacci_mod(n)
    elapsed = time.perf_counter() - start
    return {"n": n, "result": result, "mod": MOD, "seconds": round(elapsed, 4)}


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
