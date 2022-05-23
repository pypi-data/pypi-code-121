
import asyncio
import pytest

@pytest.mark.asyncio
async def test_loop_helper():
    
    await asyncio.sleep(2)

    assert True