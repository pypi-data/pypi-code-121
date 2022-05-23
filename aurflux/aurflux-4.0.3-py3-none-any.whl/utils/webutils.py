from __future__ import annotations

import typing as ty
import urllib.parse

if ty.TYPE_CHECKING:
   import aiohttp.client


async def haste(session: aiohttp.client.ClientSession, content: str):
   async with session.post("https://h.ze.ax/documents", data=content) as resp:
      r = await resp.json(content_type=None)
      return f"https://h.ze.ax/{r['key']}"


def copylink(to_copy: str, embed=True) -> str:
   link = f"https://x.ze.ax/copy?{urllib.parse.quote(to_copy)}"
   if embed:
      return f"[{to_copy}]({link})"
   else:
      return link

async def shorten(session :aiohttp.client.ClientSession, link: str):
   async with session.get("https://s.ze.ax/yourls-api.php", data={

   }) as resp:
      r = await resp.json(content_type=None)
      return f"https://h.ze.ax/{r['key']}"