import io
import base64
import logging
import re
from typing import List, Optional, Tuple
import typing
import numpy

import soundfile

from freem_bots.configuration import Config
from aiohttp import ClientSession

from enum import Enum

from freem_bots.demoji_wrp import Demoji
from freem_bots.cache import Cache


class TTSProvider(Enum):
	AZURE = 1
	GCLOUD = 2


class TTSVoiceLanguage(Enum):
	ENGLISH = 1
	SPANISH = 2
	CZECH = 3
	RUSSIAN = 4
	JAPANESE = 5
	SOMALI = 6
	GERMAN = 7
	SWAHILI = 8
	POLISH = 9
	SLOVAK = 10
	WELSH = 11


class TTSVoicelineSpeed(Enum):
	SLOWEST = 0.2
	SLOW = 0.5
	SLOWER = 0.8
	NORMAL = 1.0
	FASTER = 1.2
	FAST = 1.5
	FASTEST = 2.0


class TTSVoicelinePitch(Enum):
	LOW = 'low'
	MEDIUM = 'medium'
	HIGH = 'high'


class TTSPause(Enum):
	SHORT = 'weak'
	MEDIUM = 'medium'
	STRONG = 'strong'


class TTSVoice(Enum):
	EN_RYAN = (TTSProvider.AZURE, 'en-GB-RyanNeural', TTSVoiceLanguage.ENGLISH)
	EN_WILLIAM = (TTSProvider.AZURE, 'en-AU-WilliamNeural', TTSVoiceLanguage.ENGLISH)
	EN_CLARA = (TTSProvider.AZURE, 'en-CA-ClaraNeural', TTSVoiceLanguage.ENGLISH)
	EN_JENNY = (TTSProvider.AZURE, 'en-US-JennyNeural', TTSVoiceLanguage.ENGLISH)
	EN_NEERJA = (TTSProvider.AZURE, 'en-IN-NeerjaNeural', TTSVoiceLanguage.ENGLISH)
	EN_ADA = (TTSProvider.GCLOUD, 'en-US-Wavenet-C', TTSVoiceLanguage.ENGLISH)

	CS_ANTONIN = (TTSProvider.AZURE, 'cs-CZ-AntoninNeural', TTSVoiceLanguage.CZECH)
	CS_VLASTA = (TTSProvider.AZURE, 'cs-CZ-VlastaNeural', TTSVoiceLanguage.CZECH)
	CS_JAKUB = (TTSProvider.AZURE, 'cs-CZ-Jakub', TTSVoiceLanguage.CZECH)

	RU_DMITRY = (TTSProvider.AZURE, 'ru-RU-DmitryNeural', TTSVoiceLanguage.RUSSIAN)
	RU_SVETLANA = (TTSProvider.AZURE, 'ru-RU-SvetlanaNeural', TTSVoiceLanguage.RUSSIAN)

	JA_KEITA = (TTSProvider.AZURE, 'ja-JP-KeitaNeural', TTSVoiceLanguage.JAPANESE)
	JA_NANAMI = (TTSProvider.AZURE, 'ja-JP-NanamiNeural', TTSVoiceLanguage.JAPANESE)

	SO_UBAX = (TTSProvider.AZURE, 'so-SO-UbaxNeural', TTSVoiceLanguage.SOMALI)
	DE_CONRAD = (TTSProvider.AZURE, 'de-DE-ConradNeural', TTSVoiceLanguage.GERMAN)
	SW_ZURI = (TTSProvider.AZURE, 'sw-KE-ZuriNeural', TTSVoiceLanguage.SWAHILI)
	PL_AGNIESZKA = (TTSProvider.AZURE, 'pl-PL-AgnieszkaNeural', TTSVoiceLanguage.POLISH)
	SK_VIKTORIA = (TTSProvider.AZURE, 'sk-SK-ViktoriaNeural', TTSVoiceLanguage.SLOVAK)
	CY_ALED = (TTSProvider.AZURE, 'cy-GB-AledNeural', TTSVoiceLanguage.WELSH)
	ES_ALVARO = (TTSProvider.AZURE, 'es-ES-AlvaroNeural', TTSVoiceLanguage.SPANISH)


