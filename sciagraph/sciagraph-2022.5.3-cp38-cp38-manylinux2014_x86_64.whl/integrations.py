"""Third-party integrations."""

from zipfile import ZipFile, ZIP_DEFLATED
import logging
from tempfile import mkdtemp
from pathlib import Path

from .api import ReportResult


class _MLflowHandler(logging.Handler):
    def __init__(self, artifact_path):
        # mlflow does some atexit.register(), if mlflow only gets imported at
        # the end of the process during logging of reports... that's in atexit,
        # so it blows up. Also, better to fail early rather than later.
        import mlflow  # type: ignore

        del mlflow

        self._artifact_path = artifact_path
        logging.Handler.__init__(self)

    def emit(self, record):
        if isinstance(record.msg, ReportResult) and record.msg.report_path is not None:
            from mlflow import log_artifact  # type: ignore

            zip_path = Path(mkdtemp()) / "sciagraph-report.zip"
            zip_file = ZipFile(zip_path, "w", compresslevel=ZIP_DEFLATED)
            for path in record.msg.report_path.iterdir():
                zip_file.write(path, path.name)
            zip_file.close()
            log_artifact(zip_path, self._artifact_path)


def install_mlflow_handler():
    """
    Store the Sciagraph report using the MLflow Tracking API.
    """
    logging.getLogger("sciagraph").addHandler(
        _MLflowHandler("Sciagraph profiling report")
    )


__all__ = ["install_mlflow_handler"]
