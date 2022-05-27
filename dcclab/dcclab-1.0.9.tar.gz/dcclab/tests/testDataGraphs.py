# import env
# import pandas as pd
# import numpy as np
# import unittest
# from pathlib import Path
# import matplotlib.pyplot as plt
# import seaborn as sns
#
#
# class DataGraphs(env.DCCLabTestCase):
#
#     def setUp(self) -> None:
#         self.mCherry = pd.read_csv(Path(self.dataDir / "query_mcher_results.csv"), sep=";").dropna(axis="columns")
#         self.dapi = pd.read_csv(Path(self.dataDir / "query_DAPI_results.csv"), sep=";").dropna(axis="columns")
#         self.egfp = pd.read_csv(Path(self.dataDir / "query_egfp_results.csv"), sep=";").dropna(axis="columns")
#         self.mCherry = self.mCherry[
#             (self.mCherry["average"] != "NotYetImplemented") & (self.mCherry["average"] != "IndexError")]
#         self.dapi = self.dapi[
#             (self.dapi["average"] != "NotYetImplemented") & (self.dapi["average"] != "IndexError")]
#         self.egfp = self.egfp[
#             (self.egfp["average"] != "NotYetImplemented") & (self.egfp["average"] != "IndexError")]
#
#     def testExtractDataSingleChannel(self):
#         writeFile = open(Path(self.tmpDir / "imagesToCheck.csv"), "w", encoding="utf-8")
#         writeFile.writelines("path,channel,xVal,yVal,graphTitle")
#         channels = [self.egfp, self.dapi, self.mCherry]
#         dataNormalized = ["averageN", "stdDevN", "entropyN", "medianN"]
#         for channel in channels:
#             if self.egfp.equals(channel):
#                 channelName = "EGFP"
#                 color = "green"
#             elif self.mCherry.equals(channel):
#                 channelName = "mCherry"
#                 color = "red"
#             else:
#                 channelName = "DAPI"
#                 color = "blue"
#             for i in range(len(dataNormalized)):
#                 for j in range(i, len(dataNormalized)):
#                     xLabel = dataNormalized[i]
#                     yLabel = dataNormalized[j]
#                     if j != i:
#                         x = np.array(channel[xLabel], float)
#                         y = np.array(channel[yLabel], float)
#
#                         fig, ax = plt.subplots()
#                         sc = plt.scatter(x, y, color=color, alpha=0.2)
#                         annot = ax.annotate("", xy=(0, 0), xytext=(-100, 20), textcoords="offset points",
#                                             bbox=dict(boxstyle="round", fc="w"),
#                                             arrowprops=dict(arrowstyle="->"))
#                         annot.set_visible(False)
#                         title = "{} and {} of {} from the POM platform (normalized images)".format(xLabel, yLabel,
#                                                                                                    channelName)
#
#                         def update_annot(ind):
#                             pos = sc.get_offsets()[ind["ind"][0]]
#                             annot.xy = pos
#                             path = [np.array(channel["path"])[n] for n in ind["ind"]]
#                             xVal = [np.array(channel[xLabel])[n] for n in ind["ind"]]
#                             yVal = [np.array(channel[yLabel])[n] for n in ind["ind"]]
#                             text = "{}".format(" ".join([channel["path"][n] for n in ind["ind"]]))
#                             annot.set_text(text)
#                             for i in range(len(path)):
#                                 writeFile.writelines("\n{},{},{},{},{}".format(path[i], channelName, xVal[i], yVal[i], title))
#
#                         def click(event):
#                             vis = annot.get_visible()
#                             if event.inaxes == ax:
#                                 cont, ind = sc.contains(event)
#                                 if cont:
#                                     update_annot(ind)
#                                     annot.set_visible(True)
#                                     fig.canvas.draw_idle()
#                                 else:
#                                     if vis:
#                                         annot.set_visible(False)
#                                         fig.canvas.draw_idle()
#
#                         fig.canvas.mpl_connect("button_press_event", click)
#                         plt.ylabel(yLabel)
#                         plt.xlabel(xLabel)
#                         plt.title(title)
#
#                         plt.show()
#
#         writeFile.close()
#
#
# if __name__ == '__main__':
#     unittest.main()
