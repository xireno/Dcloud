import asyncio


async def retry_with_backoff(func, retries=3):
    """
    Retries a function with exponential backoff if it fails.
    """
    for attempt in range(retries):
        try:
            return await func()
        except Exception as e:
            if attempt < retries - 1:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
            else:
                raise e
