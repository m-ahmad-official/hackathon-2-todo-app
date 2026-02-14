"""
Performance benchmarking and load testing utilities
"""
import time
import asyncio
import httpx
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException
from src.core.logging import structured_logger

router = APIRouter()

class PerformanceBenchmark:
    """Performance benchmarking utilities"""

    @staticmethod
    async def benchmark_endpoint(endpoint: str, method: str = "GET",
                                headers: Optional[Dict[str, str]] = None,
                                data: Optional[Dict[str, Any]] = None,
                                auth_token: Optional[str] = None,
                                iterations: int = 100) -> Dict[str, Any]:
        """
        Benchmark a single API endpoint

        Args:
            endpoint: The API endpoint to benchmark
            method: HTTP method (GET, POST, PUT, DELETE)
            headers: Request headers
            data: Request payload
            auth_token: JWT token for authentication
            iterations: Number of requests to send

        Returns:
            Dictionary with benchmark results
        """
        results = {
            "endpoint": endpoint,
            "method": method,
            "iterations": iterations,
            "total_time_ms": 0,
            "average_time_ms": 0,
            "min_time_ms": float('inf'),
            "max_time_ms": 0,
            "success_count": 0,
            "error_count": 0,
            "response_times": [],
            "status_codes": {},
            "errors": []
        }

        headers = headers or {}
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"

        async with httpx.AsyncClient() as client:
            tasks = []

            for i in range(iterations):
                tasks.append(
                    PerformanceBenchmark._make_request(
                        client, endpoint, method, headers, data, results
                    )
                )

            await asyncio.gather(*tasks)

        # Calculate final metrics
        if results["response_times"]:
            results["average_time_ms"] = sum(results["response_times"]) / len(results["response_times"])
            results["min_time_ms"] = min(results["response_times"])
            results["max_time_ms"] = max(results["response_times"])

        return results

    @staticmethod
    async def _make_request(client: httpx.AsyncClient, endpoint: str, method: str,
                          headers: Dict[str, str], data: Optional[Dict[str, Any]],
                          results: Dict[str, Any]) -> None:
        """Make a single HTTP request and record metrics"""
        start_time = time.time()

        try:
            if method.upper() == "GET":
                response = await client.get(endpoint, headers=headers)
            elif method.upper() == "POST":
                response = await client.post(endpoint, json=data, headers=headers)
            elif method.upper() == "PUT":
                response = await client.put(endpoint, json=data, headers=headers)
            elif method.upper() == "DELETE":
                response = await client.delete(endpoint, headers=headers)
            else:
                results["errors"].append(f"Unsupported method: {method}")
                return

            execution_time = (time.time() - start_time) * 1000
            results["response_times"].append(execution_time)
            results["total_time_ms"] += execution_time

            # Record status code
            status_code = response.status_code
            results["status_codes"][status_code] = results["status_codes"].get(status_code, 0) + 1

            if 200 <= status_code < 300:
                results["success_count"] += 1
            else:
                results["error_count"] += 1
                results["errors"].append({
                    "status_code": status_code,
                    "response": response.text[:200]  # Truncate response
                })

        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            results["response_times"].append(execution_time)
            results["total_time_ms"] += execution_time
            results["error_count"] += 1
            results["errors"].append(str(e))

    @staticmethod
    async def load_test(endpoints: List[Dict[str, Any]], concurrency: int = 10,
                       duration: int = 60) -> Dict[str, Any]:
        """
        Perform load testing on multiple endpoints

        Args:
            endpoints: List of endpoint configurations
            concurrency: Number of concurrent requests
            duration: Duration of the load test in seconds

        Returns:
            Dictionary with load test results
        """
        results = {
            "test_duration": duration,
            "concurrency": concurrency,
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_response_time_ms": 0,
            "min_response_time_ms": float('inf'),
            "max_response_time_ms": 0,
            "endpoint_stats": {},
            "errors": []
        }

        async def worker(endpoint_config: Dict[str, Any]):
            """Worker function for load testing"""
            client = httpx.AsyncClient()
            try:
                while time.time() - start_time < duration:
                    await PerformanceBenchmark._make_request(
                        client,
                        endpoint_config["endpoint"],
                        endpoint_config["method"],
                        endpoint_config.get("headers", {}),
                        endpoint_config.get("data", None),
                        results
                    )
                    await asyncio.sleep(0.01)  # Small delay to avoid overwhelming
            finally:
                await client.aclose()

        # Start load test
        start_time = time.time()
        tasks = []

        for _ in range(concurrency):
            for endpoint in endpoints:
                tasks.append(worker(endpoint))

        await asyncio.gather(*tasks)

        # Calculate final metrics
        if results["total_requests"] > 0:
            results["average_response_time_ms"] = (
                sum(results["response_times"]) / results["total_requests"]
                if results["response_times"] else 0
            )
            results["min_response_time_ms"] = min(results["response_times"]) if results["response_times"] else 0
            results["max_response_time_ms"] = max(results["response_times"]) if results["response_times"] else 0

        return results

