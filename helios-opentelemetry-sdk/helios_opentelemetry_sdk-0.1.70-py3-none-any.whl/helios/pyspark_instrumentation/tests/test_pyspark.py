from logging import getLogger
from unittest import TestCase
from secrets import token_hex

from pyspark.sql import SparkSession

from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from helios.pyspark_instrumentation.src.pyspark import PySparkInstrumentor
from helios.pyspark_instrumentation.src.pyspark import SPAN_ATTRIBUTES_SPARK_PATH, SPAN_ATTRIBUTES_SPARK_FORMAT, \
    SPAN_ATTRIBUTES_SPARK_NAME, SPAN_ATTRIBUTES_SPARK_MODE, SPAN_ATTRIBUTES_SPARK_PARTITION_BY, \
    SPAN_ATTRIBUTES_SPARK_OUTPUT_MODE, SPAN_ATTRIBUTES_SPARK_QUERY_NAME, SAVE_SPAN_NAME, SAVE_AS_TABLE_SPAN_NAME, \
    LOAD_STREAM_SPAN_NAME, START_STREAM_SPAN_NAME

_LOG = getLogger(__name__)


class TestPySpark(TestCase):
    """
    For running these tests we need to have a Spark server running locally
    """

    def setUp(self) -> None:
        self.span_exporter = InMemorySpanExporter()
        self.span_processor = BatchSpanProcessor(self.span_exporter)
        self.tracer_provider = TracerProvider()
        self.tracer_provider.add_span_processor(self.span_processor)

        self.tracer_provider.force_flush()
        self.span_exporter.clear()

        PySparkInstrumentor().instrument(tracer_provider=self.tracer_provider)

    def tearDown(self) -> None:
        self.tracer_provider.force_flush()
        self.span_exporter.clear()
        PySparkInstrumentor().uninstrument()

    def _createDataFrame(self):
        spark = SparkSession.builder.getOrCreate()

        data = [('James', '', 'Smith', '1991-04-01', 'M', 3000),
                ('Michael', 'Rose', '', '2000-05-19', 'M', 4000),
                ('Robert', '', 'Williams', '1978-09-05', 'M', 4000),
                ('Maria', 'Anne', 'Jones', '1967-12-01', 'F', 4000),
                ('Jen', 'Mary', 'Brown', '1980-02-17', 'F', -1)
                ]

        columns = ["firstname", "middlename", "lastname", "dob", "gender", "salary"]

        return spark.createDataFrame(data=data, schema=columns)

    def _createSparkSession(self):
        return SparkSession.builder.getOrCreate()

    def test_save_span_properties(self):
        path = token_hex(10)
        format_name = 'csv'
        mode = 'overwrite'
        partition_by = ['firstname', 'middlename']
        try:
            df = self._createDataFrame()
            df.write.save(path, format_name, mode, partition_by)
        except Exception:
            self.fail('Failed to save')

        self.tracer_provider.force_flush()

        spans = self.span_exporter.get_finished_spans()
        self.assertEqual(1, len(spans))
        span = spans[0]
        self.assertEqual(span.name, SAVE_SPAN_NAME)

        attributes = span.attributes
        self.assertEqual(attributes.get(SPAN_ATTRIBUTES_SPARK_PATH), path)
        self.assertEqual(attributes.get(SPAN_ATTRIBUTES_SPARK_FORMAT), format_name)
        self.assertEqual(attributes.get(SPAN_ATTRIBUTES_SPARK_MODE), mode)
        self.assertEqual(attributes.get(SPAN_ATTRIBUTES_SPARK_PARTITION_BY), ','.join(partition_by))

    def test_save_as_table_span_properties(self):
        name = token_hex(10)
        format_name = 'csv'
        mode = 'overwrite'
        partition_by = ['firstname', 'middlename']
        try:
            df = self._createDataFrame()
            df.write.saveAsTable(name, format_name, mode, partition_by)
        except Exception:
            self.fail('Failed to save')

        self.tracer_provider.force_flush()

        spans = self.span_exporter.get_finished_spans()
        self.assertEqual(1, len(spans))
        span = spans[0]
        self.assertEqual(span.name, SAVE_AS_TABLE_SPAN_NAME)

        attributes = span.attributes
        self.assertEqual(attributes.get(SPAN_ATTRIBUTES_SPARK_NAME), name)
        self.assertEqual(attributes.get(SPAN_ATTRIBUTES_SPARK_FORMAT), format_name)
        self.assertEqual(attributes.get(SPAN_ATTRIBUTES_SPARK_MODE), mode)
        self.assertEqual(attributes.get(SPAN_ATTRIBUTES_SPARK_PARTITION_BY), ','.join(partition_by))

    def test_data_stream_reader_load_span_properties(self):
        host = "localhost"
        port = 9999
        path = f'{host}:{port}'
        format = 'socket'
        try:
            spark = self._createSparkSession()
            spark \
                .readStream \
                .option("host", host) \
                .option("port", port) \
                .load(path, format)
        except Exception:
            self.fail('Failed to load stream')

        self.tracer_provider.force_flush()

        spans = self.span_exporter.get_finished_spans()
        self.assertEqual(1, len(spans))
        span = spans[0]
        self.assertEqual(span.name, LOAD_STREAM_SPAN_NAME)

        attributes = span.attributes
        self.assertEqual(attributes.get(SPAN_ATTRIBUTES_SPARK_PATH), path)
        self.assertEqual(attributes.get(SPAN_ATTRIBUTES_SPARK_FORMAT), format)

    def test_data_stream_writer_start_span_properties(self):
        path = 'helios/pyspark_instrumentation/tests/data'
        json_file = f'{path}/example.json'
        output_path = f'{path}/output'
        format = 'memory'
        output_mode = 'complete'
        query_name = token_hex(10)
        try:
            spark = self._createSparkSession()
            static = spark \
                .read \
                .option("multiline", "true") \
                .json(json_file)

            data_schema = static.schema

            streaming = spark \
                .readStream \
                .schema(data_schema) \
                .option("maxFilesPerTrigger", 1) \
                .json(path)

            year_counts = streaming.groupBy("year").count()

            year_counts \
                .writeStream \
                .start(output_path, format, output_mode, None, query_name) \
                .awaitTermination(30)

        except Exception:
            self.fail('Failed to start write stream')

        self.tracer_provider.force_flush()

        spans = self.span_exporter.get_finished_spans()
        self.assertEqual(1, len(spans))
        span = spans[0]
        self.assertEqual(span.name, START_STREAM_SPAN_NAME)

        attributes = span.attributes
        self.assertEqual(attributes.get(SPAN_ATTRIBUTES_SPARK_PATH), output_path)
        self.assertEqual(attributes.get(SPAN_ATTRIBUTES_SPARK_FORMAT), format)
        self.assertEqual(attributes.get(SPAN_ATTRIBUTES_SPARK_OUTPUT_MODE), output_mode)
        self.assertEqual(attributes.get(SPAN_ATTRIBUTES_SPARK_QUERY_NAME), query_name)

    def test_instrument_uninstrument(self):
        PySparkInstrumentor().uninstrument()

        # Test Instrument
        PySparkInstrumentor().instrument(tracer_provider=self.tracer_provider)

        try:
            df = self._createDataFrame()
            df.write.mode('overwrite').saveAsTable('tableName')
        except Exception:
            self.fail('Failed to save')

        self.tracer_provider.force_flush()

        spans = self.span_exporter.get_finished_spans()
        self.assertEqual(1, len(spans))
        self.span_exporter.clear()

        # Test Uninstrument
        PySparkInstrumentor().uninstrument()

        try:
            df = self._createDataFrame()
            df.write.mode('overwrite').saveAsTable('tableName')
        except Exception:
            self.fail('Failed to save')

        self.tracer_provider.force_flush()

        spans = self.span_exporter.get_finished_spans()
        self.assertEqual(0, len(spans))
