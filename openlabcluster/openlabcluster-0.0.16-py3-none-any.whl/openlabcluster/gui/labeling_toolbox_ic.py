import numpy as np
import wx
import wx.lib.scrolledpanel as SP
from openlabcluster.utils.auxiliaryfunctions import read_config
from openlabcluster.utils.plotting import format_axes

class WidgetPanel(wx.Panel):
    def __init__(self, parent):
        self.panel = wx.Panel.__init__(self, parent, -1, style=wx.SUNKEN_BORDER)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        # self.box = wx.StaticBox(self.panel, -1, "StaticBox")
        # text = wx.StaticText(self.box, -1, "This window is a child of the staticbox")

from openlabcluster.gui.train_network import ImagePanel
class ImagePanel_label(ImagePanel):
    def __init__(self,parent, gui_size,  projection='2D', **kwargs):
        super(ImagePanel_label, self).__init__(parent, gui_size,  projection, **kwargs)
        # h = gui_size[0] / 2
        # w = gui_size[1] / 3
        # wx.Panel.__init__(self, parent, -1, style=wx.SUNKEN_BORDER, size=(h, w))

class custom_objects_to_plot:
    def __init__(self, x, y, name):
        self.x = x
        self.y = y
        self.name = name


class ScrollPanel(SP.ScrolledPanel):
    def __init__(self, parent):
        SP.ScrolledPanel.__init__(self, parent, -1, style=wx.SUNKEN_BORDER)
        self.SetupScrolling(scroll_x=True, scroll_y=True, scrollToTop=False)
        self.Layout()
        self.box = wx.StaticBox(parent, -1, "StaticBox")
        text = wx.StaticText(self.box, -1, "This window is a child of the staticbox")

    def on_focus(self, event):
        pass

    def addRadioButtons(self, bodyparts, fileIndex, markersize):
        """
        Adds radio buttons for each bodypart on the right panel
        """
        self.choiceBox = wx.BoxSizer(wx.VERTICAL)
        choices = [l for l in bodyparts]
        self.fieldradiobox = wx.RadioBox(
            self,
            label="Select a bodypart to label",
            style=wx.RA_SPECIFY_ROWS,
            choices=choices,
        )
        self.slider = wx.Slider(
            self,
            -1,
            markersize,
            1,
            markersize * 3,
            size=(250, -1),
            style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS,
        )
        self.slider.Enable(False)
        self.checkBox = wx.CheckBox(self, id=wx.ID_ANY, label="Adjust marker size.")
        self.choiceBox.Add(self.slider, 0, wx.ALL, 5)
        self.choiceBox.Add(self.checkBox, 0, wx.ALL, 5)
        self.choiceBox.Add(self.fieldradiobox, 0, wx.EXPAND | wx.ALL, 10)
        self.SetSizerAndFit(self.choiceBox)
        self.Layout()
        return (self.choiceBox, self.fieldradiobox, self.slider, self.checkBox)

    def clearBoxer(self):
        self.choiceBox.Clear(True)

    def printTest(self, test):
        text = wx.StaticText(self.box, -1, "This window is a child of the staticbox")

    def openDialog(self, event):
        data = wx.PrintDialogData()
        data.EnableSelection(True)
        data.EnablePrintToFile(True)
        data.EnablePageNumbers(True)
        data.SetMinPage(1)
        data.SetMaxPage(10)

        dialog = wx.PrintDialog(self, data)
        # dialog.ShowModal()

        if dialog.ShowModal() == wx.ID_OK:
            data = dialog.GetPrintDialogData()
            print('GetAllPages: %d\n' % data.GetAllPages())

            dialog.Destroy()


