"""
Health check and system monitoring endpoints
"""
import time
import psutil
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from src.core.logging import structured_logger
from src.core.database import get_session
from sqlmodel import Session

router = APIRouter()

class SystemMonitor:
    """System monitoring utilities"""

    @staticmethod
    def get_system_metrics() -> Dict[str, Any]:
        """Get system performance metrics"""
        try:
            metrics = {
                "timestamp": time.time(),
                "cpu": {
                    "percent": psutil.cpu_percent(interval=0.1),
                    "count": psutil.cpu_count(),
                    "freq": psutil.cpu_freq().current if psutil.cpu_freq() else None
                },
                "memory": {
                    "percent": psutil.virtual_memory().percent,
                    "available": psutil.virtual_memory().available,
                    "used": psutil.virtual_memory().used,
                    "total": psutil.virtual_memory().total
                },
                "disk": {
                    "percent": psutil.disk_usage("/").percent,
                    "free": psutil.disk_usage("/").free,
                    "used": psutil.disk_usage("/").used,
                    "total": psutil.disk_usage("/").total
                },
                "network": {
                    "bytes_sent": psutil.net_io_counters().bytes_sent,
                    "bytes_recv": psutil.net_io_counters().bytes_recv,
                    "packets_sent": psutil.net_io_counters().packets_sent,
                    "packets_recv": psutil.net_io_counters().packets_recv
                },
                "load": {
                    "1m": os.getloadavg()[0] if hasattr(os, 'getloadavg') else None,
                    "5m": os.getloadavg()[1] if hasattr(os, 'getloadavg') else None,
                    "15m": os.getloadavg()[2] if hasattr(os, 'getloadavg') else None
                }
            }

            # Log system metrics
            structured_logger.log_metric("system_metrics_collected", 1, {"source": "health_check"})

            return metrics
        except Exception as e:
            structured_logger.log_error(e, None, "system_monitor")
            return {"error": str(e)}

    @staticmethod
    def get_database_status(session: Session) -> Dict[str, Any]:
        """Check database connection and status"""
        try:
            start_time = time.time()

            # Test database connection
            session.execute("SELECT 1")
            session.commit()

            execution_time = (time.time() - start_time) * 1000

            return {
                "status": "healthy",
                "connection_time_ms": execution_time,
                "version": session.execute("SELECT version()").fetchone()[0],
                "connection_pool": "active"
            }
        except Exception as e:
            structured_logger.log_error(e, None, "database_monitor")
            return {
                "status": "unhealthy",
                "error": str(e)
            }

    @staticmethod
    def get_cache_status() -> Dict[str, Any]:
        """Check cache status (Redis)"""
        try:
            import redis
            r = redis.Redis(host="localhost", port=6379, db=0)
            r.ping()

            return {
                "status": "healthy",
                "redis_version": r.info("server").get("redis_version", "unknown"),
                "connected_clients": r.info("clients").get("connected_clients", 0),
                "used_memory": r.info("memory").get("used_memory_human", "unknown")
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Comprehensive health check endpoint"""
    start_time = time.time()

    try:
        # Get database session
        session = get_session()

        # Collect system metrics
        system_metrics = SystemMonitor.get_system_metrics()

        # Check database status
        database_status = SystemMonitor.get_database_status(session)

        # Check cache status
        cache_status = SystemMonitor.get_cache_status()

        # Collect application metrics
        app_metrics = {
            "uptime": time.time() - start_time,
            "version": "1.0.0",
            "environment": "production" if not settings.DEBUG else "development",
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        }

        # Calculate response time
        response_time = (time.time() - start_time) * 1000

        # Log health check
        structured_logger.log_health_check("healthy", response_time)

        return {
            "status": "healthy",
            "timestamp": time.time(),
            "response_time_ms": response_time,
            "system": system_metrics,
            "database": database_status,
            "cache": cache_status,
            "application": app_metrics
        }

    except Exception as e:
        # Log error
        structured_logger.log_error(e, None, "health_check")
        structured_logger.log_health_check("unhealthy", (time.time() - start_time) * 1000)

        raise HTTPException(
            status_code=503,
            detail=f"Health check failed: {str(e)}"
        )

@router.get("/metrics")
async def get_metrics() -> Dict[str, Any]:
    """Get application metrics"""
    try:
        # Get database session
        session = get_session()

        # Collect system metrics
        system_metrics = SystemMonitor.get_system_metrics()

        # Get database status
        database_status = SystemMonitor.get_database_status(session)

        # Get cache status
        cache_status = SystemMonitor.get_cache_status()

        # Get usage statistics
        from src.core.rate_limiting import usage_tracker
        usage_stats = usage_tracker.get_usage_statistics()

        # Get database performance stats
        from src.core.database_monitoring import database_performance_monitor
        db_stats = {
            "query_stats": database_performance_monitor.get_query_statistics(),
            "slow_queries": database_performance_monitor.get_slow_queries()
        }

        return {
            "timestamp": time.time(),
            "system": system_metrics,
            "database": database_status,
            "cache": cache_status,
            "usage": usage_stats,
            "database_performance": db_stats
        }

    except Exception as e:
        structured_logger.log_error(e, None, "metrics")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get metrics: {str(e)}"
        )

@router.get("/status")
async def simple_status() -> Dict[str, Any]:
    """Simple status endpoint for load balancers"""
    try:
        # Quick database check
        session = get_session()
        session.execute("SELECT 1")
        session.commit()

        return {
            "status": "ok",
            "timestamp": time.time(),
            "version": "1.0.0"
        }
    except Exception as e:
        structured_logger.log_error(e, None, "status")
        raise HTTPException(
            status_code=503,
            detail="Service unavailable"
        )

@router.get("/config")
async def get_configuration() -> Dict[str, Any]:
    """Get application configuration (sanitized)"""
    try:
        config = {
            "environment": "production" if not settings.DEBUG else "development",
            "database_url": settings.DATABASE_URL if not settings.DEBUG else "sqlite:///./todo_app.db",
            "debug": settings.DEBUG,
            "version": "1.0.0"
        }

        return config
    except Exception as e:
        structured_logger.log_error(e, None, "config")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get configuration: {str(e)}"
        )