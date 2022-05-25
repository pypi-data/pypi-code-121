import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import gridspec
from sklearn.base import is_classifier


def get_1D_function(inputs, fidx, splits, values, right_inclusive=False):
    idx1 = np.digitize(inputs[:, fidx[0]], bins=splits[1:-1], right=right_inclusive)
    output = values[idx1]
    return output

def predict_1D_func(fidx, splits, values, right_inclusive=False):
    def wrapper(inputs):
        return get_1D_function(inputs, fidx, splits, values, right_inclusive=right_inclusive)
    return wrapper

def get_2D_function(inputs, fidx, splits_v1, splits_v2, values, right_inclusive=False):
    idx1 = np.digitize(inputs[:, fidx[0]], bins=splits_v1[1:-1], right=right_inclusive)
    idx2 = np.digitize(inputs[:, fidx[1]], bins=splits_v2[1:-1], right=right_inclusive)
    output = values[idx1, idx2]
    return output

def predict_2D_func(fidx, splits_v1, splits_v2, values, right_inclusive=False):
    def wrapper(inputs):
        return get_2D_function(inputs, fidx, splits_v1, splits_v2, values, right_inclusive=right_inclusive)
    return wrapper

class EBMExplainer():

    def __init__(self, estimator):

        self.estimator = estimator

    def fit(self, x):
        """
        Extract the fitted effects and calcualte the importance based on Shapley value.
        """
        self.main_effect_ = {}
        self.interaction_ = {}
        self.intercept_ = self.estimator.intercept_
        self.n_features_in_ = len(self.estimator.preprocessor_.col_names_)
        
        self.min_value_ = np.zeros((self.n_features_in_))
        self.max_value_ = np.zeros((self.n_features_in_))
        for i in range(self.n_features_in_):
            fidx = self.estimator.feature_groups_[i]
            if self.estimator.feature_types[fidx[0]] == "categorical":
                self.min_value_[i] = min(list(self.estimator.preprocessor_.col_mapping_[i].values()))
                self.max_value_[i] = max(list(self.estimator.preprocessor_.col_mapping_[i].values()))
            else:
                self.min_value_[i] = self.estimator.preprocessor_.col_min_[i]
                self.max_value_[i] = self.estimator.preprocessor_.col_max_[i]

        self.feature_names_ = self.estimator.feature_names[:self.n_features_in_]
        self.effect_importances_ = self.estimator.feature_importances_ / np.sum(self.estimator.feature_importances_)
        for i in range(len(self.estimator.feature_names)):
            key = self.estimator.feature_names[i]
            fidx = self.estimator.feature_groups_[i]
            key_type = self.estimator.feature_types[i]
            if key_type == "interaction":
                if self.estimator.feature_types[fidx[0]] == "categorical":
                    categories = np.array([float(k) for k in self.estimator.pair_preprocessor_.col_mapping_[fidx[0]].keys()])
                    splits_v1 = np.hstack([-np.inf, (categories[1:] + categories[:-1]) / 2, np.inf])
                else:
                    splits_v1 = np.hstack([-np.inf, self.estimator.pair_preprocessor_.col_bin_edges_[fidx[0]], np.inf])

                if self.estimator.feature_types[fidx[1]] == "categorical":
                    categories = np.array([float(k) for k in self.estimator.pair_preprocessor_.col_mapping_[fidx[1]].keys()])
                    splits_v2 = np.hstack([-np.inf, (categories[1:] + categories[:-1]) / 2, np.inf])
                else:
                    splits_v2 = np.hstack([-np.inf, self.estimator.pair_preprocessor_.col_bin_edges_[fidx[1]], np.inf])

                values = self.estimator.additive_terms_[i][1:][:,1:]
                importance = self.effect_importances_[i]
                predict_func = predict_2D_func(fidx, splits_v1, splits_v2, values, False)
                self.interaction_[key] = {"fidx": fidx,
                                 "type": "pairwise",
                                 "splits_v1": splits_v1,
                                 "splits_v2": splits_v2,
                                 "importance": importance,
                                 "predict_func": predict_func}
            elif key_type == "continuous":
                splits = np.hstack([-np.inf, self.estimator.preprocessor_.col_bin_edges_[fidx[0]], np.inf])
                values = self.estimator.additive_terms_[i][1:]
                importance = self.effect_importances_[i]
                density = {"names": self.estimator.preprocessor_._get_hist_edges(fidx[0]),
                        "scores": self.estimator.preprocessor_._get_hist_counts(fidx[0])}
                predict_func = predict_1D_func(fidx, splits, values, False)
                self.main_effect_[key] = {"fidx": fidx,
                                 "type": "continuous",
                                 "splits": splits,
                                 "values": values,
                                 "importance": importance,
                                 "density": density,
                                 "predict_func": predict_func}
            elif key_type == "categorical":
                categories = np.array([float(k) for k in self.estimator.preprocessor_.col_mapping_[fidx[0]].keys()])
                splits = np.hstack([-np.inf, (categories[1:] + categories[:-1]) / 2, np.inf])
                values = self.estimator.additive_terms_[i][1:]
                importance = self.effect_importances_[i]
                density = {"names": self.estimator.preprocessor_._get_hist_edges(fidx[0]),
                        "scores": self.estimator.preprocessor_._get_hist_counts(fidx[0])}
                predict_func = predict_1D_func(fidx, splits, values, False)
                self.main_effect_[key] = {"fidx": fidx,
                                 "type": "categorical",
                                 "splits": splits,
                                 "values": values,
                                 "importance": importance,
                                 "density": density,
                                 "predict_func": predict_func}

        mout = self.get_main_effect_raw_output(x)
        iout = self.get_interaction_raw_output(x)
        interaction_list = self.estimator.feature_groups_[self.n_features_in_:]
        if len(interaction_list) > 0:
            shapley_value = np.vstack([mout[:, fidx] +
                       0.5 * iout[:, np.where(np.vstack(interaction_list) == fidx)[0]].sum(1)
                       for fidx in range(self.n_features_in_)]).T
        else:
            shapley_value = mout
        feature_importance_raw = shapley_value.var(0)
        if np.sum(feature_importance_raw) == 0:
            self.feature_importance_ = np.zeros((self.n_features_in_))
        else:
            self.feature_importance_ = feature_importance_raw / feature_importance_raw.sum()

    def get_main_effect_raw_output(self, x):
        """
        Returns numpy array of main effects' raw prediction.

        Parameters
        ----------
        x : np.ndarray of shape (n_samples, n_features)
            Data features.

        Returns
        -------
        pred : np.ndarray of shape (n_samples, n_features)
            numpy array of main effects' raw prediction.
        """
        if len(self.main_effect_) > 0:
            pred = np.vstack([item["predict_func"](x) for key, item in self.main_effect_.items()]).T
        else:
            pred = np.empty(shape=(x.shape[0], 0))
        return pred

    def get_interaction_raw_output(self, x):
        """
        Returns numpy array of interactions' raw prediction.

        Parameters
        ----------
        x : np.ndarray of shape (n_samples, n_features)
            Data features.

        Returns
        -------
        pred : np.ndarray of shape (n_samples, n_interactions)
            numpy array of interactions' raw prediction.
        """
        if len(self.interaction_) > 0:
            pred = np.vstack([item["predict_func"](x) for key, item in self.interaction_.items()]).T
        else:
            pred = np.empty(shape=(x.shape[0], 0))
        return pred

    def local_explain(self, x, y=None):
        """
        Extract the main effects and interactions values of a given sample.

        Parameters
        ----------
        x : np.ndarray of shape (n_samples, n_features)
            Data features.
        y : np.ndarray of shape (n_samples, )
            Target response.
        """
        if is_classifier(self.estimator):
            predicted = self.estimator.predict_proba(x)[:, 1]
        else:
            predicted = self.estimator.predict(x)

        intercept = self.intercept_
        main_effect_output = self.get_main_effect_raw_output(x)
        interaction_output = self.get_interaction_raw_output(x)
        scores = np.hstack([np.repeat(intercept, x.shape[0]).reshape(-1, 1),
                      np.hstack([main_effect_output, interaction_output])])
        effect_names = np.array(["Intercept"] + list(self.main_effect_.keys())
                        + list(self.interaction_.keys()))
        active_indices = np.arange(1 + main_effect_output.shape[1] + interaction_output.shape[1])
        if y is not None:
            data_dict_local = [{"active_indices": active_indices,
                        "scores": scores[i],
                        "effect_names": effect_names,
                        "predicted": predicted[i],
                        "actual": y[i] if y is not None else None} for i in range(x.shape[0])]
        else:
            data_dict_local = [{"active_indices": active_indices,
                        "scores": scores[i],
                        "effect_names": effect_names,
                        "predicted": predicted[i]} for i in range(x.shape[0])]
        return data_dict_local

    def global_explain(self, main_grid_size=100, interact_grid_size=20):
        """
        Extract the fitted main effects and interactions.

        Parameters
        ----------
        main_grid_size : int
            The grid size of main effects, by default 100.
        interact_grid_size : int
            The grid size of interactions, by default 20.
        """
        if hasattr(self, "data_dict_global_"):
            return self.data_dict_global_

        data_dict_global = {}
        for key, item in self.main_effect_.items():
            fidx = item["fidx"]
            if item["type"] == "continuous":
                predict_func = item["predict_func"]
                inputs = np.linspace(self.min_value_[fidx[0]], self.max_value_[fidx[0]], 100)
                xgrid_input = np.zeros((inputs.shape[0], self.n_features_in_))
                xgrid_input[:, fidx[0]] = inputs
                outputs = predict_func(xgrid_input)
            else:
                inputs = np.array([float(k) for k in self.estimator.preprocessor_.col_mapping_[fidx[0]].keys()])
                outputs = item["values"]
            data_dict_global[key] = {"type": item["type"],
                             "fidx": item["fidx"],
                             "inputs": inputs,
                             "outputs": outputs,
                             "importance": item["importance"],
                             "density": item["density"]}
        for key, item in self.interaction_.items():
            fidx = item["fidx"]
            predict_func = item["predict_func"]
            x1grid = np.linspace(self.min_value_[fidx[0]], self.max_value_[fidx[0]], interact_grid_size)
            x2grid = np.linspace(self.min_value_[fidx[1]], self.max_value_[fidx[1]], interact_grid_size)
            x1, x2 = np.meshgrid(x1grid, x2grid[::-1])
            inputs = np.hstack([np.reshape(x1, [-1, 1]), np.reshape(x2, [-1, 1])])
            xgrid_input = np.zeros((x1.shape[0] * x1.shape[1], self.n_features_in_))
            xgrid_input[:, fidx] = inputs
            outputs = predict_func(xgrid_input).reshape(x1.shape)
            data_dict_global[key] = {"type": item["type"],
                             "fidx": item["fidx"],
                             "inputs": inputs,
                             "outputs": outputs,
                             "importance": item["importance"]}

        self.data_dict_global_ = data_dict_global
        return data_dict_global

    def show_local_explain(self, x, y=None, folder="./", name="demo", save_png=False, save_eps=False):
        """
        Show local explanation of given samples.

        Parameters
        ----------
        x : np.ndarray of shape (n_samples, n_features)
            Data features.
        y : np.ndarray of shape (n_samples, )
            Target response.
        folder : str
            The path of folder to save figure, by default "./".
        name : str
            Name of the file, by default "local_explain".
        save_png : boolean
            Whether to save the plot in PNG format, by default False.
        save_eps : boolean
            Whether to save the plot in EPS format, by default False.
        """
        def local_visualize(data_dict_local, folder="./", name="local_explain", save_png=False, save_eps=False):

            max_ids = data_dict_local["scores"].shape[0]
            idx = 1 + np.argsort(np.abs(data_dict_local["scores"][1:]))[::-1]
            idx = np.array([0] + idx.tolist())
            fig = plt.figure(figsize=(round((max_ids + 1) * 0.6), 4))
            plt.bar(np.arange(max_ids), data_dict_local["scores"][idx])
            plt.xticks(np.arange(max_ids), data_dict_local["effect_names"][idx], rotation=60)

            if "actual" in data_dict_local.keys():
                title = "Predicted: %0.4f | Actual: %0.4f" % (data_dict_local["predicted"].ravel()[0],
                data_dict_local["actual"].ravel()[0])
            else:
                title = "Predicted: %0.4f" % (data_dict_local["predicted"].ravel()[0])
            plt.title(title, fontsize=15)
            plt.tight_layout()

            if max_ids > 0:
                save_path = folder + name
                if save_eps:
                    if not os.path.exists(folder):
                        os.makedirs(folder)
                    fig.savefig("%s.eps" % save_path, bbox_inches="tight", dpi=100)
                if save_png:
                    if not os.path.exists(folder):
                        os.makedirs(folder)
                    fig.savefig("%s.png" % save_path, bbox_inches="tight", dpi=100)

        data_dict_local = self.local_explain(x, y)
        for item in data_dict_local:
            local_visualize(item, folder=folder, name=name, save_eps=save_eps, save_png=save_png)

    def show_global_explain(self, main_effect_num=None, interaction_num=None, 
                    cols_per_row=4, folder="./", name="demo", save_png=False, save_eps=False):
        """
        Show the fitted main effects and interactions.
        
        Parameters
        ----------
        main_effect_num : int or None
            The number of top main effects to show, by default None,
            As main_effect_num=None, all main effects would be shown.
        interaction_num : int or None
            The number of top interactions to show, by default None,
            As interaction_num=None, all main effects would be shown.
        cols_per_row : int
            The number of subfigures each row, by default 4.
        folder : str
            The path of folder to save figure, by default "./".
        name : str
            Name of the file, by default "global_explain".
        save_png : boolean
            Whether to save the plot in PNG format, by default False.
        save_eps : boolean
            Whether to save the plot in EPS format, by default False.
        """
        data_dict_global = self.global_explain()
        maineffect_count = 0
        componment_scales = []
        for key, item in data_dict_global.items():
            componment_scales.append(item["importance"])
            if item["type"] != "pairwise":
                maineffect_count += 1

        componment_scales = np.array(componment_scales)
        sorted_index = np.argsort(componment_scales)
        active_index = sorted_index[componment_scales[sorted_index].cumsum() > 0][::-1]
        active_univariate_index = active_index[active_index < maineffect_count][:main_effect_num]
        active_interaction_index = active_index[active_index >= maineffect_count][:interaction_num]
        max_ids = len(active_univariate_index) + len(active_interaction_index)

        if max_ids == 0:
            return

        idx = 0
        fig = plt.figure(figsize=(5.2 * cols_per_row, 4 * int(np.ceil(max_ids / cols_per_row))))
        outer = gridspec.GridSpec(int(np.ceil(max_ids / cols_per_row)), cols_per_row, wspace=0.25, hspace=0.35)
        for indice in active_univariate_index:
            feature_name = list(data_dict_global.keys())[indice]
            item = data_dict_global[feature_name]
            if self.estimator.feature_types[item["fidx"][0]] == "categorical":
                inner = gridspec.GridSpecFromSubplotSpec(2, 1, subplot_spec=outer[idx],
                            wspace=0.1, hspace=0.1, height_ratios=[6, 1])
                ax1 = plt.Subplot(fig, inner[0])
                categories = np.array([float(k) for k in self.estimator.preprocessor_.col_mapping_[item["fidx"][0]].keys()])
                ax1.bar(item["inputs"], item["outputs"])
                ax1.set_xticklabels([])
                fig.add_subplot(ax1)

                ax2 = plt.Subplot(fig, inner[1])
                ax2.bar(item["density"]["names"], item["density"]["scores"])
                ax2.get_shared_x_axes().join(ax1, ax2)
                ax2.autoscale()
                ax2.set_yticklabels([])
                fig.add_subplot(ax2)
            else:
                inner = gridspec.GridSpecFromSubplotSpec(2, 1, subplot_spec=outer[idx], wspace=0.1, hspace=0.1, height_ratios=[6, 1])
                ax1 = plt.Subplot(fig, inner[0])
                ax1.plot(item["inputs"], item["outputs"])
                ax1.set_xticklabels([])
                fig.add_subplot(ax1)

                ax2 = plt.Subplot(fig, inner[1])
                xint = ((np.array(item["density"]["names"][1:]) + np.array(item["density"]["names"][:-1])) / 2).reshape([-1, 1]).reshape([-1])
                ax2.bar(xint, item["density"]["scores"], width=xint[1] - xint[0])
                ax2.get_shared_x_axes().join(ax1, ax2)
                ax2.set_yticklabels([])
                ax2.autoscale()
                fig.add_subplot(ax2)
                
            ax1.set_title(feature_name + " (" + str(np.round(100 * item["importance"], 1)) + "%)", fontsize=15)
            idx += 1

        for indice in active_interaction_index:
            feature_name = list(data_dict_global.keys())[indice]
            item = data_dict_global[feature_name]
            ax = plt.Subplot(fig, outer[idx])
            interact_plot = ax.imshow(item["outputs"], interpolation="nearest",
                              aspect="auto", extent=[self.min_value_[item["fidx"][0]], self.max_value_[item["fidx"][0]],
                              self.min_value_[item["fidx"][1]], self.max_value_[item["fidx"][1]]])
            response_precision = max(int(- np.log10(np.max(item["outputs"]) - np.min(item["outputs"]))) + 2, 0)
            fig.colorbar(interact_plot, ax=ax, orientation="vertical", format="%0." + str(response_precision) + "f", use_gridspec=True)
            ax.set_title(feature_name + " (" + str(np.round(100 * item["importance"], 1)) + "%)", fontsize=15)
            fig.add_subplot(ax)
            idx += 1

        outer.tight_layout(fig)

    def show_feature_importance(self, folder="./", name="feature_importance", save_eps=False, save_png=False):
        """
        Visualize the feature importance.

        Parameters
        ----------
        folder : str
            The path of folder to save figure, by default "./".
        name : str
            Name of the file, by default "feature_importance".
        save_png : boolean
            Whether to save the plot in PNG format, by default False.
        save_eps : boolean
            Whether to save the plot in EPS format, by default False.
        """
        all_ir = []
        all_names = []
        feature_names = self.feature_names_
        feature_importance = self.feature_importance_
        for name, importance in zip(feature_names, feature_importance):
            if importance > 0:
                all_ir.append(importance)
                all_names.append(name)

        max_ids = len(all_names)
        if max_ids > 0:
            fig = plt.figure(figsize=(0.4 + 0.65 * max_ids, 4))
            ax = plt.axes()
            ax.bar(np.arange(len(all_ir)), [ir for ir, _ in sorted(zip(all_ir, all_names))][::-1])
            ax.set_xticks(np.arange(len(all_ir)))
            ax.set_xticklabels([name for _, name in sorted(zip(all_ir, all_names))][::-1], rotation=60)
            plt.ylim(0, np.max(all_ir) + 0.05)
            plt.xlim(-1, len(all_names))
            plt.title("Feature Importance")
            plt.tight_layout()

            save_path = folder + name
            if save_eps:
                if not os.path.exists(folder):
                    os.makedirs(folder)
                fig.savefig("%s.eps" % save_path, bbox_inches="tight", dpi=100)
            if save_png:
                if not os.path.exists(folder):
                    os.makedirs(folder)
                fig.savefig("%s.png" % save_path, bbox_inches="tight", dpi=100)

    def show_effect_importance(self, folder="./", name="effect_importance", save_eps=False, save_png=False):
        """
        Visualize the effect importance.

        Parameters
        ----------
        folder : str
            The path of folder to save figure, by default "./".
        name : str
            Name of the file, by default "effect_importance".
        save_png : boolean
            Whether to save the plot in PNG format, by default False.
        save_eps : boolean
            Whether to save the plot in EPS format, by default False.
        """
        data_dict_global = self.global_explain()
        all_ir = []
        all_names = []
        for key, item in data_dict_global.items():
            if item["importance"] > 0:
                all_ir.append(item["importance"])
                all_names.append(key)

        max_ids = len(all_names)
        if max_ids > 0:
            fig = plt.figure(figsize=(0.4 + 0.65 * max_ids, 4))
            ax = plt.axes()
            ax.bar(np.arange(len(all_ir)), [ir for ir, _ in sorted(zip(all_ir, all_names))][::-1])
            ax.set_xticks(np.arange(len(all_ir)))
            ax.set_xticklabels([name for _, name in sorted(zip(all_ir, all_names))][::-1], rotation=60)
            plt.ylim(0, np.max(all_ir) + 0.05)
            plt.xlim(-1, len(all_names))
            plt.title("Effect Importance")
            plt.tight_layout()

            save_path = folder + name
            if save_eps:
                if not os.path.exists(folder):
                    os.makedirs(folder)
                fig.savefig("%s.eps" % save_path, bbox_inches="tight", dpi=100)
            if save_png:
                if not os.path.exists(folder):
                    os.makedirs(folder)
                fig.savefig("%s.png" % save_path, bbox_inches="tight", dpi=100)
