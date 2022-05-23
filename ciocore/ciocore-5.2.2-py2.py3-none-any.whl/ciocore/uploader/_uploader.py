import datetime
import importlib
import json
import logging
import os
import sys
import time
import threading
import traceback

try:
    import Queue as queue
except ImportError:
    import queue

import ciocore
from ciocore import config
from ciocore import api_client, common, worker, client_db, loggeria
from ciocore.common import CONDUCTOR_LOGGER_NAME

from .upload_stats import UploadStats

LOG_FORMATTER = logging.Formatter(
    "%(asctime)s  %(name)s%(levelname)9s  %(threadName)s:  %(message)s"
)
logger = logging.getLogger(CONDUCTOR_LOGGER_NAME)

SINGLEPART = "singlepart"
MULTIPART = "multipart"


class MD5Worker(worker.ThreadWorker):
    """
    This worker will pull filenames from in_queue and compute it's base64 encoded
    md5, which will be added to out_queue
    """

    def __init__(self, *args, **kwargs):
        # The location of the sqlite database. If None, it will degault to a value
        self.md5_caching = kwargs.get("md5_caching")
        self.database_filepath = kwargs.get("database_filepath")
        super(MD5Worker, self).__init__(*args, **kwargs)

    def do_work(self, job, thread_int):
        logger.debug("job is %s", job)
        filename, submission_time_md5 = job
        filename = str(filename)
        current_md5, cache_hit = self.get_md5(filename)

        # if a submission time md5 was provided then check against it
        if submission_time_md5:
            logger.info("Enforcing md5 match: %s for: %s", submission_time_md5, filename)
            if current_md5 != submission_time_md5:
                message = "MD5 of %s has changed since submission\n" % filename
                message += "submitted md5: %s\n" % submission_time_md5
                message += "current md5:   %s\n" % current_md5
                message += "This is likely due to the file being written to after the user"
                message += " submitted the job but before it got uploaded to conductor"
                logger.error(message)
                raise Exception(message)
        self.metric_store.set_dict("file_md5s", filename, current_md5)
        self.metric_store.set_dict("file_md5s_cache_hit", filename, cache_hit)
        size_bytes = os.path.getsize(filename)
        
        return (filename, current_md5, size_bytes)

    def get_md5(self, filepath):
        """
        For the given filepath, return a tuple of its md5 and whether the cache was used.

        Use the sqlite db cache to retrive this (if the cache is valid), otherwise generate the md5
        from scratch
        """
        
        cache_hit = True
        
        # If md5 caching is disable, then just generate the md5 from scratch
        if not self.md5_caching:
            cache_hit = False
            return common.generate_md5(filepath, poll_seconds=5), cache_hit

        # Otherwise attempt to use the md5 cache
        file_info = get_file_info(filepath)
        file_cache = client_db.FilesDB.get_cached_file(
            file_info, db_filepath=self.database_filepath, thread_safe=True
        )
        if not file_cache:
            cache_hit = False
            logger.debug("No md5 cache available for file: %s", filepath)
            md5 = common.generate_md5(filepath, poll_seconds=5)
            file_info["md5"] = md5
            self.cache_file_info(file_info)
            return md5, cache_hit

        logger.debug("Using md5 cache for file: %s", filepath)
        return file_cache["md5"], cache_hit

    def cache_file_info(self, file_info):
        """
        Store the given file_info into the database
        """
        client_db.FilesDB.add_file(file_info, db_filepath=self.database_filepath, thread_safe=True)


