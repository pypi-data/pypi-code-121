# import mfire.utils.xr_to_geo as xrgeo
import branca.colormap as cm
import xarray as xr
import ipyleaflet as ipyl
import ipywidgets as widg
import json
import os

# import mfire.promethee.src.lib.config_parser as cf
# import mfire.configuration.config_processor as cf
import mfire.text.comment_generator.text_generator as text_generator
from mfire.composite.components import RiskComponentComposite
from mfire.utils.xr_utils import compute_stepsize
import pandas as pd

# ----------------------
import plotly.graph_objs as go
import json2html
import shapely

# -------------------
from copy import deepcopy

import logging

log = logging.Logger(__name__)


hex_c = ["#15f00f", "#fcf304", "#fcb104", "#f73005"]
cmap = cm.StepColormap(hex_c, index=[0, 0.9, 1.9, 2.9], vmax=3)


def hover_info(dcrop):
    descriptive_variable = ["units", "weatherVarName"]
    text_list = []
    for step in dcrop.step:
        text = ""
        for var in dcrop.variables:
            if var not in list(dcrop.coords._names) + descriptive_variable:
                if "evt" in dcrop[var].dims:
                    for i, evt in enumerate(dcrop[var].evt):
                        units = ""
                        if "units" in dcrop and var != "density":
                            units = dcrop.sel(evt=evt)["units"].values
                        if "weatherVarName" in dcrop:
                            evt_name = dcrop.sel(evt=evt)["weatherVarName"].values
                        else:
                            evt_name = "Evt %s" % str(i + 1)
                        if i == 0:
                            text = text + "%s values <br>" % (var)
                        text = text + "    %s : %s %s <br>" % (
                            evt_name,
                            dcrop[var].sel(step=step).sel(evt=evt).values.round(3),
                            units,
                        )
                else:
                    text = text + " %s : %s <br>" % (
                        var,
                        dcrop[var].sel(step=step).values.round(3),
                    )
        text_list.append(text)
    return text_list


def get_weather_variable(param, model="PAROME__", grid="__EURW1S100"):
    paramb = deepcopy(param)
    for level in paramb["levels"]:
        for event in level["elementsEvent"]:
            if isinstance(event["field"], str):
                event["field"] = event["field"].rpartition(model)[2].rpartition(grid)[0]
            elif isinstance(event["field"], dict):
                event["field"] = event["field"]["file"].split("/")[-1].split(".")[1]
    return paramb


def from_array_to_value(da):
    if "valid_time" not in da:
        da["valid_time"] = (
            ("step"),
            pd.to_datetime(da.time.values + da.step.values).to_pydatetime(),
        )
    jours_vert = da == 0
    vert = jours_vert.where(jours_vert, drop=True)
    jours_yellow = da == 1
    yellow = jours_yellow.where(jours_yellow, drop=True)
    jours_orange = da == 2
    orange = jours_orange.where(jours_orange, drop=True)
    jours_rouge = da == 3
    rouge = jours_rouge.where(jours_rouge, drop=True)
    return vert, yellow, orange, rouge


def instantiate_figure(da, titre="Mon titre"):
    stepsize = compute_stepsize(da, var=da.dims[0])
    log.warning(stepsize.values)
    vert, yellow, orange, rouge = from_array_to_value(da)

    valeurs_vert = go.Bar(
        x=pd.to_datetime(vert.valid_time.values).to_pydatetime(),
        y=vert.values,
        opacity=1,
        marker={"color": "#3DB847", "line": dict(color="black", width=1.1)},
        width=(vert * stepsize).values * 3600 * 1000,
        name="Pas de risque",
    )

    valeurs_jaune = go.Bar(
        x=pd.to_datetime(yellow.valid_time.values).to_pydatetime(),
        y=yellow.values,
        opacity=1,
        name="Risque 1",
        marker={"color": "yellow", "line": dict(color="black", width=1.1)},
        width=(yellow * stepsize).values * 3600 * 1000,
    )

    valeurs_orange = go.Bar(
        x=pd.to_datetime(orange.valid_time.values).to_pydatetime(),
        y=orange.values,
        opacity=1,
        name="Risque 2",
        marker={"color": "orange", "line": dict(color="black", width=1.1)},
        width=(orange * stepsize).values * 3600 * 1000,
    )

    valeurs_rouge = go.Bar(
        x=pd.to_datetime(rouge.valid_time.values).to_pydatetime(),
        y=rouge.values,
        opacity=1,
        name="Risque 3",
        marker={"color": "red", "line": dict(color="black", width=1.1)},
        width=(rouge * stepsize).values * 3600 * 1000,
    )
    fig = go.FigureWidget(
        data=[valeurs_vert, valeurs_jaune, valeurs_orange, valeurs_rouge],
        layout={
            "height": 250,
            "title": titre,
            "plot_bgcolor": "rgba(0,0,0,0)",
            "yaxis": dict(visible=False),
        },
    )
    return fig


