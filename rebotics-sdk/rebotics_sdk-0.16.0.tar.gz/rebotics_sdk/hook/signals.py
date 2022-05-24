import django.dispatch

EVENTS = (
    ('report.ready', 'Report ready'),
    ('import.finish', 'Import finish'),
    ('processing.finish', 'Processing finish'),
    ('scan_batch.report.ready', 'Scan batch report ready')
)

# events
WEBHOOK_RECEIVED = django.dispatch.Signal()
IMPORT_FINISH = django.dispatch.Signal()
PROCESSING_FINISH = django.dispatch.Signal()
SCAN_BATCH_REPORT_READY = django.dispatch.Signal()

# statuses
IMPORT_FINISH_ERROR = django.dispatch.Signal()
IMPORT_FINISH_SUCCESS = django.dispatch.Signal()
PROCESSING_FINISH_ERROR = django.dispatch.Signal()
PROCESSING_FINISH_SUCCESS = django.dispatch.Signal()

EVENT_SIGNALS = {
    'report.ready': WEBHOOK_RECEIVED,
    'import.finish': WEBHOOK_RECEIVED,
    'processing.finish': PROCESSING_FINISH,
    'scan_batch.report.ready': SCAN_BATCH_REPORT_READY,
}


class SignalEmitter(object):
    def __init__(self, retailer, event, payload):
        self.retailer = retailer
        self.payload = payload
        self.event = event

    def send_signal(self, signal):
        signal.send_robust(
            sender=self,
            retailer=self.retailer,
            event=self.event,
            payload=self.payload
        )

    def emit_status(self):
        if self.event == 'import.finish':
            if self.payload.get('status', None) == 'done':
                self.send_signal(IMPORT_FINISH_SUCCESS)
            elif self.payload.get('status', None) == 'error':
                self.send_signal(IMPORT_FINISH_ERROR)
        elif self.event == 'processing.finish':
            if self.payload.get('status', None) == 'success':
                self.send_signal(PROCESSING_FINISH_SUCCESS)
            elif self.payload.get('status', None) == 'error':
                self.send_signal(PROCESSING_FINISH_ERROR)

    def emit(self):
        self.send_signal(EVENT_SIGNALS[self.event])
        self.emit_status()