class MD5OutputWorker(worker.ThreadWorker):
    """
    This worker will batch the computed md5's into self.batch_size chunks. It will send a partial
    batch after waiting self.wait_time seconds
    """

    def __init__(self, *args, **kwargs):
        super(MD5OutputWorker, self).__init__(*args, **kwargs)
        self.batch_size = 20  # the controlls the batch size for http get_signed_urls
        self.wait_time = 2
        self.batch = []

    def check_for_poison_pill(self, job):
        """we need to make sure we ship the last batch before we terminate"""
        if job == self.PoisonPill():
            logger.debug("md5outputworker got poison pill")
            self.ship_batch()
            self.mark_done()
            _thread.exit()

    # helper function to ship batch
    def ship_batch(self):
        if self.batch:
            logger.debug("sending batch: %s", self.batch)
            self.put_job(self.batch)
            self.batch = []

    @common.dec_catch_exception(raise_=True)
    def target(self, thread_int):

        while not common.SIGINT_EXIT:
            
            job = None

            try:
                logger.debug("Worker querying for job")
                job = self.in_queue.get(block=True, timeout=self.wait_time)
                logger.debug("Got job")
                queue_size = self.in_queue.qsize()                       
            
            except:
                
                logger.debug("No jobs available")
                
                if self._job_counter.value > 0:
                    
                    if self.batch:
                        self.ship_batch()
                    
                    logger.debug("Worker has completed all of its tasks ({})".format(job))
                    self.thread_complete_counter.decrement()
                    break
                
                else:
                    logger.debug("Worker waiting for first job")
                    continue
                
            logger.debug("Worker got job {}".format(job))
            self._job_counter.increment()
            logger.debug("Processing Job '{}' #{} on {}. {} tasks remaining in queue".format( job,
                                                                                              self._job_counter.value, 
                                                                                              self, 
                                                                                              queue_size))

            self.check_for_poison_pill(job)
            
            # add file info to the batch list
            self.batch.append(
                {
                    "path": job[0],
                    "hash": job[1],
                    "size": job[2],
                }
            )

            # if the batch is self.batch_size, ship it
            if len(self.batch) == self.batch_size:
                self.ship_batch()

            # mark this task as done
            self.mark_done()


class HttpBatchWorker(worker.ThreadWorker):
    """
    This worker receives a batched list of files (path, hash, size) and makes an batched http api
    call which returns a mixture of multiPartURLs (if any) and singlePartURLs (if any).

    in_queue: [
        {
            "path": "/linux64/bin/animate",
            "hash": "c986fb5f1c9ccf47eecc645081e4b108",
            "size": 2147483648
        },
        {
            "path": "/linux64/bin/tiff2ps",
            "hash": " fd27a8f925a72e788ea94997ca9a21ca",
            "size": 123
        },
    ]
    out_queue: {"multiPartURLs": [
            {
                "uploadID": "FqzC8mkGxTsLzAR5CuBv771an9D5WLthLbl_xFKCaqKEdqf",
                "filePath": "/linux64/bin/animate",
                "md5": "c986fb5f1c9ccf47eecc645081e4b108",
                "partSize": 1073741824,
                "parts": [
                    {
                        "partNumber": 1,
                        "url": "https://www.signedurlexample.com/signature1"
                    },
                    {
                        "partNumber": 2,
                        "url": "https://www.signedurlexample.com/signature1"
                    }
                ]
            }
        ],
        "singlePartURLs": [
            {
                "filePath": "/linux64/bin/tiff2ps",
                "fileSize": 123,
                "preSignedURL": "https://www.signedurlexample.com/signature2"
            }
        ]
    }
    """

    def __init__(self, *args, **kwargs):
        super(HttpBatchWorker, self).__init__(*args, **kwargs)
        self.api_client = api_client.ApiClient()
        self.project = kwargs.get("project")

    def make_request(self, job):
        uri_path = "/api/v2/files/get_upload_urls"
        headers = {"Content-Type": "application/json"}
        data = {"upload_files": job, "project": self.project}

        response_str, response_code = self.api_client.make_request(
            uri_path=uri_path,
            verb="POST",
            headers=headers,
            data=json.dumps(data),
            raise_on_error=True,
            use_api_key=True,
        )

        if response_code == 200:
            url_list = json.loads(response_str)
            return url_list
        if response_code == 204:
            return None
        raise Exception("%s Failed request to: %s\n%s" % (response_code, uri_path, response_str))
    
    def do_work(self, job, thread_int):
        logger.debug("getting upload urls for %s", job)
        result = self.make_request(job)

        # Determine which files have already been uploaded by looking at the difference betweeen
        # the file paths in job and the file paths returned by the request. Only files that need
        # to be uploaded are returned by the request
        incoming_file_paths = set([ item['path'] for item in job] )

        if result:
            
            for item_type in result.values():
                for item in item_type:
                    incoming_file_paths.remove(item['filePath'])                
        
        for path in incoming_file_paths:
            self.metric_store.increment("already_uploaded", True, path)
        
        return result

