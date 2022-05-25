"""
“Commons Clause” License Condition v1.0
Copyright Pirxcy 2022
The Software is provided to you by the Licensor under the
License, as defined below, subject to the following condition.
Without limiting other conditions in the License, the grant
of rights under the License will not include, and the License
does not grant to you, the right to Sell the Software.
For purposes of the foregoing, “Sell” means practicing any or
all of the rights granted to you under the License to provide
to third parties, for a fee or other consideration (including
without limitation fees for hosting or consulting/ support
services related to the Software), a product or service whose
value derives, entirely or substantially, from the functionality
of the Software. Any license notice or attribution required by
the License must also include this Commons Clause License
Condition notice.
Software: DiscordFilter
License: Apache 2.0
"""

import asyncio
import aiohttp

import json
import os

from typing import Any
from typing import Union

base = "https://8176b8c0-b819-499c-9fb2-e4bf4fbb9331.id.repl.co/index.json"

class FilterException(Exception):
  pass

class InvalidSelection(FilterException):
  pass

class HTTPClient:
    def __init__(self, session: aiohttp.ClientSession) -> None:
        self.session = session

    async def decider(self, response: aiohttp.ClientResponse) -> None:
      jsonResponse = await response.json()
      plain = await response.text()
      await self.close()
      if 'application/json' in response.headers.get('content-type', ''):
        return jsonResponse
      return plain

    async def close(self) -> None:
        return await self.session.close()

    async def request(self, method: str, *args: Any, **kwargs: Any) -> Union[str, dict]:
        async with self.session.request(method, *args, **kwargs) as response:
            return await self.decider(response)

    async def get(self, *args: Any, **kwargs: Any) -> Union[str, dict]:
        return await self.request('GET', *args, **kwargs)

    async def post(self, *args: Any, **kwargs: Any) -> Union[str, dict]:
        return await self.request('POST', *args, **kwargs)

class filter:
  def __init__(
    self,
    blacklist_file: str = None
  ) -> None:
    if blacklist_file == None:
      raise InvalidSelection("No File Entered.")
    self.blacklist_file = blacklist_file
    if not os.path.isfile(self.blacklist_file):
      file = open(
				self.blacklist_file, 
				"x"
			)
      file.write("[]")
      file.close()
    return
    
  async def update_blacklist(self):
    try:
      http = HTTPClient(session = aiohttp.ClientSession())
      blacklist_words = await http.get(base)
      with open(self.blacklist_file) as f:
        stored_words = json.load(f)
      added = 0
      for word in blacklist_words:
        if word in stored_words:
          continue
        else:
          stored_words.append(word)
          added += 1
      if added == 0:
        return False
      with open(
	      self.blacklist_file,
	      "w"
      ) as f_:
        print(stored_words)
        json.dump(
          stored_words,
          f_,
          indent=2
        )
        return True
    except Exception as error:
      raise(error)    
    
  async def is_filtered(
    self,
    message
  ):
    try:
      with open(self.blacklist_file) as f:
        blacklisted_words = json.load(f)
      if any(word in message.content.lower() for word in blacklisted_words.lower()):
        return True
      return False
    except Exception as error:
      raise(error)