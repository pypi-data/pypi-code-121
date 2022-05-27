
import pandas as pd
import os
import re

from orangewidget.widget import OWBaseWidget, Output
from orangewidget.settings import Setting
from orangewidget import gui, widget
from orangewidget.utils.widgetpreview import WidgetPreview
import Orange.data
from Orange.data.pandas_compat import table_from_frame

from PyQt5.QtWidgets import QFileDialog
from AnyQt.QtWidgets import QStyle, QSizePolicy as Policy
from .kduino_data_analysis import KduinoDataAnalysis


class KduinoWidget(OWBaseWidget):
    
    # Widget's name as displayed in the canvas
    name = "Kduino Obs."

    # Short widget description
    description = "Get observations from kduino device"

    # An icon resource file path for this widget
    icon = "icons/kduino.png"

    # Priority in the section MECODA
    priority = 21

    # Basic (convenience) GUI definition:
    #   a simple 'single column' GUI layout
    want_main_area = False
    
    #   with a fixed non resizable geometry.
    resizing_enabled = False

    # Defining settings
    device = Setting("kdupro_rgb_v1", schema_only=True)
    path = Setting("", schema_only=True)
    #lat = Setting("", schema_only=True)
    #lon = Setting("", schema_only=True)
    cumulative = Setting(bool(1), schema_only=True)
    #starts = Setting("", schema_only=True)
    #ends = Setting("", schema_only=True)
    starts_day = Setting("", schema_only=True)
    starts_hour = Setting("", schema_only=True)
    ends_day = Setting("", schema_only=True)
    ends_hour = Setting("", schema_only=True)

    # Widget's outputs; here, a single output named "Observations", of type Table
    class Outputs:
        data = Output("Data", Orange.data.Table, auto_summary=False)
        metadata=Output("Metadata", Orange.data.Table, auto_summary=False)
        kd = Output("Kd", Orange.data.Table, auto_summary=False)
        plot = Output("Plot", Orange.data.Table, auto_summary=False)

    def __init__(self):
        # use the init method from the class OWBaseWidget
        super().__init__()

        #layout = QGridLayout()
        #layout.setSpacing(4)

        # info area
        info = gui.widgetBox(self.controlArea, "Info")

        self.infoa = gui.widgetLabel(info, 'No observations fetched yet.')
        self.infob = gui.widgetLabel(info, '')

        gui.separator(self.controlArea)

        # searchBox area
        self.searchBox = gui.widgetBox(self.controlArea, "Source")

        #dialog = QFileDialog()
        #path, __ = dialog.getOpenFileName(self, 'Select a zip file')
        #print(path)
        self.file_button = gui.button(
            self.searchBox, 
            self, 
            label="Choose folder",
            callback=self.browse_file, 
            autoDefault=False,
            width=300,
            )
        self.file_button.setIcon(self.style().standardIcon(QStyle.SP_DirOpenIcon))
        self.file_button.setSizePolicy(
            Policy.Maximum, 
            Policy.Fixed
            )

        #gui.separator(self.searchBox)
        
        self.device_line = gui.comboBox(
            self.searchBox,
            self,
            "device",
            box=None,
            label="Device:",
            labelWidth=None,
            items=("kdupro_rgb_v1", "kdupro_rgb", "kdustick", "kdupro_multispectral"),
            sendSelectedValue=True,
            emptyString=False, 
            editable=False, 
            contentsLength=None, 
            searchable=False, 
            orientation=0,
        )

        """self.lat_line = gui.lineEdit(
            self.searchBox,
            self,
            "lat",
            label="Latitude:", 
            orientation=0, 
            controlWidth=80,
            valueType=float
            )
        
        self.lon_line = gui.lineEdit(
            self.searchBox,
            self,
            "lon",
            label="Longitude:", 
            orientation=0, 
            controlWidth=80,
            valueType=float
            )"""

        self.cumulative_line = gui.comboBox(
            self.searchBox,
            self,
            "cumulative",
            box=None,
            label="Cumulative:",
            labelWidth=None,
            items=(False, True),
            sendSelectedValue=False,
            emptyString=False, 
            editable=False, 
            contentsLength=0, 
            searchable=False, 
            orientation=0,
        )

        self.startsBox = gui.widgetBox(self.controlArea, "Starts", orientation=1)

        self.starts_day_line = gui.lineEdit(
            self.startsBox,
            self,
            "starts_day",
            label="<b>Day</b> YYYY-MM-DD",
            controlWidth=140
        )

        self.starts_hour_line = gui.lineEdit(
            self.startsBox,
            self,
            "starts_hour",
            label="<b>Hour</b> HH:MM:SS",
            controlWidth=140
        )

        self.endsBox = gui.widgetBox(self.controlArea, "Ends", orientation=1)

        self.ends_day_line = gui.lineEdit(
            self.endsBox,
            self,
            "ends_day",
            label="<b>Day</b> YYYY-MM-DD",
            controlWidth=140
        )

        self.starts_hour_line = gui.lineEdit(
            self.endsBox,
            self,
            "ends_hour",
            label="<b>Hour</b> HH:MM:SS",
            controlWidth=140
        )
        #layout.addWidget(file_button, 0, 2)

        gui.separator(self.searchBox)

        # commit area
        self.commitBox = gui.widgetBox(self.controlArea, "", spacing=2)
        gui.button(self.commitBox, self, "Load", callback=self.commit)

    """def info_searching(self):
        self.infoa.setText('Loading...')"""

    def browse_file(self):
        #self.infoa.setText('Loading...')
        dialog = QFileDialog()
        home = os.path.expanduser("~")
        path_string = dialog.getExistingDirectory(self, 'Select a folder', home)
        self.path = path_string
        if path_string != "":
            self.file_button.setDisabled(True)
            pattern = r"(\d){8}"
            x = re.search(pattern, path_string)
            default_data = x.group()

            self.starts_day = f"{default_data[0:4]}-{default_data[4:6]}-{default_data[6:]}"
            self.starts_hour = "00:00:00"
            self.ends_day = f"{default_data[0:4]}-{default_data[4:6]}-{default_data[6:]}"
            self.ends_hour = "00:00:00"

        file_selected = path_string.split("data")[-1]
        self.infoa.setText(f"<b>Folder:</b><br>{file_selected}")
        
        return self.path


    def commit(self):
        self.infoa.setText('Loading...')
        self.infob.setText(f'')
        #progress = gui.ProgressBar(self, 2)
        try:
            starts_day = str(self.starts_day).replace("-", "").replace(" ", "").replace(":", "").strip()
            starts_hour = str(self.starts_hour).replace("-", "").replace(" ", "").replace(":", "").strip()
            ends_day = str(self.ends_day).replace("-", "").replace(" ", "").replace(":", "").strip()
            ends_hour = str(self.ends_hour).replace("-", "").replace(" ", "").replace(":", "").strip()
            # create doc from input
            doc = {
                'device': self.device,
                'path': self.path,
                #'lat': float(self.lat),
                #'lon': float(self.lon),
                'cumulative': bool(self.cumulative),
                'starts': [f"{starts_day}{starts_hour}"],
                'ends': [f"{ends_day}{ends_hour}"],
                'resample': 'T',
                'discard_items': None, 
                'shift': {
                    'time': None, 
                    'freq': None
                    }, 
                'r2': None, 
                'analysis': {
                    'plot': [
                        'timeseries_individual', 
                        'timeseries_buoy', 
                        'histogram', 
                        'max_diff', 
                        'scatter_matrix', 
                        'correlation_resample', 
                        'kd'
                        ]
                    }
                }
            """if self.lat != "":
                doc['lat'] = float(self.lat)
            if self.lon != "":
                doc['lon'] = float(self.lon)"""


            if doc['path'] == "":
                self.infoa.setText(f'You have to select a folder with data.')
                self.info.set_output_summary(self.info.NoOutput)
            else:
                # show progress bar
                progress = gui.ProgressBar(self, 2)
                progress.advance()
                
                kduino = KduinoDataAnalysis(doc)
                if (doc['device'] == "kdupro_rgb_v1") or (doc['device'] == "kdupro_rgb"):
                    data, kd = kduino.analysis_kduino(doc['path'])
                    kduino.plot_kduino(doc['path'])

                    if doc["cumulative"] is True:
                        cum = "cumulative"
                    else:
                        cum = "non_cumulative"

                    plot = {
                        #"category": "files/cumulative",
                        "image_name": "plot",
                        "image": os.path.join(doc['path'], "files", cum, 'plot.png'),
                        "size": 242220,
                        "width": 1800,
                        "height": 1200
                    }
                    plot_df = pd.DataFrame([plot])
                    table_plot = table_from_frame(plot_df)
                    for meta in table_plot.domain.metas:
                        if meta.name == "image":
                            meta.attributes = {"type": "image"}


                    if len(data.data) > 0:
                        metadata = pd.DataFrame.from_dict(data.metadata)

                        table_kduino = table_from_frame(data.data)
                        table_metadata = table_from_frame(metadata)
                        table_kd = table_from_frame(kd.data)
                        table_plot = table_from_frame(plot_df)

                        self.infoa.setText(f'{len(data.data)} observations gathered')
                        self.infob.setText("")

                        self.info.set_output_summary(len(data.data))

                        self.Outputs.data.send(table_kduino)
                        self.Outputs.metadata.send(table_metadata)
                        self.Outputs.kd.send(table_kd)
                        self.Outputs.plot.send(table_plot)
                    else:
                        self.infoa.setText(f'Nothing found.')
                        self.info.set_output_summary(self.info.NoOutput)
                
                else:
                    data = kduino.analysis_kduino(doc['path'])
                    if len(data.data) > 0:
                        table_kduino = table_from_frame(data.data)
                        self.infoa.setText(f'{len(data.data)} observations gathered')
                        self.infob.setText("")

                        self.info.set_output_summary(len(data.data)) 
                        self.Outputs.data.send(table_kduino)
                    else:
                        self.infoa.setText(f'Nothing found.')
                        self.info.set_output_summary(self.info.NoOutput)                 

        except ValueError:
            self.infoa.setText(f'Nothing found.')
            
        except Exception as error:
            self.infoa.setText(f'ERROR: \n{error}')
            self.infob.setText("")
            print(error)
            
        progress.finish()    
        

# For developer purpose, allow running the widget directly with python
if __name__ == "__main__":
    WidgetPreview(KduinoWidget).run()