"""
This worker subscribes to a queue of list of file uploads (multipart and singlepart).

For each item on the queue, it uses the HttpBatchWorker response payload fileSize (bytes) to be
uploaded, and aggregates the total size for all uploads.

It then places a tuple of (filepath, file_size, upload, type of upload(multipart or singlepart))
onto the out_queue

The bytes_to_upload arg is used to hold the aggregated size of all files that need to be uploaded.
Note: This is stored as an [int] in order to pass it by reference, as it needs to be accessed and
reset by the caller.
"""


class FileStatWorker(worker.ThreadWorker):
    def __init__(self, *args, **kwargs):
        super(FileStatWorker, self).__init__(*args, **kwargs)

    def do_work(self, job, thread_int):
        """
        Job is a list of file uploads (multipart and singlepart) returned from File API. The
        FileStatWorker iterates through the list. For each item, it aggregates the filesize in
        bytes, and passes the upload into the UploadWorker queue.
        """

        if job:
            # iterate through singlepart urls
            for singlepart_upload in job.get("singlePartURLs", []):
                path = singlepart_upload["filePath"]
                file_size = singlepart_upload["fileSize"]
                upload_url = singlepart_upload["preSignedURL"]
                
                self.metric_store.increment("bytes_to_upload", file_size, path)
                self.metric_store.increment("num_files_to_upload")
    
                self.put_job((path, file_size, upload_url, SINGLEPART))
    
            # iterate through multipart
            for multipart_upload in job.get("multiPartURLs", []):
                path = multipart_upload["filePath"]
                file_size = multipart_upload["fileSize"]
                
                self.metric_store.increment("bytes_to_upload", file_size, path)
                self.metric_store.increment("num_files_to_upload")
    
                self.put_job((path, file_size, multipart_upload, MULTIPART))

        # make sure we return None, so no message is automatically added to the out_queue
        return None


