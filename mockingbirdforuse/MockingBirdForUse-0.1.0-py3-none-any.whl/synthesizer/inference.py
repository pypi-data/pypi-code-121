import torch
import librosa
import numpy as np
from pathlib import Path
from typing import Union, List
from pypinyin import lazy_pinyin, Style

from . import audio
from .hparams import hparams
from .utils.symbols import symbols
from .models.tacotron import Tacotron
from .utils.text import text_to_sequence
from .utils.logmmse import denoise, profile_noise
from ..log import logger


class Synthesizer:
    sample_rate = hparams.sample_rate
    hparams = hparams

    def __init__(self, model_fpath: Path):
        """
        The model isn't instantiated and loaded in memory until needed or until load() is called.

        :param model_fpath: path to the trained model file
        """
        self.model_fpath = model_fpath

        # Check for GPU
        if torch.cuda.is_available():
            self.device = torch.device("cuda")
        else:
            self.device = torch.device("cpu")
        logger.info(f"Synthesizer using device: {self.device}")

        # Tacotron model will be instantiated later on first use.
        self._model = None

    def is_loaded(self):
        """
        Whether the model is loaded in memory.
        """
        return self._model is not None

    def load(self):
        """
        Instantiates and loads the model given the weights file that was passed in the constructor.
        """
        self._model = Tacotron(
            embed_dims=hparams.tts_embed_dims,
            num_chars=len(symbols),
            encoder_dims=hparams.tts_encoder_dims,
            decoder_dims=hparams.tts_decoder_dims,
            n_mels=hparams.num_mels,
            fft_bins=hparams.num_mels,
            postnet_dims=hparams.tts_postnet_dims,
            encoder_K=hparams.tts_encoder_K,
            lstm_dims=hparams.tts_lstm_dims,
            postnet_K=hparams.tts_postnet_K,
            num_highways=hparams.tts_num_highways,
            dropout=hparams.tts_dropout,
            stop_threshold=hparams.tts_stop_threshold,
            speaker_embedding_size=hparams.speaker_embedding_size,
        ).to(self.device)

        self._model.load(self.model_fpath, self.device)
        self._model.eval()

        logger.info(
            'Loaded synthesizer "%s" trained to step %d'
            % (self.model_fpath.name, self._model.state_dict()["step"])
        )

    def synthesize_spectrograms(
        self,
        texts: List[str],
        embeddings: Union[np.ndarray, List[np.ndarray]],
        return_alignments=False,
        style_idx=0,
        min_stop_token=5,
        steps=2000,
    ):
        """
        Synthesizes mel spectrograms from texts and speaker embeddings.

        :param texts: a list of N text prompts to be synthesized
        :param embeddings: a numpy array or list of speaker embeddings of shape (N, 256)
        :param return_alignments: if True, a matrix representing the alignments between the
        characters
        and each decoder output step will be returned for each spectrogram
        :return: a list of N melspectrograms as numpy arrays of shape (80, Mi), where Mi is the
        sequence length of spectrogram i, and possibly the alignments.
        """
        # Load the model on the first request.
        if not self.is_loaded():
            self.load()
        assert self._model is not None

        logger.debug("Read " + str(texts))
        texts = [
            " ".join(lazy_pinyin(v, style=Style.TONE3, neutral_tone_with_five=True))
            for v in texts
        ]
        logger.debug("Synthesizing " + str(texts))
        # Preprocess text inputs
        inputs = [text_to_sequence(text, hparams.tts_cleaner_names) for text in texts]
        if not isinstance(embeddings, list):
            embeddings = [embeddings]

        # Batch inputs
        batched_inputs = [
            inputs[i : i + hparams.synthesis_batch_size]
            for i in range(0, len(inputs), hparams.synthesis_batch_size)
        ]
        batched_embeds = [
            embeddings[i : i + hparams.synthesis_batch_size]
            for i in range(0, len(embeddings), hparams.synthesis_batch_size)
        ]

        specs = []
        alignments = []
        for i, batch in enumerate(batched_inputs, 1):
            logger.debug(f"\n| Generating {i}/{len(batched_inputs)}")

            # Pad texts so they are all the same length
            text_lens = [len(text) for text in batch]
            max_text_len = max(text_lens)
            chars = [pad1d(text, max_text_len) for text in batch]
            chars = np.stack(chars)

            # Stack speaker embeddings into 2D array for batch processing
            speaker_embeds = np.stack(batched_embeds[i - 1])

            # Convert to tensor
            chars = torch.tensor(chars).long().to(self.device)
            speaker_embeddings = torch.tensor(speaker_embeds).float().to(self.device)

            # Inference
            _, mels, alignments = self._model.generate(
                chars,
                speaker_embeddings,
                style_idx=style_idx,
                min_stop_token=min_stop_token,
                steps=steps,
            )
            mels = mels.detach().cpu().numpy()
            for m in mels:
                # Trim silence from end of each spectrogram
                while np.max(m[:, -1]) < hparams.tts_stop_threshold:
                    m = m[:, :-1]
                specs.append(m)

        logger.debug("\n\nDone.\n")
        return (specs, alignments) if return_alignments else specs

    @staticmethod
    def load_preprocess_wav(fpath):
        """
        Loads and preprocesses an audio file under the same conditions the audio files were used to
        train the synthesizer.
        """
        wav = librosa.load(path=str(fpath), sr=hparams.sample_rate)[0]
        if hparams.rescale:
            wav = wav / np.abs(wav).max() * hparams.rescaling_max
        # denoise
        if len(wav) > hparams.sample_rate * (0.3 + 0.1):
            noise_wav = np.concatenate(
                [
                    wav[: int(hparams.sample_rate * 0.15)],
                    wav[-int(hparams.sample_rate * 0.15) :],
                ]
            )
            profile = profile_noise(noise_wav, hparams.sample_rate)
            wav = denoise(wav, profile)
        return wav

    @staticmethod
    def make_spectrogram(fpath_or_wav: Union[str, Path, np.ndarray]):
        """
        Creates a mel spectrogram from an audio file in the same manner as the mel spectrograms that
        were fed to the synthesizer when training.
        """
        if isinstance(fpath_or_wav, str) or isinstance(fpath_or_wav, Path):
            wav = Synthesizer.load_preprocess_wav(fpath_or_wav)
        else:
            wav = fpath_or_wav

        mel_spectrogram = audio.melspectrogram(wav, hparams).astype(np.float32)
        return mel_spectrogram

    @staticmethod
    def griffin_lim(mel):
        """
        Inverts a mel spectrogram using Griffin-Lim. The mel spectrogram is expected to have been built
        with the same parameters present in hparams.py.
        """
        return audio.inv_mel_spectrogram(mel, hparams)


def pad1d(x, max_len, pad_value=0):
    return np.pad(x, (0, max_len - len(x)), mode="constant", constant_values=pad_value)
