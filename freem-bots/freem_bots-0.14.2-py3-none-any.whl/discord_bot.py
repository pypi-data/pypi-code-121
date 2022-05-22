import io
import logging
from typing import Awaitable, Dict, List, Literal, Optional, TypeVar
import typing
import discord
from discord.channel import VoiceChannel
import discord.ext.commands
import discord.ext.commands.core
import asyncio
import numpy
import soundfile

from freem_bots.asyncio_queue_log_handler import AsyncioQueueLogHandler
from freem_bots.configuration import Config
from freem_bots.random_provider import RandomProvider
from freem_bots.tts import TTS, TTSPause, TTSVoice, TTSVoiceline, TTSVoicelinePart, TTSVoicelineSpeed
from freem_bots.cache import Cache


class DiscordBot(discord.ext.commands.Bot):  # type: ignore
	_tvC = TypeVar('_tvC', bound = Config)

	def __init__(self, configuration: _tvC) -> None:
		self._log_queue: 'asyncio.Queue[str]' = asyncio.Queue()
		self._logger = logging.getLogger('bot-discord')
		handler = AsyncioQueueLogHandler(self._log_queue)
		logging.root.addHandler(handler)
		super().__init__(command_prefix = '/', intents = self._intents)
		self._configuration = configuration
		self._random_provider: RandomProvider = RandomProvider()
		self.__load_opus()
		self._cache = (
			None
			if self._configuration.memcached_host is None or self._configuration.memcached_port is None
			else Cache(
				host = self._configuration.memcached_host,
				port = self._configuration.memcached_port,
			)
		)
		self._tts = TTS(self._configuration, self._cache)
		self._init_tasks: List[Awaitable[None]] = [
			self.__task_log_to_log_channel(),
			self.__task_watch_voice_states(),
		]
		self._user_channels: Dict[int, VoiceChannel] = {}  # user id: voice channel
		self._active_voice_clients: Dict[int, discord.VoiceClient] = {}  # guild id: voice client
		self._guild_voice_locks: Dict[int, asyncio.Lock] = {}  # guild id: lock

	@property
	def _intents(self) -> discord.Intents:
		intents = discord.Intents.all()
		return intents

	async def on_ready(self) -> None:
		''' Invoked when bot connects to Discord servers '''
		self._logger.info('Bot connected under %s', self.user.name)
		for waiting_task in self._init_tasks:
			self.loop.create_task(waiting_task)

	async def on_voice_state_update(  # pylint: disable=unused-argument
		self,
		member: discord.Member,
		before: discord.VoiceState,
		after: discord.VoiceState,
	) -> None:
		if after.channel is None:
			self._logger.debug('Registered voice state update, disconnection for user %s', member.name)
			self._user_channels.pop(member.id)
		elif after.channel is not None and isinstance(after.channel, VoiceChannel):
			self._logger.debug('Registered voice state update, user %s in channel %s', member.name, after.channel.name)
			self._user_channels[member.id] = after.channel
			if member.id == self.user.id:
				self._logger.debug(
					'Registered self connection to channel (%s), checking internal state',
					after.channel.name,
				)
				# check that we have a registered VoiceClient for this guild, otherwise we've desynced
				if after.channel.guild.id not in self._active_voice_clients:
					self._logger.warning(
						"We don't have a registered VoiceClient for this update, we are desynced, this is okay if the bot just started up"
					)

	async def get_audio_for_text(self, text: str, voice: TTSVoice, username: str) -> bytes:
		''' Returns PCM for given lines '''
		username_lines = text.split('{}')
		message_voicelines: List[TTSVoicelinePart] = []
		for username_line in username_lines:
			message_voicelines.append(TTSVoicelinePart(voice, username_line.strip(), TTSVoicelineSpeed.NORMAL))
			message_voicelines.append(
				TTSVoicelinePart(voice, username.strip(), TTSVoicelineSpeed.SLOWER, prepended_pause = TTSPause.SHORT)
			)
		message_voicelines.pop()
		voiceline = TTSVoiceline(message_voicelines)
		return await self.get_voiceline_pcm(voiceline)

	async def get_audio_for_text_simple(self, text: str, voice: TTSVoice) -> bytes:
		''' Gets PCM for a simple string '''
		voiceline = TTSVoiceline([TTSVoicelinePart(voice, text)])
		return await self.get_voiceline_pcm(voiceline)

	async def get_voiceline_pcm(self, voiceline: TTSVoiceline) -> bytes:
		''' Gets PCM for voiceline content '''
		sample_rate = 96000
		byts = await self._tts.get_audio_bytes(voiceline, sample_rate)
		return DiscordBot.get_pcm_from_bytes(byts)

	async def play_audiofile(
		self,
		filename: str,
		voice_channel: VoiceChannel,
		stay_connected: bool = False,
	) -> None:
		if '.' in filename:
			self._logger.warning('Refusing to resolve insecure path: filename=%s', filename)
			return
		full_path = f'audio_files/{filename}.wav'
		pcms = [self.get_pcm_from_file(full_path)]
		await self.play_pcms_in_voice_channel(voice_channel, pcms, stay_connected)

	def get_pcm_from_file(self, file: str) -> bytes:
		''' Gets PCM from a file '''
		(audio, sample_rate) = soundfile.read(file, dtype = 'int16')
		multiplier = round(96000 / sample_rate)
		if len(audio.shape) == 2:
			multiplier //= audio.shape[1]
		if multiplier > 1:
			stacked_p = []
			for _ in range(multiplier):
				stacked_p.append(audio)
			multiplied = numpy.stack(stacked_p, axis = 1)
			return typing.cast(bytes, multiplied.tobytes())
		return typing.cast(bytes, audio.tobytes())

	@staticmethod
	def get_pcm_from_bytes(sound_bytes: bytes) -> bytes:
		''' Gets PCM from bytes '''
		return sound_bytes

	def send_log_to_log_channel(self, message: str) -> None:
		self._log_queue.put_nowait(message)

	def locate_user_in_voice_channel(self, target_user: discord.User) -> Optional[VoiceChannel]:
		if target_user.id in self._user_channels:
			return self._user_channels[target_user.id]
		else:
			return None

	async def play_voiceline_in_voice_channel(
		self,
		voice_channel: VoiceChannel,
		voiceline: TTSVoiceline,
		stay_connected: bool = False,
	) -> None:
		byts = await self._tts.get_audio_bytes(voiceline)
		pcms = [DiscordBot.get_pcm_from_bytes(byts)]
		await self.play_pcms_in_voice_channel(voice_channel, pcms, stay_connected)

	async def play_pcms_in_voice_channel(
		self,
		voice_channel: VoiceChannel,
		pcms: List[bytes],
		stay_connected: bool = False,
	) -> None:
		''' Connects to a channel, plays a collection of PCMs, then disconnects '''
		await self.connect_to_voice_channel(voice_channel)
		await self.play_pcms_in_guild(voice_channel.guild, pcms)
		if not stay_connected:
			await self.disconnect_from_voice_channel(voice_channel.guild)

	async def connect_to_voice_channel(self, target_voice_channel: VoiceChannel) -> None:
		guild: discord.Guild = target_voice_channel.guild
		self._logger.debug('Requested to connect to channel %s', target_voice_channel.name)
		async with self._get_voice_lock_for_guild(guild):
			if guild.id in self._active_voice_clients:
				# user is already connected to a voice channel
				active_voice_client = self._active_voice_clients[guild.id]
				assert active_voice_client.is_connected()
				active_channel_gen = active_voice_client.channel
				if isinstance(active_channel_gen, VoiceChannel):
					active_channel: VoiceChannel = active_channel_gen
					if active_channel.id == target_voice_channel.id:
						# target channel is the one we're currently in, nothing to do
						self._logger.debug("Target channel is the same as the one we're currently in, nothing to do")
					else:
						self._logger.debug(
							'Target channel (%s) is different from the current channel (%s), moving',
							target_voice_channel.name,
							active_channel.name,
						)
						await active_voice_client.move_to(target_voice_channel)
						condition = asyncio.Condition()
						async with condition:
							try:
								self._logger.debug('Waiting for WS to drop')
								await asyncio.wait_for(
									condition.wait_for(lambda: not active_voice_client.is_connected()),
									timeout = 2.0,
								)
							except asyncio.TimeoutError:
								self._logger.debug('WS never dropped, this is fine')
							self._logger.debug('Waiting for WS to reconnect')
							try:
								await asyncio.wait_for(condition.wait_for(active_voice_client.is_connected), timeout = 10.0)
							except asyncio.TimeoutError:
								self._logger.error('We were never reconnected')
								raise
							self._logger.debug('Move between channels completed')

				else:
					# invalid channel type
					self._logger.error('Active voice channel is of unknown type, cannot proceed safely')
					raise Exception(f'Invalid channel type: {type(active_channel_gen)}')
			else:
				# user is not connected to a voice channel
				self._logger.debug('Not connected to any channel yet, connecting')
				new_voice_client: discord.VoiceClient = await target_voice_channel.connect()
				self._active_voice_clients[guild.id] = new_voice_client

	async def disconnect_from_voice_channel(self, guild: discord.Guild) -> None:
		self._logger.debug('Requested to disconnect from channel in guild %s', guild.name)
		async with self._get_voice_lock_for_guild(guild):
			if guild.id in self._active_voice_clients:
				# we are indeed connected to a voice channel in this guild
				active_voice_client = self._active_voice_clients[guild.id]
				self._logger.debug('Connected to a channel, disconnecting')
				await active_voice_client.disconnect(force = True)
				self._active_voice_clients.pop(guild.id)
			else:
				# we are not connected to a voice channel in this guild, nothing to do
				self._logger.debug(
					'Not connected to a voice channel, nothing to do (if this is innacurate, we have desynced and should terminate)'
				)

	async def play_pcms_in_guild(self, guild: discord.Guild, pcms: List[bytes]) -> None:
		async with self._get_voice_lock_for_guild(guild):
			if guild.id in self._active_voice_clients:
				# we are indeed connected somewhere in this guild
				voice_client = self._active_voice_clients[guild.id]
				for pcm_bytes in pcms:
					audio_stream = io.BytesIO(pcm_bytes)
					audio_source = discord.PCMAudio(audio_stream)
					self._logger.debug('Starting playing')
					voice_client.play(audio_source)
					while voice_client.is_playing():
						await asyncio.sleep(0.005)
					self._logger.debug('Done playing')
			else:
				# we are not connected in this guild
				self._logger.error('Requested to play PCMs in a guild where we are not in a voice channel')

	async def stream_pcms_in_guild(self, guild: discord.Guild, stream: io.BufferedIOBase) -> None:
		async with self._get_voice_lock_for_guild(guild):
			if guild.id in self._active_voice_clients:
				# we are indeed connected somewhere in this guild
				voice_client = self._active_voice_clients[guild.id]
				audio_source = discord.PCMAudio(stream)
				self._logger.debug('Starting streaming')
				voice_client.play(audio_source)
				while voice_client.is_playing():
					await asyncio.sleep(0.1)
				self._logger.debug('Done streaming')
			else:
				# we are not connected in this guild
				self._logger.error('Requested to stream audio in a guild where we are not in a voice channel')

	def _get_voice_lock_for_guild(self, guild: discord.Guild) -> asyncio.Lock:
		if guild.id not in self._guild_voice_locks:
			self._guild_voice_locks[guild.id] = asyncio.Lock()
		return self._guild_voice_locks[guild.id]

	async def _get_user_by_uid(self, guild: str, user_id: int) -> Optional[discord.Member]:
		try:
			target_user_id = user_id
			# find the guild
			target_guilds = [i for i in self.guilds if i.name.lower() == guild.lower()]
			if len(target_guilds) == 0:
				self._logger.fatal('Unable to find %s guild', guild)
				return None
			target_guild = target_guilds[0]
			# get user
			members: List[discord.Member] = [member for member in target_guild.members if member.id == target_user_id]
			if len(members) == 0:
				self._logger.error('Unable to find user in %s', guild)
				return None

			target_user = members[0]
			return target_user
		except discord.DiscordException:
			return None

	def __load_opus(self) -> None:
		if not discord.opus.is_loaded():
			discord.opus._load_default()  # pylint: disable=protected-access
		if not discord.opus.is_loaded():
			raise Exception('Unable to load OPUS audio library')

	async def __task_log_to_log_channel(self) -> None:
		log_channel_id = self._configuration.log_channel_id
		if log_channel_id is None:
			self._logger.warning("Won't log to discord, no log channel configured")
			while not self.is_closed():
				await self._log_queue.get()
				await asyncio.sleep(0.05)
			return
		log_channel = self.get_channel(log_channel_id)
		while not self.is_closed():
			while not self._log_queue.empty():
				message: str = await self._log_queue.get()
				try:
					message = message.replace('`', '\\`')
					message = f'`{message}`'
					await log_channel.send(message)
				except discord.DiscordException:
					await asyncio.sleep(5.0)  # probably hit rate limiting, if discord disconnect, loop will stop anyway
			await asyncio.sleep(0.05)

	async def __task_watch_voice_states(self) -> None:
		while not self.is_closed():
			to_prune: List[int] = []
			for guild_id in self._active_voice_clients:
				voice_client = self._active_voice_clients[guild_id]
				if not voice_client.is_connected():
					channel = voice_client.channel
					assert channel is not None and isinstance(channel, discord.VoiceChannel)
					self._logger.info('Voice client (channel %s) indicated disconnected', channel.name)
					await asyncio.sleep(5)
					if not voice_client.is_connected():
						self._logger.error('Voice client still indicating disconnected, pruning it from local state')
						to_prune.append(guild_id)
			for id_to_prune in to_prune:
				self._active_voice_clients.pop(id_to_prune)
			await asyncio.sleep(2.5)

	# pylint: disable=dangerous-default-value
	async def sync_commands(
		self,
		commands: Optional[List[discord.ext.commands.core.ApplicationCommand]] = None,
		method: Literal['individual', 'bulk', 'auto'] = 'bulk',
		force: bool = False,
		guild_ids: Optional[List[int]] = None,
		register_guild_commands: bool = True,
		check_guilds: Optional[List[int]] = [],
		delete_exiting: bool = True,
	) -> None:
		return typing.cast(
			None,
			await super().sync_commands(
				commands,
				method,
				force,
				guild_ids,
				register_guild_commands,
				check_guilds,
				delete_exiting,
			),
		)

	async def register_command(
		self,
		_: discord.ext.commands.core.ApplicationCommand,
		__: bool = True,
		___: List[int] = None,
	) -> None:
		return None
