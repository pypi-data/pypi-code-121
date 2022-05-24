"""
etl_job.py
~~~~~~~~~~

This Python module contains an example Apache Spark ETL job definition
that implements best practices for production ETL jobs. It can be
submitted to a Spark cluster (or locally) using the 'spark-submit'
command found in the '/bin' directory of all Spark distributions
(necessary for running any Spark job, locally or otherwise). For
example, this example script can be executed as follows,

    $SPARK_HOME/bin/spark-submit \
    --master spark://localhost:7077 \
    --py-files packages.zip \
    --files configs/etl_config.json \
    jobs/etl_job.py

where packages.zip contains Python modules required by ETL job (in
this example it contains a class to provide access to Spark's logger),
which need to be made available to each executor process on every node
in the cluster; etl_config.json is a text file sent to the cluster,
containing a JSON object with all of the configuration parameters
required by the ETL job; and, etl_job.py contains the Spark application
to be executed by a driver process on the Spark master node.

For more details on submitting Spark applications, please see here:
http://spark.apache.org/docs/latest/submitting-applications.html

Our chosen approach for structuring jobs is to separate the individual
'units' of ETL - the Extract, Transform and Load parts - into dedicated
functions, such that the key Transform steps can be covered by tests
and jobs or called from within another environment (e.g. a Jupyter or
Zeppelin notebook).
"""

import os
import sys
import json
import argparse
import traceback

from dependencies import enrich


def add_data(config):

    sqlsc = config["sqlsc"]
    root = config["root"]
    data = {}
    for name, path in config["data"].items():
        filename = os.path.join(root, path)
        df = sqlsc.read.csv(filename, header=True, mode="DROPMALFORMED", sep=",")

        data[name] = df.rdd

    config["rdds"] = data


def run(config):

    from dependencies import supernova

    add_data(config)

    params = config["params"]

    # Initialize the tagger...
    tagging_extra = supernova.initialize(params)

    rdd = config["rdds"]["members"]

    def reducefunc(g):
        key = g[0]
        rows = g[1]
        rows = list(rows)

        # All elements are text. So fix the types..

        # Now run the tagger..
        records = supernova.process(rows, tagging_extra)

        print("LOOKING AT KEY", key)
        print("LOOKING AT ROWS", rows)
        result = (key, len(rows))
        print("RESULT", result)
        return {"key": key, "len": len(rows)}

    def grouping(row):
        return tuple([row[x] for x in ["MEMBERSHIP_ID", "bdate", "storenmbr"]])

    grouped = rdd.groupBy(grouping)

    collected = grouped.map(reducefunc)
    print("GROUPED COLLECT", collected.take(2))

    collected = collected.collect()

    print("COLLECTED", collected)


# entry point for PySpark ETL application
if __name__ == "__main__":

    # => Load configuration and pass any additional parameters...
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Configuration file")
    args = parser.parse_args()
    config = json.load(open(args.config))
    config["root"] = os.path.dirname(args.config)

    # Start the spark session
    enrich.start_spark_session(config)

    # Run the code...
    try:
        run(config)
    except:
        traceback.print_exc()

    # Shut down
    enrich.stop_spark_session(config)
