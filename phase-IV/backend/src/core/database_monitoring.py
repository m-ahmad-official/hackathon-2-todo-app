"""
Database performance monitoring utilities
"""
import time
from typing import Any, Callable
from contextlib import contextmanager
from src.core.logging import structured_logger
from src.core.database import get_session
from sqlmodel import Session

@contextmanager
def monitor_database_query(user_id: str = "unknown"):
    """Context manager to monitor database query performance"""
    start_time = time.time()
    try:
        yield
    finally:
        execution_time_ms = (time.time() - start_time) * 1000

        # Log the database query performance
        structured_logger.log_database_query(
            "DATABASE_QUERY_EXECUTED",
            execution_time_ms,
            user_id
        )

        # Log performance metric
        structured_logger.log_metric(
            "database_query_execution_time",
            execution_time_ms,
            {
                "user_id": user_id,
                "status": "completed"
            }
        )

        # Alert if query is too slow
        if execution_time_ms > 500:  # 500ms threshold
            structured_logger.log_metric(
                "slow_database_query",
                execution_time_ms,
                {
                    "user_id": user_id,
                    "threshold": 500
                }
            )

def monitor_query_execution(user_id: str = "unknown"):
    """Decorator to monitor query execution time"""
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs) -> Any:
            with monitor_database_query(user_id):
                return func(*args, **kwargs)
        return wrapper
    return decorator

class DatabasePerformanceMonitor:
    """Class to monitor and analyze database performance"""

    def __init__(self):
        self.query_stats = {}
        self.slow_queries = []

    def record_query(self, query: str, execution_time_ms: float, user_id: str = "unknown"):
        """Record query execution statistics"""
        if query not in self.query_stats:
            self.query_stats[query] = {
                "total_time": 0,
                "count": 0,
                "max_time": 0,
                "min_time": float('inf'),
                "user_ids": set()
            }

        stats = self.query_stats[query]
        stats["total_time"] += execution_time_ms
        stats["count"] += 1
        stats["max_time"] = max(stats["max_time"], execution_time_ms)
        stats["min_time"] = min(stats["min_time"], execution_time_ms)
        stats["user_ids"].add(user_id)

        # Check if query is slow
        if execution_time_ms > 1000:  # 1 second threshold
            self.slow_queries.append({
                "query": query[:200],  # Truncate long queries
                "execution_time_ms": execution_time_ms,
                "user_id": user_id,
                "timestamp": time.time()
            })

    def get_query_statistics(self) -> dict:
        """Get aggregated query statistics"""
        stats = {}
        for query, data in self.query_stats.items():
            stats[query] = {
                "average_time_ms": data["total_time"] / data["count"],
                "total_time_ms": data["total_time"],
                "execution_count": data["count"],
                "max_time_ms": data["max_time"],
                "min_time_ms": data["min_time"],
                "unique_users": len(data["user_ids"])
            }
        return stats

    def get_slow_queries(self, limit: int = 10) -> list:
        """Get the slowest queries"""
        return sorted(self.slow_queries, key=lambda x: x["execution_time_ms"], reverse=True)[:limit]

# Global database performance monitor
database_performance_monitor = DatabasePerformanceMonitor()

class QueryPerformanceContext:
    """Context manager for query performance monitoring"""

    def __init__(self, query: str, user_id: str = "unknown"):
        self.query = query
        self.user_id = user_id
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            execution_time_ms = (time.time() - self.start_time) * 1000

            # Log the query performance
            structured_logger.log_database_query(
                self.query,
                execution_time_ms,
                self.user_id
            )

            # Record statistics
            database_performance_monitor.record_query(
                self.query,
                execution_time_ms,
                self.user_id
            )


def execute_monitored_query(query_func: Callable, user_id: str = "unknown") -> Any:
    """Execute a database query with performance monitoring"""
    with QueryPerformanceContext("EXECUTED_QUERY", user_id):
        return query_func()