class TTSVoicelinePart:
	def __init__(
		self,
		voice: TTSVoice,
		text: str,
		speed: TTSVoicelineSpeed = TTSVoicelineSpeed.NORMAL,
		pitch: TTSVoicelinePitch = TTSVoicelinePitch.MEDIUM,
		prepended_pause: TTSPause = None,
	) -> None:

		self.voice_provider, self.voice_name, self.voice_language = voice.value
		self.text = Demoji().remove_emojis(text)
		self.speed = speed
		self.pitch = pitch
		self.prepended_pause = prepended_pause
		self.ssml_part = self._assemble_ssml_part()
		self.ssml_full = self.assemble_ssml_full(self.ssml_part)

	def _assemble_ssml_part(self) -> str:
		escaped_text = self._escape_text(self.text)

		assembled: str = ''

		if self.voice_provider == TTSProvider.AZURE:
			# open voice name
			assembled += f'<voice name="{self.voice_name}">'
			# open speed, pitch
			assembled += f'<prosody rate="{self.speed.value}" pitch="{self.pitch.value}">'

			# insert pause if applicable
			if self.prepended_pause is not None:
				assembled += f'<break strength="{self.prepended_pause.value}" />'

			# insert text
			assembled += escaped_text

			# close speed, pitch
			assembled += '</prosody>'
			# close voice name
			assembled += '</voice>'
		elif self.voice_provider == TTSProvider.GCLOUD:
			# open voice name
			assembled += f'<voice name="{self.voice_name}">'
			# open speed, pitch
			assembled += f'<prosody rate="{int(self.speed.value * 100)}%" pitch="{self.pitch.value}">'

			# insert pause if applicable
			if self.prepended_pause is not None:
				assembled += f'<break strength="{self.prepended_pause.value}" />'
			# insert text
			assembled += escaped_text

			# close speed, pitch
			assembled += '</prosody>'
			# close voie name
			assembled += '</voice>'
		else:
			raise NotImplementedError()
		return assembled

	@staticmethod
	def _scrub_duplicate_voice_definitions(input_ssml: str) -> str:
		# find all voice starts
		opening_matches: List[Tuple[int, Optional[str]]] = []
		for re_match in re.finditer(r'<voice name=\"(?P<voice>.*?)\">', input_ssml):
			start = re_match.start()
			voice: Optional[str] = re_match.group('voice')
			opening_matches.append((start, voice))

		closing_match_positions: List[int] = []
		for re_match in re.finditer(r'</voice>', input_ssml):
			start = re_match.start()
			closing_match_positions.append(start)

		marked_opening_matches_for_removal: List[Tuple[int, Optional[str]]] = []

		last_match: Optional[Tuple[int, Optional[str]]] = None
		for opening_match in opening_matches:
			if last_match is not None and last_match[1] == opening_match[1]:  # pylint:disable=unsubscriptable-object
				# same voice, can remove here
				marked_opening_matches_for_removal.append(opening_match)
			last_match = opening_match

		marked_closing_matches_for_removal = []
		for marked_opening_match_for_removal in marked_opening_matches_for_removal:
			# need to remove the previous close
			max_previous_close = None
			for close in closing_match_positions:
				if close >= marked_opening_match_for_removal[0]:  # this close is after our current open, we can keep it
					continue
				if max_previous_close is None or close > max_previous_close:
					max_previous_close = close
			if max_previous_close is not None:
				marked_closing_matches_for_removal.append(max_previous_close)

		ranges_marked_for_removal = []
		for marked_opening_match in marked_opening_matches_for_removal:
			start_position = marked_opening_match[0]
			end_position = start_position + len(f'<voice name="{marked_opening_match[1]}">')
			ranges_marked_for_removal.append([start_position, end_position])
		for marked_closing_position in marked_closing_matches_for_removal:
			start_position = marked_closing_position
			end_position = start_position + len('</voice>')
			ranges_marked_for_removal.append([start_position, end_position])

		# now, change the input string to char array, replace the removed ranges with None and recombine without these
		input_text_arr = typing.cast(List[Optional[str]], list(input_ssml))
		for range_to_remove in ranges_marked_for_removal:
			for i in range(range_to_remove[0], range_to_remove[1]):
				input_text_arr[i] = None
		output_ssml = ''.join([char for char in input_text_arr if char is not None])
		return output_ssml

	def assemble_ssml_full(self, inner_part: Optional[str] = None) -> str:
		if inner_part is None:
			inner_part = self._assemble_ssml_part()

		if self.voice_provider == TTSProvider.AZURE:
			full_ssml = f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="en-US">{inner_part}</speak>'
		elif self.voice_provider == TTSProvider.GCLOUD:
			full_ssml = f'<speak>{inner_part}</speak>'
		else:
			raise NotImplementedError()
		full_ssml = TTSVoicelinePart._scrub_duplicate_voice_definitions(full_ssml)
		return full_ssml

	def _escape_text(self, text: str) -> str:
		text = text.replace('&', '&amp;')
		text = text.replace('<', '&lt;')
		text = text.replace('>', '&gt;')
		text = text.replace('"', '&quot;')
		text = text.replace("'", '&apos;')
		return text

	@staticmethod
	def join_parts(parts: 'List[TTSVoicelinePart]') -> str:
		if len(parts) == 0:
			raise Exception('No parts given, nothing to produce')
		initial_provider = parts[0].voice_provider
		for i in range(1, len(parts)):
			if parts[i].voice_provider != initial_provider:
				raise Exception('Cannot use different providers in one voiceline')
		if len(parts) == 1:
			return parts[0].ssml_full
		return parts[0].assemble_ssml_full(''.join([part.ssml_part for part in parts]))


