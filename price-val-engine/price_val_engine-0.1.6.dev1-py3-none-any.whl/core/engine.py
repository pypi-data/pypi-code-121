import datetime
import socket
import warnings
from price_val_engine.conf import settings
from price_val_engine.core.data import reader, writer
from price_val_engine.core.exceptions import ImproperlyConfigured
from price_val_engine.core import utils

try:
    from slack_sdk import WebClient
except Exception as e:
    print(e)
    warnings.warn("Missing library slack-sdk. alert would not be send")
    WebClient = None
    
class BaseValidationEngine(object):
    validation_rules = settings.VALIDATION_PIPELINES
    data_reader = None
    data_writer = None
    
    def __init__(self, 
        input_file_path, 
        output_file_path,
        storage_options=None,
        validation_rules=[]
        ) -> None:
        
        self.input_file_path = input_file_path
        self.output_file_path = output_file_path
        self.storage_options = storage_options or {}
        # overide validation rules 
        if isinstance(validation_rules, (list, tuple)) and len(validation_rules):
            self.validation_rules = validation_rules
        self.items = []
        
        self.slack_client = None
        if settings.SLACK_ENABLED and WebClient:
            self.slack_client = WebClient(settings.SLACK_BOT_TOKEN)
    
    
    def __slack_message(self, item, error):
        return [
        {
	        "mrkdwn_in": ["text"],
            "color": "#d12815",
            "author_name": f"{socket.getfqdn()}({socket.gethostbyname(socket.gethostname())})",
            "title": f"{error.get('category')}",
            "fields": [
                {
                    "title": "Severity",
                    "value": f"*`{error.get('severity')}`*",
                    "short": True
                },
                {
                    "title": "Message",
                    "value": f"`{error.get('reason')}`",
                    "short": False
                },
                { 
                    "title": "Data",
                    "value": f"{str(item)}",
                    "short": False
                }
            ],
            "thumb_url": "https://www.cars24.com/js/28776e9c38260ac3339c3babe6171dd0.svg",
            "footer": "LP Revision",
            "footer_icon": "https://platform.slack-edge.com/img/default_application_icon.png",
            "ts": datetime.datetime.now().timestamp()
        }
    ]
    
    def alert(self, item, error, slacK_channel=None):
        if self.slack_client and error.get('severity') == 'HIGH':
            slacK_channel = slacK_channel or settings.SLACK_CHANNEL
            if slacK_channel == None:
                raise ImproperlyConfigured(
                    "SLACK_CHANNEL should not be blank if SLACK_ENABLED in settings file"
                )
            self.slack_client.chat_postMessage(
                channel=slacK_channel,
                text="Price Validation Engine - alert",
                attachments=self.__slack_message(item, error)
            )
        
    def all(self):
        if self.data_reader is None:
            raise ImproperlyConfigured(
                "Invalid Data Reader class !"
            )
        rows = []
        
        for row in self.data_reader(
                    file_path=self.input_file_path
                ).read():
            rows.append(row)
        return rows
        
    def validate(self, row):
        result = [] 
        for validation_cls in self.validation_rules:
            if isinstance(validation_cls, str):
                klass = utils.import_model(validation_cls)
                validation = klass()
            else:
                validation = validation_cls()
                
            if not validation.is_valid(row):
                result.append(validation.errors)
        if len(result):
            return False, result
        return True, {"category": "success", "severity": "",  "reason": "success"}
    
    def validate_all(self):
        for item in self.all():
            is_valid, response = self.validate(item)
            if is_valid:
                self.items.append({**item, 'is_valid': is_valid, **response})
            else:
                for error in response:
                    # hook to send slack alert on High severaity cases
                    self.alert(item, error)
                    self.items.append({**item, 'is_valid': is_valid, **error})
        return self.items
    
    def save(self):
        if self.data_writer is None:
            raise ImproperlyConfigured(
                "Invalid Data Writer class"
            )  
        if len(self.items):
            fieldnames = list(self.items[0].keys())
            self.data_writer(
                file_path=self.output_file_path
            ).write(self.items, headers=fieldnames)

class DataFrameValidationEngine(BaseValidationEngine):
    
    def __init__(self, DataFrame):
        self.DataFrame = DataFrame
        self.DataFrame.columns= self.DataFrame.columns.str.lower()
        self.items = []
        super().__init__(None, None)

    def all(self):
        yield from self.DataFrame.to_dict(orient='records')
    
    def to_dataframe(self):
        return self.DataFrame.__class__(self.items)
    
    def save(self):
        return self.to_dataframe()
    
    
class ValidationEngine(BaseValidationEngine):
    data_reader = reader.CSVReader
    data_writer = writer.CSVWriter
    
    
Engine = ValidationEngine