from openlabcluster.gui.plot_hidden import extract_hid
class PlotGUI_panel(wx.Panel):
    """Class to display basic GUI elements."""

    def __init__(self, parent, cfg, sample_method, percentage, reducer_name='PCA', dimension='2d', model_name=None, model_type=None):
        self.cfg = cfg
        from openlabcluster.utils.auxiliaryfunctions import read_config
        self.cfg_data = read_config(self.cfg)

        self.reducer_name = reducer_name
        self.dimension = dimension
        if model_name:
            self.model_name = model_name
        else:
            self.model_name = self.cfg_data['tr_modelName']
            if not self.model_name:
                wx.MessageBox('No Model Exist Yet!', 'Error')
                return

        wx.Panel.__init__(self, parent, -1, style=wx.BORDER_NONE)
        displays = (
            wx.Display(i) for i in range(wx.Display.GetCount())
        )  # Gets the number of displays
        screenSizes = [
            display.GetGeometry().GetSize() for display in displays
        ]  # Gets the size of each display
        index = 0  # For display 1.
        screenWidth = screenSizes[index][0]
        screenHeight = screenSizes[index][1]
        self.gui_size = (screenWidth * 0.3, screenHeight * 0.5)
        self.selection_id =  {"Uniform (Uni)": 'random', "Cluster Center (Top)" : 'ktop',
                              "Cluster Random (Rand)":'krandom', "Marginal Index (MI)": 'kmi',
                              "Core Set (CS)": 'core_set'}

        self.SetSizeHints(
            wx.Size(self.gui_size)
        )
        # This sets the minimum size of the GUI. It can scale now!
        ###################################################################################################################################################

        # Spliting the frame into top and bottom panels. Bottom panels contains the widgets. The top panel is for showing images and plotting!
        #topSplitter = wx.SplitterWindow(self)
        # vSplitter = wx.SplitterWindow(topSplitter)

        if model_type:
            self.model_type = model_type
        else:
            self.model_type = self.cfg_data['tr_modelType']

        if sample_method:
            self.sample_method = self.selection_id[sample_method]
        else:
            self.sample_method = self.selection_id.get(self.cfg_data['sample_method'], 'ktop')

        self.image_panel = ImagePanel(self, self.gui_size)
        self.image_panel.axes.set_title('Behavior Classification Map')

        format_axes(self.image_panel.axes)

        self.num_sample = percentage

        self.ok = wx.Button(self.image_panel, label="Update Selection")
        self.ok.Bind(wx.EVT_BUTTON, self.savelabel)

        # widgetsizer.Add(self.re, 1, wx.ALL, 15)
        self.image_panel.widgetsizer.Add(self.ok,  wx.ALL, border=15)

        # self.image_panel.widget_panel.SetSizer(self.image_panel.widgetsizer)
        self.image_panel.renew_sizer()
        #self.SetSizer(self.image_panel.sizer)
        self.sizer = wx.GridBagSizer(1, 1)
        self.sizer.Add(self.image_panel,pos=(0,0), span=(1,1))
        self.SetSizer(self.sizer)
        self.sizer.Fit(self)

        self.selected_id = []
        self.text = ['Selected Points\n']
        if self.model_name:
            self.extract_hiddenstate()
            self.plot_initial()

            if self.model_type != 'seq2seq':
                self.plot_iter()

            self.plot_suggest()
            self.highlight, = self.image_panel.axes.plot([], [], 'o', color='r')
            # self.image_panel.axes.plot(0, 0, 'r', picker=3)
            self.image_panel.canvas.mpl_connect('pick_event', self.display_data)

        self.image_panel.axes.autoscale()

    def refresh(self, event, selection_method):
        self.selected_id = []
        from openlabcluster.utils.auxiliaryfunctions import read_config
        self.image_panel.axes.clear()
        self.cfg_data = read_config(self.cfg)

        self.model_name = self.cfg_data['tr_modelName']
        if not self.model_name:
            wx.MessageBox('No Model Exist Yet!', 'Error')
            return

        self.model_type = self.cfg_data['tr_modelType']
        
        print('slection methods', self.selection_id[selection_method])
        
        self.sample_method = self.selection_id[selection_method]
        
        self.extract_hiddenstate()
        self.plot_initial()

        if self.model_type != 'seq2seq':
            self.plot_iter()
        
        self.plot_suggest()

    def savelabel(self, event):
        import os
        import re
        label_path = os.path.join(self.cfg_data['project_path'], self.cfg_data['sample_path'])
        if not os.path.exists(label_path):
            os.mkdir(label_path)
        file_list = [x for x in os.listdir(label_path) if not x.startswith('.')]
        print(file_list)
        if len(file_list) > 0:
            last = np.sort(file_list)[-1]
            iter = re.split('([0-9]+)', last)
            iter = int(iter[1])+1
        else:
            iter = 0
        np.save(os.path.join(label_path, 'label%d.npy' % (iter)), self.selected_id)
        from openlabcluster.utils.auxiliaryfunctions import edit_config
        edit_config(self.cfg, {"selected_path":os.path.join(label_path, 'label%d.npy' % (iter))})
        # wx.MessageBox('Save Selected Samples')
        self.load_video()

    def initialize_video_coonection(self, load_video):
        self.load_video = load_video

    def display_data(self, event):
        cur_pos = np.array([event.mouseevent.xdata, event.mouseevent.ydata])
        inarray = np.asarray(event.ind)
        print(inarray)
        if len(inarray) > 0:
            x_tmp = self.extracted.transformed[inarray, 0]
            y_tmp = self.extracted.transformed[inarray, 1]
            if self.dimension=='3d':
                #x, y, z = event.artist._offsets3d
                z_tmp = self.extracted.transformed[inarray, 2]
                dist = (x_tmp - cur_pos[0]) ** 2 + (y_tmp -cur_pos[1]) ** 2
            else:
                dist = (x_tmp - cur_pos[0]) ** 2 + (y_tmp - cur_pos[1]) ** 2
            ind = inarray[np.argmin(dist)]
        else:
            ind = inarray

        if isinstance(ind, list):
            ind = ind[0]

        if ind not in self.selected_id:
            self.selected_id = self.selected_id + [ind]
            print('id', self.selected_id)
            #self.highlight.set_data(xdata[tmp], ydata[tmp])
            if self.dimension == '2d':
                self.image_panel.axes.plot(self.extracted.transformed[ind,0],self.extracted.transformed[ind, 1],'o', color='blue')

            else:
                self.image_panel.axes.plot3D(self.extracted.transformed[ind, 0], self.extracted.transformed[ind, 1],self.extracted.transformed[ind, 3], 'o',
                                           color='blue')
            self.text = self.text + ['P:%d\n' % ind]
            # self.label = wx.StaticText(self.choice_panel, -1, ''.join(self.text))
            # self.choice_panel.sizer.Add(self.label, 0, wx.ALIGN_CENTER_VERTICAL)
            self.image_panel.canvas.draw_idle()
        else:
            # self.choice_panel.sizer.Clear(True)
            self.selected_id.remove(ind)
            self.text.remove('P:%d\n' % ind)
            if self.dimension == '2d':
                self.image_panel.axes.plot(self.extracted.transformed[ind, 0], self.extracted.transformed[ind, 1], 'o',
                                           color='grey')

            else:
                self.image_panel.axes.plot3D(self.extracted.transformed[ind, 0], self.extracted.transformed[ind, 1],
                                             self.extracted.transformed[ind, 3], 'o',
                                             color='grey')
            self.image_panel.canvas.draw_idle()

    def extract_hiddenstate(self):
        # extract hidden state and suggest samples
        import os
        import re
        self.cfg_data = read_config(self.cfg)
        label_path = os.path.join(self.cfg_data['project_path'], self.cfg_data['sample_path'])
        self.model_type = self.cfg_data['tr_modelType']
        self.model_name = self.cfg_data['tr_modelName']
        if not os.path.exists(label_path):
            os.mkdir(label_path)
        file_list = [x for x in os.listdir(label_path) if not x.startswith('.')]
        print(file_list)
        if len(file_list) > 0:
            last = np.sort(file_list)[-1]
            iter = re.split('([0-9]+)', last)
            self.iter = int(iter[1]) + 1
        else:
            self.iter = 0

        self.extracted = extract_hid(self.cfg, dimension=self.dimension, reducer_name=self.reducer_name,
                                     model_name=self.model_name, model_type=self.model_type)

        from openlabcluster.training_utils.ssl.clustering_classification import iter_kmeans_cluster, remove_labeled_cluster
        from openlabcluster.training_utils.ssl.labelSampling import SampleFromCluster
        toLabel = np.where(self.extracted.semilabel!=0)[0].tolist()
        index_train_complete = np.arange(0, self.extracted.hidarray.shape[0])
        if  self.model_type == 'seq2seq':

            if self.sample_method == 'core_set':
                from openlabcluster.training_utils.ssl.kcenter_greedy import kCenterGreedy
                self.cor_set = kCenterGreedy(self.extracted.hidarray, None, seed=1)
                self.suggest = self.cor_set.select_batch_(None, toLabel,self.num_sample)
            else:
                hi_train, index_train = remove_labeled_cluster(self.extracted.hidarray,
                                                               index_train_complete, toLabel)
                train_id_list, dis_list, dis_list_prob, label_list = iter_kmeans_cluster(hi_train, index_train,
                                                                                         self.num_sample)
                self.suggest = SampleFromCluster(train_id_list, dis_list, dis_list_prob, 'ktop',
                                                 self.num_sample)
        else:
            if self.sample_method == 'core_set':
                self.cor_set.features = self.extracted.hidarray
                self.suggest = self.cor_set.select_batch_(None, toLabel, self.num_sample)
            else:
                hi_train,index_train, mi, = remove_labeled_cluster(self.extracted.hidarray,
                                                                   index_train_complete, toLabel, self.extracted.mi)
                try:
                    test = mi[0]
                except:
                    wx.MessageBox('All samples have been labled!', 'Error')
                train_id_list, dis_list, dis_list_prob, label_list = iter_kmeans_cluster(hi_train, index_train,
                                                                                         self.num_sample,mi)
                print('sample from cluster', self.sample_method)
                self.suggest = SampleFromCluster(train_id_list, dis_list, dis_list_prob, self.sample_method, self.num_sample)

    def plot_initial(self):

        self.image_panel.axes.scatter(self.extracted.transformed[:, 0], self.extracted.transformed[:,1], picker=True, color='grey')

    def plot_suggest(self):
        for ind in self.suggest:
            self.selected_id = self.selected_id + [ind]
            print('id', self.selected_id)
            self.image_panel.axes.scatter(self.extracted.transformed[ind, 0],self.extracted.transformed[ind, 1],  color='blue')

            self.text = self.text + ['P:%d\n' % ind]
            self.image_panel.canvas.draw_idle()

    def plot_iter(self):
        # plot samples already labeled as green
        i = self.extracted.semilabel != 0
        # fig = Figure()
        if sum(i) !=0:
            self.image_panel.axes.plot(self.extracted.transformed[i, 0], self.extracted.transformed[i, 1], 'o',
                                          color='green', alpha = 1)

    def current_sample(self, index):
        self.image_panel.axes.plot(self.extracted.transformed[index, 0], self.extracted.transformed[index, 1], 'o',
                                   color='r')
        self.image_panel.canvas.draw_idle()

    def update_labeled(self, index):
        self.image_panel.axes.plot(self.extracted.transformed[index, 0], self.extracted.transformed[index, 1], 'o',
                                   color='g')
        self.image_panel.canvas.draw_idle()

    def update_image_panel(self,  dim, method):
        self.dimension = dim
        self.reducer_name = method
        self.image_panel.refresh(dim)
        self.extracted = extract_hid(self.cfg, dimension=self.dimension, reducer_name=self.reducer_name,
                                     model_name=self.model_name, model_type=self.model_type)
        transform = self.extracted.transformed
        if dim =='2d':
            self.sc = self.image_panel.axes.scatter(transform[:,0], transform[:,1],s=10, picker=True, color='k')
        else:
            self.sc = self.image_panel.axes.scatter(transform[:,0], transform[:,1],transform[:,2], s=10, picker=True, color='k')
        font = {'family': 'serif',
                'color': 'darkred',
                'weight': 'normal',
                'size': 16,
                }
        self.image_panel.axes.set_title('Behavior Classification Map', fontdict=font)
        self.image_panel.axes.autoscale()