def generate_text_for_level(level, ds, crop):
    d_level = ds.sel(risk_level=level).dropna("evt", how="all")
    unpleasant_var = ["units", "areaName", "areaType", "weatherVarName"]
    var_present = ds.data_vars
    var_to_drop = list(set(var_present).intersection(set(unpleasant_var)))
    unit_present = False
    weathervar_present = False
    if "units" in d_level:
        unit_present = True
        dunit = d_level["units"]
    if "weatherVarName" in d_level:
        weathervar_present = True
        dvar = d_level["weatherVarName"]

    d_level = d_level.drop(var_to_drop).dropna("evt", how="all")
    evts = d_level.evt.values

    if crop.step.size > 0:
        dcrop = d_level * crop
        # On remet les unités et les noms de variables
        if unit_present:
            dcrop["units"] = dunit.sel(evt=evts)
        if weathervar_present:
            dcrop["weatherVarName"] = dvar.sel(evt=evts)
        text_list = hover_info(dcrop.dropna("step", how="all"))
        return text_list
    return None


def update_fig(da, fig1, title, ds=None):
    if "occurrence" in ds:
        ds = ds.drop("occurrence")
    if "occurrence_event" in ds:
        ds = ds.drop("occurrence_event")
    stepsize = compute_stepsize(da, var=da.dims[0])
    vert, yellow, orange, rouge = from_array_to_value(da)
    ns = 3600 * 1000
    fig1.data[0].x = pd.to_datetime(vert.valid_time.values).to_pydatetime()
    fig1.data[0].y = vert.values
    fig1.data[0].width = (vert * stepsize).values * ns

    fig1.data[1].x = pd.to_datetime(yellow.valid_time.values).to_pydatetime()
    fig1.data[1].y = yellow.values
    fig1.data[1].width = (yellow * stepsize).values * ns
    if ds is not None:
        if 1 in ds.risk_level:
            text_list = generate_text_for_level(1, ds, yellow)
            if text_list is not None:
                fig1.data[1].hovertext = text_list

    fig1.data[2].x = pd.to_datetime(orange.valid_time.values).to_pydatetime()
    fig1.data[2].y = orange.values
    fig1.data[2].width = (orange * stepsize).values * ns
    if ds is not None:
        if 2 in ds.risk_level:
            text_list = generate_text_for_level(2, ds, orange)
            if text_list is not None:
                fig1.data[2].hovertext = text_list

    fig1.data[3].x = pd.to_datetime(rouge.valid_time.values).to_pydatetime()
    fig1.data[3].y = rouge.values
    fig1.data[3].width = (rouge * stepsize).values * ns
    if ds is not None:
        if 3 in ds.risk_level:
            text_list = generate_text_for_level(3, ds, rouge)
            if text_list is not None:
                fig1.data[3].hovertext = text_list

    fig1.layout.title = title


