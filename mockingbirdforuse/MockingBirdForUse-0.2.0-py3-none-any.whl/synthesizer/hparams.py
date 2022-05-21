from dataclasses import dataclass


@dataclass
class HParams:
    ### Signal Processing (used in both synthesizer and vocoder)
    sample_rate = 16000
    n_fft = 800
    num_mels = 80
    hop_size = 200
    """Tacotron uses 12.5 ms frame shift (set to sample_rate * 0.0125)"""
    win_size = 800
    """Tacotron uses 50 ms frame length (set to sample_rate * 0.050)"""
    fmin = 55
    min_level_db = -100
    ref_level_db = 20
    max_abs_value = 4.0
    """Gradient explodes if too big, premature convergence if too small."""
    preemphasis = 0.97
    """Filter coefficient to use if preemphasize is True"""
    preemphasize = True

    ### Tacotron Text-to-Speech (TTS)
    tts_embed_dims = 512
    """Embedding dimension for the graphemes/phoneme inputs"""
    tts_encoder_dims = 256
    tts_decoder_dims = 128
    tts_postnet_dims = 512
    tts_encoder_K = 5
    tts_lstm_dims = 1024
    tts_postnet_K = 5
    tts_num_highways = 4
    tts_dropout = 0.5
    tts_cleaner_names = ["basic_cleaners"]
    tts_stop_threshold = -3.4
    """
    Value below which audio generation ends.
    For example, for a range of [-4, 4], this
    will terminate the sequence at the first
    frame that has all values < -3.4
    """

    ### Tacotron Training
    tts_schedule = [
        (2, 1e-3, 10_000, 12),
        (2, 5e-4, 15_000, 12),
        (2, 2e-4, 20_000, 12),
        (2, 1e-4, 30_000, 12),
        (2, 5e-5, 40_000, 12),
        (2, 1e-5, 60_000, 12),
        (2, 5e-6, 160_000, 12),
        (2, 3e-6, 320_000, 12),
        (2, 1e-6, 640_000, 12),
    ]
    """
    Progressive training schedule
    (r, lr, step, batch_size)
    r = reduction factor (# of mel frames synthesized for each decoder iteration)
    lr = learning rate
    """

    tts_clip_grad_norm = 1.0
    """clips the gradient norm to prevent explosion - set to None if not needed"""
    tts_eval_interval = 500
    """
    Number of steps between model evaluation (sample generation)
    Set to -1 to generate after completing epoch, or 0 to disable
    """
    tts_eval_num_samples = 1
    """Makes this number of samples"""
    tts_finetune_layers = []
    """For finetune usage, if set, only selected layers will be trained, available: encoder,encoder_proj,gst,decoder,postnet,post_proj"""

    ### Data Preprocessing
    max_mel_frames = 900
    rescale = True
    rescaling_max = 0.9
    synthesis_batch_size = 16
    """For vocoder preprocessing and inference."""

    ### Mel Visualization and Griffin-Lim
    signal_normalization = True
    power = 1.5
    griffin_lim_iters = 60

    ### Audio processing options
    fmax = 7600
    """Should not exceed (sample_rate // 2)"""
    allow_clipping_in_normalization = True
    """Used when signal_normalization = True"""
    clip_mels_length = True
    """If true, discards samples exceeding max_mel_frames"""
    use_lws = False
    """Fast spectrogram phase recovery using local weighted sums"""
    symmetric_mels = True
    """Sets mel range to [-max_abs_value, max_abs_value] if True, and [0, max_abs_value] if False"""
    trim_silence = True
    """Use with sample_rate of 16000 for best results"""

    ### SV2TTS
    speaker_embedding_size = 256
    """Dimension for the speaker embedding"""
    silence_min_duration_split = 0.4
    """Duration in seconds of a silence for an utterance to be split"""
    utterance_min_duration = 1.6
    """Duration in seconds below which utterances are discarded"""
    use_gst = True
    """Whether to use global style token"""
    use_ser_for_gst = True
    """Whether to use speaker embedding referenced for global style token"""


hparams = HParams()