class UploadWorker(worker.ThreadWorker):
    """
    This worker receives a either (filepath: signed_upload_url) pair or (filepath: multipart (dict))
    and performs an upload of the specified file to the provided url.
    """

    def __init__(self, *args, **kwargs):
        super(UploadWorker, self).__init__(*args, **kwargs)
        self.chunk_size = 1048576  # 1M
        self.report_size = 10485760  # 10M
        self.api_client = api_client.ApiClient()
        self.project = kwargs.get("project")

    def chunked_reader(self, filename):
        with open(filename, "rb") as fp:
            while worker.WORKING and not common.SIGINT_EXIT:
                data = fp.read(self.chunk_size)
                if not data:
                    # we are done reading the file
                    break
                # TODO: can we wrap this in a retry?
                yield data

                # report upload progress
                self.metric_store.increment("bytes_uploaded", len(data), filename)

    def do_work(self, job, thread_int):
        
        if job:
            filename = job[0]
            file_size = job[1]
            upload = job[2]
            upload_type = job[3]
    
            md5 = self.metric_store.get_dict("file_md5s", filename)
    
            try:
                if upload_type == SINGLEPART:
                    return self.do_singlepart_upload(upload, filename, file_size, md5)
                elif upload_type == MULTIPART:
                    return self.do_multipart_upload(upload, filename, md5)
    
                raise Exception("upload_type neither %s or %s" % (SINGLEPART, MULTIPART))
            except:
                logger.exception("Failed to upload file: %s because of:\n", filename)
                real_md5 = common.get_base64_md5(filename)
                error_message = "ALERT! File %s retried and still failed!\n" % filename
                error_message += "expected md5 is %s, real md5 is %s" % (md5, real_md5)
                logger.error(error_message)
                raise
            
        return None

    @common.DecRetry(retry_exceptions=api_client.CONNECTION_EXCEPTIONS, tries=5)
    def do_singlepart_upload(self, upload_url, filename, file_size, md5):
        """
        Note that for GCS we don't rely on the make_request's own retry mechanism because we need to
        recreate the chunked_reader generator before retrying the request. Instead, we wrap this
        method in a retry decorator.

        We cannot reuse make_request method for S3 because it adds auth and Transfer-Encoding
        headers that S3 does not accept.
        """

        if "amazonaws" in upload_url:
            # must declare content-length ourselves due to zero byte bug in requests library.
            # api_client.make_prepared_request docstring.
            headers = {
                "Content-Type": "application/octet-stream",
                "Content-Length": str(file_size),
            }

            with open(filename, "rb") as fh:
                # TODO: support chunked
                response = self.api_client.make_prepared_request(
                    verb="PUT",
                    url=upload_url,
                    headers=headers,
                    params=None,
                    data=fh,
                    tries=1,
                    # s3 will return a 501 if the Transfer-Encoding header exists
                    remove_headers_list=["Transfer-Encoding"],
                )

                # close response object to add back to pool, since no body is being read
                # https://requests.readthedocs.io/en/master/user/advanced/#body-content-workflow
                response.close()

                # report upload progress
                self.metric_store.increment("bytes_uploaded", file_size, filename)
        else:
            headers = {"Content-MD5": md5, "Content-Type": "application/octet-stream"}

            return self.api_client.make_request(
                conductor_url=upload_url,
                headers=headers,
                data=self.chunked_reader(filename),
                verb="PUT",
                tries=1,
                use_api_key=True,
            )

    def do_multipart_upload(self, upload, filename, md5):
        """
        Files will be split into partSize returned by the FileAPI and hydrated once all parts are
        uploaded. On successful part upload, response headers will contain an ETag. This value must
        be tracked along with the part number in order to complete and hydrate the file.
        """
        uploads = []
        complete_payload = {
            "uploadID": upload["uploadID"],
            "hash": md5,
            "completedParts": [],
            "project": self.project,
        }

        # iterate over parts and upload
        for part in upload["parts"]:
            resp_headers = self._do_multipart_upload(
                upload_url=part["url"],
                filename=filename,
                part_number=part["partNumber"],
                part_size=upload["partSize"],
            )

            if resp_headers:
                uploads.append(upload["uploadID"])
                completed_part = {
                    "partNumber": part["partNumber"],
                    "etag": resp_headers["ETag"].strip('"'),
                }
                complete_payload["completedParts"].append(completed_part)

        # Complete multipart upload in order to hydrate file for availability
        uri_path = "/api/v2/files/multipart/complete"
        headers = {"Content-Type": "application/json"}
        self.api_client.make_request(
            uri_path=uri_path,
            verb="POST",
            headers=headers,
            data=json.dumps(complete_payload),
            raise_on_error=True,
            use_api_key=True,
        )

        return uploads

    @common.DecRetry(retry_exceptions=api_client.CONNECTION_EXCEPTIONS, tries=5)
    def _do_multipart_upload(self, upload_url, filename, part_number, part_size):
        with open(filename, "rb") as fh:
            # seek to the correct part position
            start = (part_number - 1) * part_size
            fh.seek(start)

            # read up to part size determined by file-api
            data = fh.read(part_size)
            content_length = len(data)

            # upload part
            response = self.api_client.make_prepared_request(
                verb="PUT",
                url=upload_url,
                headers={"Content-Type": "application/octet-stream"},
                params=None,
                data=data,
                tries=1,
                remove_headers_list=[
                    "Transfer-Encoding"
                ],  # s3 will return a 501 if the Transfer-Encoding header exists
            )

            # report upload progress
            self.metric_store.increment("bytes_uploaded", content_length, filename)

            # close response object to add back to pool
            # https://requests.readthedocs.io/en/master/user/advanced/#body-content-workflow
            response.close()

            return response.headers


