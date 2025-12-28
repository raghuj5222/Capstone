# async_utils.py

import asyncio

def run_async(coro):
    """
    Run an async coroutine from synchronous code (e.g., Streamlit).
    """
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    if loop.is_running():
        # Streamlit sometimes runs inside an event loop
        return asyncio.run(coro)
    else:
        return loop.run_until_complete(coro)
