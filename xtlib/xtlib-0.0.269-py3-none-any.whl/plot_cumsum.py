# plot_lines.py: displays hyperparameter searches over models as line plots (x=% of runss, y=accuracy acheived)
import os
import sys
import yaml
import numpy as np

import matplotlib.pyplot as plt

from xtlib.console import console
from xtlib.report_builder import ReportBuilder   

class CumsumPlots():
    def __init__(self, config, store) -> None:
        self.cumulative = True
        self.buckets = 20
        self.artist_infos = []
        self.metric_names = []
        self.metric_index = 0
        self.models = []
        self.config = config
        self.store = store
        self.metric_names = None
        self.figure_title = None
        self.run_dict = {}
        self.artists = []
        self.model_names = []
        self.hyperparameter_info = None
        self.all_stats = []
        self.all_metrics_dict = []

    def hide_toolbar(self, fig):
        from PyQt5 import QtWidgets 
        try:
            win = fig.canvas.manager.window
        except AttributeError:
            win = fig.canvas.window()
        toolbar = win.findChild(QtWidgets.QToolBar)
        toolbar.setVisible(False)


    def set_tooltip(self, text):
        from PyQt5.QtWidgets import QToolTip

        win = self.fig.canvas.window()

        if text:
            win.setToolTip(text)
        else:
            win.setToolTip(text)
            QToolTip.hideText()
            
    def get_data_for_jobs(self, store, job_id, metric_names, model_name, run_dict, hyperparameter_info):
        # top_x = get_top_k_values(x, 1000)
        only_show_completed = False

        full_metric_names = ["metrics." + metric for metric in metric_names]
        
        filter_dict = {"job_id": job_id}
        fields_dict = {"status": 1, "job_id": 1, "run_name": 1, "last_time": 1}

        # if only_show_completed:
        #     filter_dict["end_id"] = {"$exists": True}

        for name in hyperparameter_info:
            fields_dict["hparams." + name] = 1

        for name in full_metric_names:
            #filter_dict[name] = {"$exists": True}
            fields_dict[name] = 1
        
        new_runs = store.get_all_runs("job", "tpx", job_id, filter_dict=filter_dict, fields_dict=fields_dict, use_cache=False)

        all_values = {}
        if new_runs:
            for run in new_runs:
                run_dict[run["run_name"]] = run

            for name in metric_names:
                values = [record["metrics"][name] for record in new_runs if name in record["metrics"]]
                run_names = [record["run_name"] for record in new_runs if name in record["metrics"]]
                all_values[name] = (values, run_names)

        stats = {"job": job_id, "model": model_name}

        for i, status in enumerate(["error", "running", "cancelled", "completed"]):
            runs = [record for record in new_runs if record["status"] == status]
            count = len(runs)
            stats[status] = count

        return all_values, stats


    def get_norm_bins(self, values):
        bins, info = np.histogram(values, bins=self.buckets, range=(0, 1))

        total = sum(bins)
        norm_values = np.array(bins)/total

        # set x to max of each bucket
        x = info[1:]  

        return x, norm_values

    def build_xy(self, values):
        x, y = self.get_norm_bins(values)

        if self.cumulative:
            y = np.cumsum(y) # [::-1])
            
        return x, y

    def update_tooltip(self, found_artists):
        text = ""

        for ai, index_ary in found_artists:
            indexes = list(index_ary["ind"])
            model_name = ai["model_name"]
            job_id = ai["job_id"]
            x = ai["x"]
            y = ai["y"]

            for index in indexes:

                if text:
                    text += "<br><br>"

                bucket_max = x[index]
                bucket_min = bucket_max - 1/self.buckets
                mass = y[index]

                text += \
                    "<b>model: </b>{}" \
                    "<br><b>job: </b>{}" \
                    "<br><b>bucket: </b>[{:.4f}, {:.4f}]"\
                    "<br><b>cumulative mass: </b>{:.4f}" \
                    .format(model_name, job_id, bucket_min, bucket_max, mass)

                # for now, just show first item seen
                #break

        self.set_tooltip(text)

    def hover(self, event):
        # find the artist associated with the mouseover event
        found_artists = []

        for ai in self.artist_infos:
            artist = ai["artist"]
            cont, ind = artist.contains(event)
            if cont and len(ind):
                found_artists.append( (ai, ind) )

        if found_artists:
            self.update_tooltip(found_artists)
        else:
            self.set_tooltip("")

    def build_metric_plot(self, metric_index):

        # clear stuff associated with plots
        self.run_dict = {}
        self.artists = []
        self.artist_infos = []
        self.fig.clear()

        self.metric_index = metric_index
        metric_name = self.metric_names[self.metric_index]

        print("building plot for: {}".format(metric_name))

        title = "{}: {}".format(self.figure_title, metric_name)
        plt.title(title)

        md_index = 0

        for md in self.models:
            if "job" in md and md["job"]:
                job_id = md["job"]
                model_name = md["model"]
                #metrics_dict, stats = self.get_data_for_jobs(self.store, job_id, self.metric_names, model_name, self.run_dict, self.hyperparameter_info)

                metrics_dict = self.all_metrics_dict[md_index]
                md_index += 1

                # build x, y for this model
                if metric_name in metrics_dict:
                    values = metrics_dict[metric_name][0]
                    x, y = self.build_xy(values)

                    #artist, = plt.plot(x, y)
                    artist = plt.scatter(x, y, s=20, alpha=.7)
                    plt.plot(x, y, alpha=.7)

                    self.artists.append(artist)
                    self.model_names.append(model_name)
                    ai = {"artist": artist, "model_name": model_name, "job_id": job_id, "x": x, "y": y}
                    self.artist_infos.append(ai)

        self.finish_plot()

    def finish_plot(self):
        from PyQt5.QtWidgets import QPushButton

        plt.ylabel("% of runs")
        plt.xlabel("model accuracy")

        if self.cumulative:
            plt.ylim(1, 0)

        # show values for accuracy
        plt.xticks( [0, .1, .2, .3, .4, .5, .6, .7, .8, .9, 1] )

        plt.legend(self.artists, self.model_names)

        self.fig.canvas.mpl_connect("motion_notify_event", self.hover)

        win = self.fig.canvas.window()
        button = QPushButton('Next', win)
        button.setToolTip('Redraw plot with next available metric')
        button.move(70, 0)
        #win.verticalLayout.addWidget(button, alignment=QtCore.Qt.AlignRight)
        button.clicked.connect(self.next_metric)

        plt.draw()

    def next_metric(self, event):
        metric_index = (self.metric_index + 1) % (len(self.metric_names))
        self.build_metric_plot(metric_index)
    
    def read_data_for_models(self):

        for md in self.models:
            if "job" in md and md["job"]:
                job_id = md["job"]
                model_name = md["model"]
                metrics_dict, stats = self.get_data_for_jobs(self.store, job_id, self.metric_names, model_name, self.run_dict, self.hyperparameter_info)

                self.all_stats.append(stats)
                self.all_metrics_dict.append(metrics_dict)

    def build_plot(self, workspace, fn_summary, show_plot=False):

        # hide normal XT output (specifically about retreiving rows from DB)
        console.set_level("none")

        if os.path.isdir(fn_summary):
            # add default filename to specified path
            fn_summary += "/hp_summary.yaml"

        with open(fn_summary, "rt") as infile:
            sdf = yaml.safe_load(infile)  

        sd = sdf["hp_summary"]
        metric_info = sd["metric_info"]
        models = sd["models"]
        pubs = sd["pubs"]
        hyperparameter_info = sd["hyperparameter_info"]
        figure = sd["figure"]
        width = figure["width"]
        height = figure["height"]
        self.figure_title = figure["title"]

        self.fig = plt.figure("xt plot cumsum", figsize=(width, height))
        self.hide_toolbar(self.fig)

        self.models = models
        self.hyperparameter_info = hyperparameter_info
        self.metric_names = list(metric_info.keys())

        hyperparameter_info = sd["hyperparameter_info"]
        
        self.read_data_for_models()

        # print report of all_stats
        builder = ReportBuilder(self.config, self.store)
        text, rows = builder.build_formatted_table(self.all_stats)
        print(text)

        # this triggers the actual plotting
        self.build_metric_plot(len(self.metric_names)-1)

        plt.tight_layout()

        if show_plot:
            plt.show()


if __name__ == "__main__":
    from xtlib.helpers.xt_config import get_merged_config
    from xtlib.storage.store import Store
    
    config = get_merged_config()
    store = Store(config=config)

    line_plot = CumsumPlots(config, store)
    line_plot.build_plot(True)


