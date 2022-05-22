# plot_rings.py: plots multiple stats for multiple models for a task, summarizing a hyperparameter search
import os
import sys
import yaml
import arrow
import numpy as np

import matplotlib.pyplot as plt

from xtlib import utils
from xtlib.console import console
from xtlib.report_builder import ReportBuilder   

def hide_toolbar(fig):
    from PyQt5 import QtWidgets 
    try:
        win = fig.canvas.manager.window
    except AttributeError:
        win = fig.canvas.window()
    toolbar = win.findChild(QtWidgets.QToolBar)
    toolbar.setVisible(False)

class RingPlots():
    def __init__(self, config, store) -> None:
        self.config = config
        self.store = store
        self.artists = {}
        self.artist_infos = []
        self.artist_names = []
        self.models = []
        self.group_separators = []
        self.group_names = []
        self.metrics = None
        self.run_dict = {}
        self.all_stats = []
        self.metric_colors = None
        self.model_names = []
        self.last_tip = 0

    def get_data_for_jobs(self, store, workspace, job_id, metrics, model_name, run_dict, hyperparameter_info):
        # top_x = get_top_k_values(x, 1000)
        only_show_completed = False

        full_metric_names = ["metrics." + metric for metric in metrics]
        
        filter_dict = {"ws_name": workspace, "job_id": job_id}
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

            for name in metrics:
                values = [record["metrics"][name] for record in new_runs if name in record["metrics"]]
                run_names = [record["run_name"] for record in new_runs if name in record["metrics"]]
                all_values[name] = (values, run_names)

        stats = {"job": job_id, "model": model_name}
        #print("{} ({}): ".format(job_id, model_name), end="")

        for i, status in enumerate(["error", "running", "cancelled", "completed"]):
            runs = [record for record in new_runs if record["status"] == status]
            count = len(runs)
            stats[status] = count

        return all_values, stats

    def add_tooltips(self, fig, ax, artist_infos, run_dict, pubs, hyperparameter_info):

        def update_tooltip(ai, index):
            indexes = list(index["ind"])

            if "run_names" in ai:
                run_names = ai["run_names"]
                metric_name = ai["metric_name"]

                # get information about run
                text = ""
                for index in indexes:
                    run_name = run_names[index]
                    rd = run_dict[run_name]

                    last_time = rd["last_time"]
                    lt_value = arrow.get(last_time)
                    timestamp = lt_value.format('YYYY-MM-DD @HH:mm:ss')
                    metrics = rd["metrics"]
                    
                    if text:
                        text += "\n"
                    text += \
                        "<b>{}:</b> {:.4f}" \
                        "<br><b>name: </b>{}" \
                        "<br><b>status: </b>{}"\
                        "<br><b>updated: </b>{}" \
                        .format(metric_name, metrics[metric_name], rd["run_name"], rd["status"], timestamp)

                    for name in hyperparameter_info:
                        text += "<br><b>{}:</b> {}".format(name, rd["hparams"][name])
                    break

            elif "pub_names" in ai:
                all_pub_names = ai["pub_names"]
                text = ""
                for index in indexes:
                    pub_name = all_pub_names[index]
                    pub = pubs[pub_name]
                    metrics = pub["metrics"]
                    metric_name, metric_value = next(iter(metrics.items()))

                    if text:
                        text += "\n"
                    text += "<b>{}: </b> {:.4f}" \
                        "<br><b>Author: </b>{}" \
                        "<br><b>Year: </b>{}" \
                        "<br><b>Model: </b>{}" \
                             .format(metric_name, metric_value, pub["name"], pub["year"], pub["model"])
                    break

            win = fig.canvas.window()
            win.setToolTip(text)

        def hover(event):
            from PyQt5.QtWidgets import QToolTip
            
            # find the artist associated with the mouseover event
            found = False

            if event.inaxes == ax:
                for ai in artist_infos:
                    artist = ai["artist"]
                    cont, ind = artist.contains(event)
                    if cont and len(ind):
                        update_tooltip(ai, ind)
                        found = True
                        break

            if not found: 
                win = fig.canvas.window()
                win.setToolTip("")
                QToolTip.hideText()

        fig.canvas.mpl_connect("motion_notify_event", hover)


    def get_pub_metrics(self, pub_names, pubs):
        all_values = []

        for pub_name in pub_names:
            # # TEMP 
            # if isinstance(pub_name, float):
            #     all_values.append(pub_name)
            #     continue

            if not pub_name in pubs:
                raise Exception("pubs entry not found for: {}".format(pub_name))

            entry = pubs[pub_name]
            metrics = entry["metrics"]
            values = list(metrics.values())
            all_values += values

        return all_values

    def process_model(self, workspace, md, pubs, ax, series, group_count, series_count, hyperparameter_info):
        y_value = (series_count-1) - series

        if "group" in md:
            # group separator entry
            y_separator = y_value + .5
            name = md["group"]
            self.group_separators.append(y_separator)
            self.group_names.append(name)
            return None

        # get data 
        model_name = md["model"]
        job = md["job"]
        pub_names = md["pubs"]
        sz = 72
        spacing_factor = .25

        if job:
            metrics_dict, stats = self.get_data_for_jobs(self.store, workspace, job, self.metrics, model_name, self.run_dict, hyperparameter_info)
            if metrics_dict:
                self.all_stats.append(stats)

                for v, (name, (values, run_names)) in enumerate(metrics_dict.items()):
                    circle_y = y_value + (v-1)*spacing_factor
                    y = [circle_y]*len(values)
                    cr = self.metric_colors[v]
                    artist = ax.scatter(values, y, alpha=.4, s=sz//4, color=cr, facecolors="none")
                    #artist.set_facecolor((1, 1, 1, 0))
                    self.artists[self.artist_names[v]] = artist
                    ai = {"artist": artist, "run_names": run_names, "metric_name": name}
                    self.artist_infos.append(ai)

        if pub_names:
            pubs_values = self.get_pub_metrics(pub_names, pubs)
            y = [y_value]*len(pubs_values)
            artist = ax.scatter(pubs_values, y, alpha=.7, s=sz, color="red", facecolors='none')
            #artist.set_facecolor((1, 1, 1, 0))
            metric_name = self.artist_names[3]
            self.artists[metric_name] = artist
            ai = {"artist": artist, "pub_names": pub_names}
            self.artist_infos.append(ai)

        return model_name

    def build(self, workspace, fn_summary, show_plot=False):

        if os.path.isdir(fn_summary):
            # add default filename to specified path
            fn_summary += "/hp_summary.yaml"

        with open(fn_summary, "rt") as infile:
            sdf = yaml.safe_load(infile)  

        sd = sdf["hp_summary"]
        metric_info = sd["metric_info"]
        models = sd["models"]
        pubs = sd["pubs"]
        figure = sd["figure"]
        hyperparameter_info = sd["hyperparameter_info"]
        
        width = figure["width"]
        height = figure["height"]
        self.fig = plt.figure("xt plot rings", figsize=(width, height))
        hide_toolbar(self.fig)

        self.metrics = list(metric_info.keys())
        self.metric_colors = list([mv["color"] for mv in metric_info.values()])

        ax = self.fig.add_subplot(1, 1, 1)
        #models.reverse()

        series = 0
        self.artist_names = ["train-acc", "test-acc", "gen-acc", "pub-gen-acc"]

        group_count = len([m for m in models if "group" in m])
        series_count = len([m for m in models if not "group" in m])

        # hide normal XT output (specifically about retreiving rows from DB)
        console.set_level("none")

        for i, md in enumerate(models):
            model_name = self.process_model(workspace, md, pubs, ax, series, group_count, series_count, hyperparameter_info)
            if model_name:
                series += 1
                self.model_names.append(model_name)

        # restore normal XT output (specifically about retreiving rows from DB)
        console.set_level("normal")

        figure_title = figure["title"]
        ax.title.set_text(figure_title)
        ax.grid(axis="x", alpha=.2)
        
        yticks = list(np.arange(len(self.model_names)))
        ax.set_yticks(yticks)
        ax.set_yticklabels(self.model_names[::-1]) 

        ax.set_xticks([0, .2, .4, .6, .8, 1.0])

        # build legend
        arts = []
        names = []
        for artist_name in self.artist_names:
            if artist_name in self.artists:
                artist = self.artists[artist_name]
                arts.append(artist)
                names.append(artist_name)

        ax.legend(arts, names)

        # draw GROUP horizontal lines and labels
        trans = ax.get_yaxis_transform()

        for y, label in zip(self.group_separators, self.group_names):
            # horizontal separator line
            ax.axhline(y=y, xmin=-.15, color='black', alpha=.3, lw=1, linestyle='-', clip_on=False)        

            # group label
            ax.annotate(label, xy=(-.15, y-.5), xycoords=trans, alpha=.4, color="black")

        # draw horizontal grid lines lines separating each model (light)
        for y in range(series):
            ax.axhline(y=y+.5, color='black', alpha=.05, lw=1, linestyle='-')  

        # print report of all_stats
        builder = ReportBuilder(self.config, self.store)
        text, rows = builder.build_formatted_table(self.all_stats)
        print(text)

        self.add_tooltips(self.fig, ax, self.artist_infos, self.run_dict, pubs, hyperparameter_info)
            
        plt.tight_layout()

        if show_plot:
            plt.show()


if __name__ == "__main__":
    from xtlib.helpers.xt_config import get_merged_config
    from xtlib.storage.store import Store

    config = get_merged_config()
    store = Store(config=config)

    w = RingPlots(config, store)
    w.build()
    plt.show()
