from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional
import uuid

# Prevent circular dependency
if TYPE_CHECKING:
    from jetpack.core._jetpack_function_with_client import JetpackFunctionWithClient


class Task:
    def __init__(
        self,
        jetpack_function: JetpackFunctionWithClient[Any],
        parent_task_id: str,
        with_checkpointing: bool,
        target_time: int,
        is_scheduled: bool,
    ):
        self.jetpack_function = jetpack_function
        self.parent_task_id = parent_task_id
        self.with_checkpointing = with_checkpointing
        self.target_time = target_time
        self.id: Optional[uuid.UUID] = None
        self.is_scheduled = is_scheduled

    def symbol_name(self) -> str:
        return self.jetpack_function.name()

    async def cancel(self) -> bool:
        return await self.jetpack_function.client.cancel_task(str(self.id))
