import seaborn as sns
from matplotlib import pyplot as plt
import pandas as pd


class IReportManager:
    def report_overall(self, performance_logs):
        pass

    def report_by_index(self, train_targets: pd.DataFrame,
                              train_pred: pd.DataFrame,
                              test_targets: pd.DataFrame,
                              test_pred: pd.DataFrame):
        pass


class BasicReportManager(IReportManager):

    def report_overall(self, perf_train: pd.DataFrame, perf_test: pd.DataFrame):
        sns.despine()
        subp_n = int(len(perf_train.columns))
        fig, axes = plt.subplots(subp_n, 3, figsize=(18, subp_n * 4))
        fig.suptitle('Overall Performance Report For All windows')
        for i in range(subp_n):
            sns.histplot(perf_train[perf_train.columns[i]], ax=axes[i, 0])
            sns.histplot(perf_test[perf_test.columns[i]], ax=axes[i, 1])
            perf_train[[perf_train.columns[i]]].plot(ax=axes[i, 2], marker="+")
            perf_test[[perf_test.columns[i]]].plot(ax=axes[i, 2], marker="o")

        sns.despine()
        fig.tight_layout()
        return fig

    def report_by_index(self, train_targets: pd.DataFrame,
                        train_pred: pd.DataFrame,
                        test_targets: pd.DataFrame,
                        test_pred: pd.DataFrame):
        # train_row = performance_data.iloc[index_key][["train_targets", "train_predictions"]]
        # test_row = performance_data.iloc[index_key][["test_targets", "test_predictions"]]

        index_key = "window"
        res_train = pd.DataFrame(
            data={"pred": train_pred.values.flatten(), "actual": train_targets.values.flatten()},
            index=train_targets.index)

        res_test = pd.DataFrame(
            data={"pred": test_pred.values.flatten(), "actual": test_targets.values.flatten()},
            index=test_targets.index)

        fig, axes = plt.subplots(4, 2, figsize=(12, 12))
        fig.suptitle(f'Performance Report for window (index): {index_key}')

        axes[0, 0].set_title("test actual data dist")
        sns.histplot(res_test["actual"], ax=axes[0, 0])

        axes[1, 0].set_title("test predictions dist")
        sns.histplot(res_test["pred"], ax=axes[1, 0])

        axes[2, 0].set_title("test scatter")
        sns.scatterplot(data=res_test, x="actual", y="pred", ax=axes[2, 0], color="red")

        axes[0, 1].set_title("train actual data dist")
        sns.histplot(res_train["actual"], ax=axes[0, 1])

        axes[1, 1].set_title("train predictions dist")
        sns.histplot(res_train["pred"], ax=axes[1, 1])

        axes[2, 1].set_title("train scatter")
        sns.scatterplot(data=res_train, x="actual", y="pred", ax=axes[2, 1], color="red")

        gs = axes[3, 0].get_gridspec()
        axes[3, 0].remove()
        axes[3, 1].remove()
        row3_ax = fig.add_subplot(gs[3, 0:])
        res_train.plot(ax=row3_ax, cmap='tab20')
        res_test.plot(ax=row3_ax, cmap='Accent')

        sns.despine()
        fig.tight_layout()
        return fig
    