class Uploader(object):

    sleep_time = 10
    
    CLIENT_NAME = "Uploader"

    def __init__(self, args=None):
        logger.debug("Uploader.__init__")
        self.api_client = api_client.ApiClient()
        self.args = args or {}
        logger.debug("args: %s", self.args)

        self.location = self.args.get("location")
        self.project = self.args.get("project")
        self.progress_callback = None
        self.cancel = False
        self.error_messages = []
        self.num_files_to_process = 0
        
        self.report_status_thread = None
        self.monitor_status_thread = None
        
    def emit_progress(self, upload_stats):
        
        if self.progress_callback:        
            self.progress_callback(upload_stats)

    def prepare_workers(self):
        logger.debug("preparing workers...")
        
        if isinstance(threading.current_thread(), threading._MainThread):
            common.register_sigint_signal_handler()
        self.manager = None

    def create_manager(self, project):
       
        job_description = [
            (
                MD5Worker,
                [],
                {
                    "thread_count": self.args["thread_count"],
                    "database_filepath": self.args["database_filepath"],
                    "md5_caching": self.args["md5_caching"],
                },
            ),
            (   
                MD5OutputWorker, [], {"thread_count": 1}
            ),
            (
                HttpBatchWorker,
                [],
                {"thread_count": self.args["thread_count"], "project": project},
            ),
            (   
                FileStatWorker, [], {"thread_count": 1}
            ),
            (
                UploadWorker, [], {"thread_count": self.args["thread_count"]}
            ),
        ]

        manager = worker.JobManager(job_description)
        manager.start()
        return manager

    @common.dec_catch_exception(raise_=True)
    def report_status(self):
        logger.debug("started report_status thread")
        update_interval = 5
        while True:

            # don't report status if we are doing a local_upload
            if not self.upload_id:
                logger.debug("not updating status as we were not provided an upload_id")
                return

            if self.working:
                bytes_to_upload = self.manager.metric_store.get("bytes_to_upload")
                bytes_uploaded = self.manager.metric_store.get("bytes_uploaded")
                try:
                    status_dict = {
                        "upload_id": self.upload_id,
                        "transfer_size": bytes_to_upload,
                        "bytes_transfered": bytes_uploaded,
                    }
                    logger.debug("reporting status as: %s", status_dict)
                    self.api_client.make_request(
                        "/uploads/%s/update" % self.upload_id,
                        data=json.dumps(status_dict),
                        verb="POST",
                        use_api_key=True,
                    )

                except Exception:
                    logger.error("could not report status:")
                    logger.error(traceback.print_exc())
                    logger.error(traceback.format_exc())
                    
            else:
                break

            time.sleep(update_interval)

    def create_report_status_thread(self):
        logger.debug("creating reporter thread")
        self.report_status_thread = threading.Thread(name="ReporterThread", target=self.report_status)
        self.report_status_thread.daemon = True
        self.report_status_thread.start()

    @common.dec_catch_exception(raise_=True)
    def monitor_status(self, progress_handler):
        logger.debug("starting monitor_status thread")
        update_interval = 0.5

        def sleep():
            time.sleep(update_interval)

        while True:
            if self.working:
                try:
                    upload_stats = UploadStats.create (self.manager.metric_store, self.num_files_to_process, self.job_start_time)
                    progress_handler(upload_stats)
                except Exception as e:
                    print(e)
                    print(traceback.format_exc())
                    
            else:
                break
            sleep()

    def create_monitor_status_thread(self):
        logger.debug("creating console status thread")
        self.monitor_status_thread = threading.Thread(name="PrintStatusThread", target=self.monitor_status, args=(self.emit_progress,))

        # make sure threads don't stop the program from exiting
        self.monitor_status_thread.daemon = True

        # start thread
        self.monitor_status_thread.start()

    def mark_upload_finished(self, upload_id, upload_files):

        data = {"upload_id": upload_id, "status": "server_pending", "upload_files": upload_files}

        self.api_client.make_request(
            "/uploads/%s/finish" % upload_id, data=json.dumps(data), verb="POST", use_api_key=True
        )
        return True

    def mark_upload_failed(self, error_message, upload_id):
        logger.error("failing upload due to: \n%s" % error_message)

        # report error_message to the app
        self.api_client.make_request(
            "/uploads/%s/fail" % upload_id, data=error_message, verb="POST", use_api_key=True
        )

        return True

    def handle_upload_response(self, project, upload_files, upload_id=None):
        """
        This is a really confusing method and should probably be split into to clear logic
        branches: one that is called when in daemon mode, and one that is not. If not called in
        daemon mode (local_upload=True), then md5_only is True and project is not None.Otherwise
        we're in daemon mode, where the project information is not required because the daemon will
        only be fed uploads by the app which have valid projects attached to them.
        """
        try:

            logger.info("%s", "  NEXT UPLOAD  ".center(30, "#"))
            logger.info("project: %s", project)
            logger.info("upload_id is %s", upload_id)
            logger.info(
                "upload_files %s:(truncated)\n\t%s",
                len(upload_files),
                "\n\t".join(list(upload_files)[:5]),
            )

            # reset counters
            self.num_files_to_process = len(upload_files)
            logger.debug( "Processing {} files".format(self.num_files_to_process))
            self.job_start_time = datetime.datetime.now()
            self.upload_id = upload_id
            self.job_failed = False

            # signal the reporter to start working
            self.working = True

            self.prepare_workers()
            
            # create worker pools
            self.manager = self.create_manager(project)

            # create reporters
            logger.debug("creating report status thread...")
            self.create_report_status_thread()

            # load tasks into worker pools
            for path in upload_files:
                md5 = upload_files[path]
                self.manager.add_task((path, md5))

            logger.info("creating console status thread...")
            self.create_monitor_status_thread()                

            #wait for work to finish
            while not self.manager.is_complete():
                logger.info("Manager is running, cancel requested?: {}".format(self.cancel))
                
                if self.cancel or self.manager.error:
                    self.error_messages = self.manager.stop_work()
                    logger.debug("Manager sucesfully stopped")
                    break
                
                time.sleep(1)
                
            # Shutdown the manager once all jobs are done
            if not self.cancel and not self.manager.error:    
                logger.debug("Waiting for Manager to join")            
                self.manager.join()

            upload_stats = UploadStats.create(self.manager.metric_store, self.num_files_to_process, self.job_start_time)
            logger.info(upload_stats.get_formatted_text())
            self.emit_progress(upload_stats)            
            
            logger.debug("error_message: %s", self.error_messages)

            # signal to the reporter to stop working
            self.working = False
            logger.info("done uploading files")
            
            logger.debug("Waiting for reporter status thread to join")
            self.report_status_thread.join()
            
            logger.debug("Waiting for print status thread to join")
            self.monitor_status_thread.join()            

            #  Despite storing lots of data about new uploads, we will only send back the things
            #  that have changed, to keep payloads small.
            finished_upload_files = {}
            if self.upload_id:
                md5s = self.return_md5s()
                for path in md5s:
                    finished_upload_files[path] =  {"source": path, "md5": md5s[path]}

                self.mark_upload_finished(self.upload_id, finished_upload_files)

        except:
            self.error_messages.append(sys.exc_info())

    def main(self, run_one_loop=False):
        
        def show_ouput(upload_stats):
            logger.info(upload_stats.get_formatted_text())
            
        self.progress_callback = show_ouput
        
        logger.info("Uploader Started. Checking for uploads...")

        while not common.SIGINT_EXIT:
            try:
                # TODO: we should pass args as url params, not http data
                data = {}
                data["location"] = self.location
                logger.debug("Data: %s", data)
                resp_str, resp_code = self.api_client.make_request(
                    "/uploads/client/next", data=json.dumps(data), verb="PUT", use_api_key=True
                )
                if resp_code == 204:
                    logger.debug("no files to upload")
                    sys.stdout.write(".")
                    sys.stdout.flush()
                    time.sleep(self.sleep_time)
                    continue
                elif resp_code != 201:
                    logger.error("received invalid response code from app %s", resp_code)
                    logger.error("response is %s", resp_str)
                    time.sleep(self.sleep_time)
                    continue

                print("")  # to make a newline after the 204 loop

                try:
                    json_data = json.loads(resp_str)
                    upload = json_data.get("data", {})
                except ValueError:
                    logger.error("response was not valid json: %s", resp_str)
                    time.sleep(self.sleep_time)
                    continue

                upload_files = upload["upload_files"]
                upload_id = upload["id"]
                project = upload["project"]

                self.handle_upload_response(project, upload_files, upload_id)
                
                error_message = []
                
                for exception in self.error_messages:
                    
                    error_message.append("{}: {}".format(exception[1], 
                                                         traceback.format_tb(exception[2])))
                    
                if error_message:
                    self.mark_upload_failed("\n".join(error_message, upload_id))
                
                self.error_messages = []

            except KeyboardInterrupt:
                logger.info("ctrl-c exit")
                break
            except:
                logger.exception("Caught exception:\n")
                time.sleep(self.sleep_time)
                continue

        logger.info("exiting uploader")

    def return_md5s(self):
        """
        Return a dictionary of the filepaths and their md5s that were generated
        upon uploading
        """
        return self.manager.metric_store.get_dict("file_md5s")