class my_rapid_map(widg.VBox):
    def __init__(self, param, mask_path, res_path="./", **kwargs):
        self.param = param
        self.mask_path = mask_path
        self.res_path = res_path
        self.mask_init()
        self.risk_init()
        self.map = ipyl.Map(zoom=7, center=(48, 0), layout={"height": "600px"})
        self.choro_init()
        self.map.center = self.get_center()
        # Popup init
        self.html_popup = widg.HTML(
            """Dragg your mouse over the data to see what is inside"""
        )
        self.html_popup.layout.margin = "0px 20px 20px 20px"
        self.map.add_control(
            ipyl.WidgetControl(widget=self.html_popup, position="bottomright")
        )

        # Step init
        self.step = 0
        nb_step = len(self.ds_res.step) - 1
        self.wid_step = widg.IntSlider(
            description="Step", value=self.step, max=nb_step, min=0
        )
        self.wid_step.observe(self.step_change, "value")

        self.map.add_control(ipyl.WidgetControl(widget=self.wid_step))
        self.map.add_control(ipyl.FullScreenControl())
        self.title_init()
        self.fig = instantiate_figure(
            self.da_occu.isel(id=0),
            titre=self.get_region_name(id_in=self.da_occu.isel(id=0).id.values),
        )
        # Add controls
        risk_description = self.define_risk_widget()
        accordion_risk = widg.Accordion(children=[risk_description])
        accordion_risk.set_title(0, "Description du risque")
        accordion_risk.selected_index = None
        if "object" in kwargs:
            super().__init__(
                [self.title, kwargs["object"], self.map, self.fig, accordion_risk]
            )
        else:
            super().__init__([self.title, self.map, self.fig, accordion_risk])

    def mask_init(self):
        geo_file = self.mask_path
        with open(geo_file) as geo1:
            self.poly = json.load(geo1)

    def risk_init(self):
        self.ds_res = xr.open_dataset(self.res_path + "ds.nc").dropna("step", how="all")
        self.da_occu = xr.open_dataarray(self.res_path + "occurence.nc").dropna(
            "step", how="all"
        )
        self.da_occu.name = "riskLevel"

    def get_center(self):
        s = shapely.geometry.shape(self.poly_crop["features"][0]["geometry"])
        return s.centroid.y, s.centroid.x

    def get_region_name(self, id_in):
        name_out = "unknown"
        for elt in self.poly["features"]:
            if elt["id"] == id_in:
                name_out = elt["properties"]["name"]
        return name_out

    def change_all(self, param, mask_path, res_path):
        self.param = param
        self.mask_path = mask_path
        self.res_path = res_path
        self.mask_init()
        self.risk_init()
        self.poly_restriction()
        self.map.center = self.get_center()
        self.map.remove_layer(self.choro)
        self.choro_init()
        self.title.value = " <h3> Risque de {}</h3>".format(self.param["name"])
        update_fig(
            self.da_occu.isel(id=0),
            self.fig,
            self.get_region_name(id_in=self.da_occu.isel(id=0).id.values),
            self.ds_res.isel(id=0),
        )
        self.update_risk_widget()
        nb_step = len(self.ds_res.step) - 1
        self.wid_step.value = 0
        self.wid_step.max = nb_step
        self.wid_step.min = 0

    def title_init(self):
        self.title = widg.HTML(" <h3> Risque de {}</h3>".format(self.param["name"]))
        # self.title = widg.HTML('''
        # <h3> Risk vent sur zones sympos </h3>  ''')

    def poly_restriction(self):
        self.poly_crop = deepcopy(self.poly)
        for elt in self.poly["features"]:
            if elt["id"] not in self.da_occu.id.values:
                self.poly_crop["features"].remove(elt)

    def choro_init(self):
        self.poly_restriction()
        self.choro = ipyl.Choropleth(
            geo_data=self.poly_crop,
            choro_data=self.da_occu.isel(step=0).to_dataframe()["riskLevel"].to_dict(),
            value_min=0,
            value_max=3,
            colormap=cmap,
            style={"fillOpacity": 0.8},
            name="Risk",
        )
        self.choro.value_min = 0
        self.choro.value_max = 3
        self.choro.on_hover(self.update_popup)
        self.choro.on_click(self.update_frise)
        self.map.add_layer(self.choro)

    def define_risk_widget(self):
        attributes = 'id="info-table" class="table table-bordered table-hover"'
        area = json2html.json2html.convert(
            json=self.param["geos"], table_attributes=attributes
        )
        period = json2html.json2html.convert(
            json=self.param["period"], table_attributes=attributes
        )
        param_short = get_weather_variable(self.param)
        levels = json2html.json2html.convert(
            json=param_short["levels"], table_attributes=attributes
        )
        self.area_widg = widg.HTML(value=area)
        self.period_widg = widg.HTML(value=period)
        self.risk_widg = widg.HTML(value=levels)
        return widg.VBox(
            [widg.HBox([self.area_widg, self.period_widg]), self.risk_widg]
        )

    def update_risk_widget(self):
        attributes = 'id="info-table" class="table table-bordered table-hover"'
        area = json2html.json2html.convert(
            json=self.param["geos"], table_attributes=attributes
        )
        period = json2html.json2html.convert(
            json=self.param["period"], table_attributes=attributes
        )
        param_short = get_weather_variable(self.param)
        levels = json2html.json2html.convert(
            json=param_short["levels"], table_attributes=attributes
        )
        self.area_widg.value = area
        self.period_widg.value = period
        self.risk_widg.value = levels

    def step_change(self, change):
        self.step = change["new"]
        self.choro.choro_data = (
            self.da_occu.isel(step=self.step).to_dataframe()["riskLevel"].to_dict()
        )
        self.choro.value_min = 0
        self.choro.value_max = 3

    def update_frise(self, **kwargs):
        if kwargs.get("event") == "click":
            feature = kwargs.get("feature")
            title = feature["properties"]["name"]
            my_id = feature["id"]
            update_fig(
                self.da_occu.sel(id=my_id), self.fig, title, self.ds_res.sel(id=my_id)
            )

    def update_popup(self, feature, **kwargs):
        my_id = feature["id"]
        # On rajoute cela pour pouvoir virer les echeances qui contiennent des nans.
        param_handler = RiskComponentComposite(**self.param)
        param_handler.load_risk(self.ds_res)
        comment = text_generator.GenerationText(param_handler)
        self.html_popup.value = """
                <h3> <b> Commentaire détaillé :</b> {} </h3>

                """.format(
            comment.identification_cas(my_id)
        )


