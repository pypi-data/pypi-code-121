from asyncio import iscoroutinefunction

from django.core.paginator import Page as BasePage
from django.core.paginator import Paginator as BasePaginator
from django.db.models import F, Q

__all__ = ["paginate"]


class Page(BasePage):
    async def output(self, render=lambda o: dict(id=o.pk)):

        rows = [
            render(await obj) if iscoroutinefunction(obj) else render(obj)
            for obj in self
        ]

        return (
            dict(
                page=self.number,
                limit=self.paginator.per_page,
                count=self.paginator.count,
                # order=request.data.get('order', None),
                rows=rows,
            )
            if hasattr(self, "paginator")
            else dict(
                page=1,
                limit=len(rows),
                count=len(rows),
                # order=request.data.get('order', None),
                rows=rows,
            )
        )


class Paginator(BasePaginator):
    def _get_page(self, *args, **kwargs):
        return Page(*args, **kwargs)


async def paginate(qs, data={}, output=lambda o: dict(id=o.pk), page=1, limit=25):

    try:
        page = int(data.get("page", page))
    except (KeyError, ValueError, TypeError) as e:
        page = 1

    try:
        limit = max(1, min(200, int(data.get("limit", limit))))
    except (KeyError, ValueError, TypeError) as e:
        limit = 25

    paginator = Paginator(qs, limit)
    return paginator.get_page(page)
