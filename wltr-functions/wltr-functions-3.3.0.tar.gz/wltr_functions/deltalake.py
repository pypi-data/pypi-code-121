class DeltaLake(object):
    class LandingZone:
        def __init__(self, source_dataframe, file_path, stream_query):
            self.source_dataframe = source_dataframe
            self.file_path = file_path
            self.stream_query = stream_query

        def write_stream(self):
            try:
                (self.source_dataframe \
                 .writeStream.format('delta') \
                 .option('checkpointLocation', self.file_path + '/_checkpoint') \
                 .queryName(self.stream_query) \
                 .outputMode('append') \
                 .start(self.file_path) \
                 .awaitTermination())

                return

            except ValueError as e:
                return print(e)