class my_slow_map(my_rapid_map):
    def __init__(self, config, mask_path):
        """__init__
        Permet de faire une carte de risque à partir d'une configuration

        [extended_summary]

        Args:
            config ([type]): [description]
            mask_path ([type]): [description]
        """
        # On passe maintenant la config parser.
        self.config = config["components"]
        self.risk = 1

        param = self.config[self.risk]
        super().__init__(param, mask_path)  # ,object=save_button)

    def change_config(self, config, mask_path):
        self.config = config["components"]
        drisk = {}
        for i, x in enumerate(self.config):
            if x["type"] in ["risk", "Risk"]:
                drisk[x["name"]] = i
        self.risk = 0
        self.title_widg.value = self.risk
        self.title_widg.options = drisk
        self.mask_path = mask_path
        self.mask_init()
        self.change_risk({"new": self.risk})

    def title_init(self):
        drisk = {}
        for i, x in enumerate(self.config):
            if x["type"] in ["risk", "Risk"]:
                drisk[x["name"]] = i
        self.param = self.config[self.risk]
        self.title_text = widg.HTML(
            " <h3> Risque de {}</h3>".format(self.param["name"])
        )
        self.title_widg = widg.Dropdown(options=drisk, value=self.risk)
        self.title_widg.observe(self.change_risk, "value")
        self.title = widg.HBox([self.title_text, self.title_widg])

    def change_risk(self, change):
        self.risk = change["new"]
        self.param = self.config[self.risk]
        self.title_text.value = " <h3> Risque de {}</h3>".format(self.param["name"])
        self.update_risk_widget()
        self.update_risk()

    def update_risk(self):
        loading = widg.HTML("Computing risk. Be patient it can take a few seconds.")
        widget_control = ipyl.WidgetControl(
            widget=loading, position="bottomleft", min_height=100
        )
        self.map.add_control(widget_control)
        self.risk_init()
        self.wid_step.min = 0
        self.wid_step.max = len(self.da_occu.step)
        self.step = self.wid_step.min
        self.poly_restriction()
        self.map.remove_layer(self.choro)
        self.choro_init()
        self.map.remove_control(widget_control)
        title = "Init avec la premiere region"
        update_fig(self.da_occu.isel(id=0), self.fig, title, self.ds_res.isel(id=0))

    def compute_risk(self):
        # On va calculer le risque correspondant au parametre
        param_gen = RiskComponentComposite(**self.param)
        _ = param_gen.compute()
        # On recupere le risque et le dataset complet
        self.da_occu = param_gen.final_risk_da.dropna("step", how="all")
        self.da_occu.name = "riskLevel"
        self.ds_res = param_gen.risks_ds.sel(step=self.da_occu.step)

    def save_output(self, dout):
        """save_output
        Fonction permettant de sauvegarder les sorties.
        A lier quelque part avec un bouton.

        info -- Argument inutilisé passer par défaut par le callback

        """
        dir_risk = os.path.join(dout, self.param["name"])
        os.makedirs(dir_risk, exist_ok=True)
        self.da_occu.to_netcdf(os.path.join(dir_risk, "occurence.nc"))
        self.ds_res.to_netcdf(os.path.join(dir_risk, "ds.nc"))

    def mask_init(self):
        try:
            with open(self.mask_path) as geo1:
                self.poly = json.load(geo1)
        except TypeError:
            # Cas ou c'est dans un objet io.BytesIO
            self.poly = json.load(self.mask_path)

    def risk_init(self):
        self.compute_risk()