def set_logging(level=None, log_dirpath=None):
    log_filepath = None
    if log_dirpath:
        log_filepath = os.path.join(log_dirpath, "conductor_ul_log")
    loggeria.setup_conductor_logging(
        logger_level=level,
        console_formatter=LOG_FORMATTER,
        file_formatter=LOG_FORMATTER,
        log_filepath=log_filepath,
    )


def run_uploader(args):
    """
    Start the uploader process. This process will run indefinitely, polling
    the Conductor cloud app for files that need to be uploaded.
    """
    # convert the Namespace object to a dictionary
    args_dict = vars(args)
    cfg = config.config().config
    
    api_client.ApiClient.register_client(client_name = Uploader.CLIENT_NAME, client_version=ciocore.__version__) 

    # Set up logging
    log_level_name = args_dict.get("log_level") or cfg["log_level"]
    log_level = loggeria.LEVEL_MAP.get(log_level_name)
    log_dirpath = args_dict.get("log_dir")
    set_logging(log_level, log_dirpath)
    logger.debug("Uploader parsed_args is %s", args_dict)
    resolved_args = resolve_args(args_dict)
    uploader = Uploader(resolved_args)
    uploader.main()


def get_file_info(filepath):
    """
    For the given filepath return the following information in a dictionary:

        "filepath": filepath (str)
        "modtime": modification time (datetime.datetime)
        "size": filesize in bytes (int)

    """
    assert os.path.isfile(filepath), "Filepath does not exist: %s" % filepath
    stat = os.stat(filepath)
    modtime = datetime.datetime.fromtimestamp(stat.st_mtime)

    return {"filepath": filepath, "modtime": modtime, "size": stat.st_size}


def resolve_args(args):
    """
    Resolve all arguments, reconciling differences between command line args and config.yml args.
    See resolve_arg function.
    """
    
    args["md5_caching"] = resolve_arg("md5_caching", args)
    args["database_filepath"] = resolve_arg("database_filepath", args)
    args["location"] = resolve_arg("location", args)
    args["thread_count"] = resolve_arg("thread_count", args)

    return args

def resolve_arg(key, args):
    """
    If the key doesn't exist (or is None), grab it from the config.
    """
    
    cfg = config.config().config
    config_value = cfg.get(key) 
    
    value = args.get(key, config_value)
    
    if value is None:
        value = config_value
        
    return value
 
