#  packet headers #####################################################################################################
PACKET_NUMBER_HEADER: str = 'PacketNumber'
SESSION_ID_HEADER: str = 'Sid'
FRAME_START_TIME_HEADER: str = 'FrameStartTime'
FRAME_END_TIME_HEADER: str = 'FrameEndTime'
FINAL_FRAME_HEADER: str = 'FinalFrame'
SILENCE_DETECTED_HEADER: str = 'SilenceDetected'
PROCESSING_TIME_SECONDS_HEADER: str = 'ProcessingTimeSeconds'
#  split
SPLIT_PACKET_HEADER: str = 'SplitPacket'
FINAL_SPLIT_PACKET_HEADER: str = 'FinalSplitPacket'
SPLIT_ID_HEADER: str = 'SplitId'
#  bytes request
REQUEST_BYTES_HEADER: str = 'RequestBytes'
FLUSH_HEADER: str = 'Flush'
# audio attributes
SAMPLE_RATE_HEADER: str = 'SampleRate'
BIT_RATE_HEADER: str = 'BitRate'
BIT_DEPTH_HEADER: str = 'BitDepth'
AUDIO_FORMAT_HEADER: str = 'AudioFormat'
SENDING_HEADERS_HEADER: str = 'SendingHeaders'
CHANNELS_HEADER: str = 'ChannelsHeader'

# request headers ####################################################################################################
FRAME_LEN_HEADER = 'FrameLength'
FRAME_OVERLAP_HEADER = 'FrameOverlap'
BUFFER_OFFSET_HEADER = 'BufferOffset'
RESERVATION_KEY_HEADER = 'ReservationKey'

# AMQP message headers ###############################################################################################
USER_AMQP_HEADER: str = 'UserId'
MODEL_AMQP_HEADER: str = 'ModelUid'
