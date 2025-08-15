"""
Simple task throttling utility to limit background task execution rate.
Ensures tasks are executed at a rate of one per minute, even when multiple
tasks are queued simultaneously.
"""
import time
import asyncio
from loguru import logger
from typing import Callable, Any

# Global variables
_last_task_time = 0
_throttle_lock = asyncio.Lock()  # Lock to ensure only one task proceeds at a time

async def throttled_task(func: Callable, *args, **kwargs) -> Any:
    """
    Executes the given function with its arguments, ensuring that executions
    are at least 60 seconds apart, even when multiple tasks are queued.
    
    Uses an async lock to ensure that only one task proceeds through the
    throttling gate at a time, preventing race conditions where multiple
    tasks would execute simultaneously.
    
    Args:
        func: The async function to execute
        *args: Arguments to pass to func
        **kwargs: Keyword arguments to pass to func
        
    Returns:
        The result of func(*args, **kwargs)
    """
    global _last_task_time
    
    # Acquire the lock - this ensures only one task at a time can check and update _last_task_time
    async with _throttle_lock:
        current_time = time.time()
        
        # Calculate time to wait (if any)
        if current_time - _last_task_time < 60:
            wait_seconds = 60 - (current_time - _last_task_time)
            logger.info(f"Throttling task, waiting {wait_seconds:.2f} seconds...")
            
            # Sleep while holding the lock - critical to prevent race conditions
            await asyncio.sleep(wait_seconds)
        
        # Update last task time BEFORE releasing the lock
        _last_task_time = time.time()
        task_start_time = _last_task_time
        logger.info(f"Starting throttled task at {time.strftime('%H:%M:%S', time.localtime(task_start_time))}")
    
    # Execute the function outside the lock to allow the next task to start its waiting period
    return await func(*args, **kwargs)