class BenchmarkMiddleware:
    """Middleware to automatically benchmark endpoints"""

    def __init__(self, benchmark_config: Dict[str, Any]):
        self.benchmark_config = benchmark_config
        self.benchmarks = {}

    async def __call__(self, request: Request, call_next: Callable) -> Response:
        endpoint = request.url.path

        # Check if this endpoint should be benchmarked
        if endpoint in self.benchmark_config:
            benchmark = self.benchmark_config[endpoint]
            if benchmark.get("enabled", False):
                return await self._benchmark_request(request, call_next, endpoint, benchmark)

        return await call_next(request)

    async def _benchmark_request(self, request: Request, call_next: Callable,
                                endpoint: str, benchmark: Dict[str, Any]) -> Response:
        """Benchmark a single request"""
        start_time = time.time()
        user_id = request.headers.get("X-User-Id", "unknown")

        try:
            response = await call_next(request)
        except Exception as e:
            # Log benchmark error
            structured_logger.log_metric(
                "benchmark_error",
                1,
                {
                    "endpoint": endpoint,
                    "user_id": user_id,
                    "error": str(e)
                }
            )
            raise

        # Calculate metrics
        execution_time_ms = (time.time() - start_time) * 1000
        status_code = response.status_code

        # Log benchmark metrics
        structured_logger.log_metric(
            "endpoint_benchmark",
            execution_time_ms,
            {
                "endpoint": endpoint,
                "method": request.method,
                "status_code": status_code,
                "user_id": user_id,
                "benchmark_name": benchmark.get("name", "default")
            }
        )

        return response

@router.post("/benchmark/endpoint")
async def benchmark_single_endpoint(benchmark_request: Dict[str, Any]) -> Dict[str, Any]:
    """Endpoint to benchmark a single API endpoint"""
    try:
        # Validate input
        required_fields = ["endpoint", "method"]
        for field in required_fields:
            if field not in benchmark_request:
                raise HTTPException(
                    status_code=400,
                    detail=f"Missing required field: {field}"
                )

        # Extract benchmark parameters
        endpoint = benchmark_request["endpoint"]
        method = benchmark_request["method"]
        headers = benchmark_request.get("headers", {})
        data = benchmark_request.get("data", None)
        auth_token = benchmark_request.get("auth_token", None)
        iterations = benchmark_request.get("iterations", 100)

        # Run benchmark
        result = await PerformanceBenchmark.benchmark_endpoint(
            endpoint, method, headers, data, auth_token, iterations
        )

        # Log benchmark result
        structured_logger.log_metric(
            "benchmark_completed",
            1,
            {
                "endpoint": endpoint,
                "iterations": iterations,
                "success_rate": result["success_count"] / iterations if iterations > 0 else 0
            }
        )

        return result

    except Exception as e:
        structured_logger.log_error(e, None, "benchmark")
        raise HTTPException(
            status_code=500,
            detail=f"Benchmark failed: {str(e)}"
        )

@router.post("/benchmark/load")
async def load_test_endpoint(load_test_request: Dict[str, Any]) -> Dict[str, Any]:
    """Endpoint to perform load testing"""
    try:
        # Validate input
        required_fields = ["endpoints", "concurrency", "duration"]
        for field in required_fields:
            if field not in load_test_request:
                raise HTTPException(
                    status_code=400,
                    detail=f"Missing required field: {field}"
                )

        # Extract load test parameters
        endpoints = load_test_request["endpoints"]
        concurrency = load_test_request["concurrency"]
        duration = load_test_request["duration"]

        # Run load test
        result = await PerformanceBenchmark.load_test(endpoints, concurrency, duration)

        # Log load test completion
        structured_logger.log_metric(
            "load_test_completed",
            1,
            {
                "endpoints_count": len(endpoints),
                "concurrency": concurrency,
                "duration": duration
            }
        )

        return result

    except Exception as e:
        structured_logger.log_error(e, None, "load_test")
        raise HTTPException(
            status_code=500,
            detail=f"Load test failed: {str(e)}"
        )

@router.get("/benchmark/health")
async def benchmark_health_check() -> Dict[str, Any]:
    """Health check for benchmarking system"""
    try:
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "benchmark_system": "operational",
            "version": "1.0.0"
        }
    except Exception as e:
        structured_logger.log_error(e, None, "benchmark_health")
        raise HTTPException(
            status_code=503,
            detail="Benchmark system unavailable"
        )