class TTSVoiceline:
	def __init__(self, parts: List[TTSVoicelinePart]) -> None:
		self.parts = parts
		self.provider = self.parts[0].voice_provider
		self.ssml = self._get_ssml_for_parts()

	def _get_ssml_for_parts(self) -> str:
		return TTSVoicelinePart.join_parts(self.parts)


class TTS:
	def __init__(self, configuration: Config, cache: Optional[Cache]) -> None:
		self._logger = logging.getLogger('tts')
		self.configuration = configuration
		self.cache = cache

	async def get_audio_bytes(self, voiceline: TTSVoiceline, target_sample_rate: int = 96000) -> bytes:
		if voiceline.provider == TTSProvider.AZURE:
			return await self._get_audio_bytes_azure(voiceline.ssml, target_sample_rate)
		elif voiceline.provider == TTSProvider.GCLOUD:
			return await self._get_audio_bytes_gcloud(voiceline.ssml, target_sample_rate)
		else:
			raise NotImplementedError()

	async def _get_audio_bytes_azure(self, ssml: str, target_sample_rate: int) -> bytes:
		cache_key = f'{ssml=}, {target_sample_rate=}'
		if self.cache:
			cached = await self.cache.get(cache_key)
			if cached:
				return cached

		if self.configuration.azure_token is None:
			raise Exception('Cannot get audio from Azure, no Azure token configured')
		if self.configuration.azure_location is None:
			raise Exception('Cannot get audio from Azure, no Azure location configured')

		url = f'https://{self.configuration.azure_location}.tts.speech.microsoft.com/cognitiveservices/v1'
		output_format = 'riff-48khz-16bit-mono-pcm'
		async with ClientSession() as session:
			self._logger.info('Making request to Azure TTS endpoint, format %s', output_format)
			async with session.post(
				url = url,
				headers = {
					'Ocp-Apim-Subscription-Key': self.configuration.azure_token,
					'Content-Type': 'application/ssml+xml',
					'X-Microsoft-OutputFormat': output_format,
				},
				data = ssml,
			) as response:
				self._logger.info('Got response from Azure TTS endpoint')
				response_bytes = await response.read()
				# have 48 kHz stereo, need to 96 kHz stereo
				with io.BytesIO(response_bytes) as response_file:
					response_file.name = 'audio.wav'
					(response_audio, _) = soundfile.read(response_file, dtype = 'int16')
					stacked = numpy.stack([response_audio, response_audio], axis = 1)
					return typing.cast(bytes, stacked.tobytes())

	async def _get_audio_bytes_gcloud(self, ssml: str, target_sample_rate: int) -> bytes:
		cache_key = f'{ssml=}, {target_sample_rate=}'
		if self.cache:
			cached = await self.cache.get(cache_key)
			if cached:
				return cached

		if self.configuration.gcloud_voice_key is None:
			raise Exception('Cannot get audio from Azure, no GCloud API key configured')

		url = f'https://texttospeech.googleapis.com/v1/text:synthesize?key={self.configuration.gcloud_voice_key}'
		output_format = 'LINEAR16'
		async with ClientSession() as session:
			self._logger.info('Making request to GCloud TTS endpoint, format %s', output_format)
			async with session.post(
				url = url,
				json = {
					'input': {'ssml': ssml},
					'voice': {'languageCode': 'en-us', 'name': 'en-US-Wavenet-C', 'ssmlGender': 'FEMALE'},
					'audioConfig': {'audioEncoding': output_format},
				},
			) as response:
				self._logger.info('Got response from GCloud TTS endpoint')
				response_json = await response.json()
				response_base64 = response_json['audioContent']
				response_bytes = base64.b64decode(response_base64)
				# have 48 kHz mono, need to 96 kHz stereo
				with io.BytesIO(response_bytes) as response_file:
					response_file.name = 'audio.wav'
					(response_audio, _) = soundfile.read(response_file, dtype = 'int16')
					stacked = numpy.stack([response_audio, response_audio, response_audio, response_audio], axis = 1)
					return typing.cast(bytes, stacked.tobytes())
