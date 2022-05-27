#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File      : afm.py
# Author    : Chris Jones
# Email     : crj341@student.bham.ac.uk
# Date      : 26/06/2020
# Version   : 0.3.20

from operator import contains
import  numpy                   as      np
import  plotly.graph_objects    as      go
import  easygui                 as      gui
from    scipy                   import  interpolate as  interp
from    NSFopen                 import  read        as  ns
import  re
import  os
from    sklearn.linear_model    import  LinearRegression

import  pandas              as      pd
import  seaborn             as      sns
import  matplotlib.pyplot   as      plt
from    fnmatch             import  fnmatch

class AFM:

    '''
    The nanofoce.AFM() class is used for importing, storing and analysing AFM
    force curves produced by Nanoscope 6. Details of the parameters, functions
    and an example running script are given below.

    Prerequisits
    ------------
    pip install numpy
    pip install plotly
    pip install scipy
    pip install easygui

    Parameters
    ----------  
    approach_raw: [samples, curve_number]
        Raw AFM force curve approach data (nN) imported from nanoscope
        files without baseline or contact corrections applied, produced
        by input_files function
    retract_raw: [samples, curve_number]
        Raw AFM force curve retract data (nN) imported from nanoscope
        files without baseline or contact corrections applied, produced
        by input_files function
    z_position_raw: [samples, curve_number]
        Raw AFM force curve piezo position data (nm) imported from nanoscope
        files without baseline or contact corrections applied, produced
        by input_files function
    approach: [samples, curve_number]
        AFM force curve approach data (nN) produced by the baseline function
        and updated by teh contact function
    retract: [samples, curve_number]
        AFM force curve retract data (nN) produced by the baseline function
        and updated by teh contact function
    z_approach:[samples, curve_number]
        AFM force curve tip/piezo position data (nm) produced by the baseline
        function and updated by teh contact function
    z_withdraw:[samples, curve_number]
        AFM force curve tip/piezo position data (nm) produced by the baseline
        function and updated by teh contact function
    adhesion: [curve_number]
        Adhesion (nN) value calculated for each force curve by calc_adhesion
    modulus: [curve_number]
        Modulus (MPa) value calculated for each force curve by calc_modulus
    def_sens:
        Deflection sensetivity (nm/V), imported manually from first force
        curve file and manually overriden with set_def_sense function
    spr_const:
        Spring constant (N/m), imported manually from first force
        curve file and manually overriden with set_def_sense function
    file_name:
        First file name (usually with .000 extension)
    filelist: [curve_number]
        Full list of imported file names (.000 to .n extension)
    run_name:
        Name of experiment, specified by set_run_name function

    Functions
    ---------
    set_run_name:
        Manually set 'run_name' variable <.set_run_name(Sample name here)>
    set_def_sens:
        Manually set 'def_sens' variable <.set_def_sens(Value)>
    set_spr_const:
        Manually set 'spr_const' variable <.set_spr_const(Value)>
    run:
        Basic run script calling:
            .input_files()
            .nanoscope_params()
            .nanoscope_read()
            .baseline()
            .contact()
            .plot_curves()
            .calc_adhesion()
            .calc_modulus()
    input_files:
        Function to find input file names. If called with no inputs a GUI
        window will appear prompting the user to select the first Nanoscope
        file (usually with '.000' extension). Alternativley the file path can
        be given as an input to the function <.input_files(\path\to\file\.000)>.
        The function will then search for all subsequent files with the same
        name and consecutive file extensions (.000, .001, .002, ..., .nnn)
    nanoscope_params:
        Function to extract relevant parameters from first Nanoscope file
    nanoscope_read:
        Function to import raw force curve data
    plot_raw:
        Function to plot individual, unprocessed force curves. Curve number to
        plot must be given as an input <.plot_raw(n)>
    baseline:
        Function to adjust force curve baseline to zero by taking the mean value
        of a specified region of the approach curve. The default is from 0.45*z
        to 0.8*z, starting at the contact side of the curve. The start and end
        points may be specified using the 'start_pos' and 'end_pos' inputs to
        account for a longer/shorter baseline or regions of noise. Noisy curves
        may be removed by specifying a maximum standard deviation for the baseline
        region separatley for the approach and retract curves using the inputs
        'max_approach_noise' and 'max_retract_noise' respectivley. The defaults for
        each are 1 nN.
    contact:
        Function to align the contact point of the approach curve with zero by
        finding the first point to cross the axis and interpolating between this
        and the previous value. Note this method may be unstable for noisy curves.
    plot_adjusted:
        Function to plot individual, processed force curves. Curve number to
        plot must be given as an input <.plot_adjusted(n)>
    plot_curves:
        Function to plot all processed force curves
    delete_curve:
        Function to manually remove erroneous or highly noisy curves. Specify the
        curve(s) to remove in the input <.delete_curve(i,j,k)>
    save_data:
        Function to save current variables in '.npz' format. The file name and path
        for saving can be given as an input. If no input is given a GUI will prompt
        the user to select a location and file name. In both case no file extension
        is needed.
    load_data:
        Function to import previously saved variables in '.npz' format. As with saving,
        the file name and path can be given as an input or left blank to use a GUI.
    calc_adhesion:
        Funciton to calculate the adhesion value for each curve by finding the minimum
        point on the retact curve. A histogram of calculated values can be plotted by
        setting the 'plot_hist' input to 'True'
    overlay_adhesion_hist:
        Funciton to plot a histogram comparing adhesion values for multiple experiments.
        A separate instance of the AFM class containing the data for each should be
        given as the inputs
    overlay_adhesion_box:
        Funciton to produce a box plot comparing adhesion values for multiple experiments.
        A separate instance of the AFM class containing the data for each should be
        given as the inputs
    overlay_adhesion_violin:
        Funciton to produce a violin plot comparing adhesion values for multiple experiments.
        A separate instance of the AFM class containing the data for each should be
        given as the inputs
    overlay_adhesion_bar:
        Funciton to produce a bar chart comparing adhesion values for multiple experiments.
        A separate instance of the AFM class containing the data for each should be
        given as the inputs
    calc_modulus:
        Funciton to calculate the modulus value for each curve using the Hertz model.
        A histogram of calculated values can be plotted by setting the 'plot_hist'
        input to 'True'
    overlay_modulus_hist:
        Funciton to plot a histogram comparing modulus values for multiple experiments.
        A separate instance of the AFM class containing the data for each should be
        given as the inputs
    overlay_modulus_box:
        Funciton to produce a box plot comparing modulus values for multiple experiments.
        A separate instance of the AFM class containing the data for each should be
        given as the inputs
    overlay_modulus_violin:
        Funciton to produce a violin plot comparing modulus values for multiple experiments.
        A separate instance of the AFM class containing the data for each should be
        given as the inputs
    overlay_modulus_bar:
        Funciton to produce a bar chart comparing modulus values for multiple experiments.
        A separate instance of the AFM class containing the data for each should be
        given as the inputs
    plot_adhesion_modulus:
        Function to produce a scatter plot of adhesion vs. modulus values for a single
        experiment

    Example
    -------
    An example script and full tutorial for using the AFM class is available from:
    https://github.com/crj341/nanoforce

    '''

    def __init__(self):

        self.approach = []
        self.retract = []
        self.z_approach = []
        self.z_withdraw = []

        self.approach_raw = []
        self.retract_raw = []
        self.z_position_raw = []
        self.z_approach_raw = []
        self.z_withdraw_raw = []
        self.z_approach_piezo =[]
        self.z_withdraw_piezo =[]


        self.adhesion = []
        self.modulus = []
        self.contact_point = []
        self.indent_depth = []
        self.snap_in = []
        self.max_force = []

        self.data_offset = []
        self.data_length = []
        self.ramp_size = []
        self.samps_line = []
        self.zsens = []
        self.zscale = []
        self.def_sens = []
        self.spr_const = []

        self.file_name = []
        self.filelist = []
        self.run_name = []
        self.measurements = []


    def set_run_name(self,_run_name):
        '''
        Manually set 'run_name' variable <.set_run_name(Sample name here)>
        '''
        self.run_name = str(_run_name)

    def set_def_sens(self,_def_sens):
        '''
        Manually set 'def_sens' variable <.set_def_sens(Value)>
        '''
        self.def_sens = _def_sens

    def set_spr_const(self,_spr_const):
        '''
        Manually set 'spr_const' variable <.set_spr_const(Value)>
        '''
        self.spr_const = _spr_const

    def run(self):
        '''
        Basic run script calling:
            .input_files()
            .nanoscope_params()
            .nanoscope_read()
            .baseline()
            .contact()
            .plot_curves()
            .calc_adhesion()
            .calc_modulus()
        '''

        self.input_files()
        self.nanoscope_params()
        self.nanoscope_read()
        self.baseline()
        self.contact()
        self.plot_curves()
        self.calc_adhesion()
        self.calc_modulus()

    def input_files(
        self,
        gui_on = True
    ):
        '''
        Function to find input file names. If called with no inputs a GUI
        window will appear prompting the user to select the first Nanoscope
        file (usually with '.000' extension). Alternativley the file path can
        be given as an input to the function <.input_files(\path\to\file\.000)>.
        The function will then search for all subsequent files with the same
        name and consecutive file extensions (.000, .001, .002, ..., .nnn)
        '''

        if gui_on:
            file = gui.fileopenbox()
        else:
            file = self.file_name

        if file[-3:] == 'nid':
            print('input_files function not required for .nid files')

        else:
            file_no_ext = file[:-3]

            i = int(file[-3])
            j = int(file[-2])
            k = int(file[-1])

            ext = str(i) + str(j) + str(k)

            _filelist = list('')

            while os.path.isfile(file_no_ext + ext):
                
                _filelist.append(file_no_ext + ext)

                k += 1
                if k == 10:
                    k = 0
                    j += 1
                
                if j == 10:
                    j = 0
                    i += 1

                ext = str(i) + str(j) + str(k)

            self.filelist = _filelist

    def nanoscope_params(
        self,
        nanoscope_version = 6
        ):
        '''
        Function to extract relevant parameters from first Nanoscope file.
        By default the function will search for the parameters used in a
        Nanoscope 6 file. If using Nanoscope 5, change the 'nanoscope_version'
        input to 5.
        '''

        if nanoscope_version not in [5, 6]:
            Warning('The nanoscope_version input is not set to a compatible version (5 or 6)')
            exit()

        filename = self.filelist[0]
        data = open(filename, "r", errors='ignore')

        nanoscope_chk = data.readline().strip()
        if not nanoscope_chk.startswith('\*Force file list'):
            Warning('Input file not nanoscope')
            exit()

        if nanoscope_version == 6:

            while data:

                line = data.readline().strip()

                if line.startswith('\*File list end'):
                    break

                if len(line) < 1:
                    continue
                
                if re.search('\Data offset:', line):
                    _data_offset = [int(s) for s in line.split() if s.isdigit()]

                elif re.search('\Data length:', line):
                    _data_length = [int(s) for s in line.split() if s.isdigit()]

                elif re.search('\@4:Ramp size:', line):
                    _ramp_size = re.findall(r'\d+',line)[1] + '.' + re.findall(r'\d+',line)[2]

                elif re.search('\Samps/line', line):
                    _samps_line = [int(s) for s in line.split() if s.isdigit()]

                elif re.search('@Sens. Zsens:', line):
                    _zsens = re.findall(r'\d+',line)[0] + '.' + re.findall(r'\d+',line)[1]

                elif re.search('\@4:Z scale: V ', line):
                    _zscale = re.findall(r'\d+',line)[1] + '.' + re.findall(r'\d+',line)[2]

                elif re.search('\@Sens. DeflSens:', line):
                    _def_sens = re.findall(r'\d+',line)[0] + '.' + re.findall(r'\d+',line)[1]
                    
                elif re.search('\Spring Constant:', line):
                    try:
                        _spr_const = re.findall(r'\d+',line)[0] + '.' + re.findall(r'\d+',line)[1]
                    except:
                        _spr_const = re.findall(r'\d+',line)[0]

            data.close()

        elif nanoscope_version == 5:

            while data:

                line = data.readline().strip()

                if line.startswith('\*File list end'):
                    break

                if len(line) < 1:
                    continue
                
                if re.search('\Data offset:', line):
                    _data_offset = [int(s) for s in line.split() if s.isdigit()]

                elif re.search('\Data length:', line):
                    _data_length = [int(s) for s in line.split() if s.isdigit()]

                elif re.search('\@4:Ramp size:', line):
                    _ramp_size = re.findall(r'\d+',line)[1] + '.' + re.findall(r'\d+',line)[2]

                elif re.search('\Samps/line', line):
                    _samps_line = [int(s) for s in line.split() if s.isdigit()]

                elif re.search('\@Sens. Zscan:', line):
                    _zsens = re.findall(r'\d+',line)[0] + '.' + re.findall(r'\d+',line)[1]

                elif re.search('\@4:Z scale: V ', line):
                    _zscale = re.findall(r'\d+',line)[1] + '.' + re.findall(r'\d+',line)[2]

                elif re.search('\@Sens. Deflection:', line):
                    _def_sens = re.findall(r'\d+',line)[0] + '.' + re.findall(r'\d+',line)[1]
                    
                elif re.search('\Spring constant:', line):
                    try:
                        _spr_const = re.findall(r'\d+',line)[0] + '.' + re.findall(r'\d+',line)[1]
                    except:
                        _spr_const = re.findall(r'\d+',line)[0]
            data.close()

        self.data_offset = int(_data_offset[0])
        self.data_length = int(_data_length[0])
        self.ramp_size = float(_ramp_size)
        self.samps_line = int(_samps_line[0])
        self.zsens = float(_zsens)
        self.zscale = float(_zscale)
        self.def_sens = float(_def_sens)
        self.spr_const = float(_spr_const)

    def nanoscope_read(
        self
        ):
        '''
        Function to import raw force curve data
        '''

        i = 0

        self.approach_raw = np.zeros([self.samps_line, len(self.filelist)])
        self.retract_raw = np.zeros([self.samps_line, len(self.filelist)])
        self.z_position_raw = np.zeros([self.samps_line , len(self.filelist)])

        for filename in self.filelist:

            data = open(filename,"rb")

            data.seek(self.data_offset)
            _approach_curve = np.fromfile(file = data, dtype = 'int16', count = self.samps_line) * self.zscale * self.spr_const * self.def_sens
            _retract_curve = np.fromfile(file = data, dtype = 'int16', count = self.samps_line) * self.zscale * self.spr_const * self.def_sens

            hscale = (self.zsens * self.ramp_size * 2 ** 16 / self.samps_line ) / 2
            _z_position = hscale * np.arange(1, self.samps_line + 1)

            self.approach_raw[:,i] = np.array(_approach_curve)
            self.retract_raw[:,i] = np.array(_retract_curve)
            self.z_position_raw[:,i] = np.array(_z_position)

            i += 1

        self.measurements = self.approach_raw.shape[1]


    def nanosurf_import(
        self
    ):
        '''
        Function to plot import Nanosurf .nid data files.
        '''
        _nid = ns.read(self.file_name)
        _data = _nid.data
        _params = _nid.param

        _approach = _data.Spec.Forward['Deflection']
        _z_approach = _data.Spec.Forward['Z-Axis Sensor']

        _withdraw = _data.Spec.Backward['Deflection']
        _z_withdraw = _data.Spec.Backward['Z-Axis Sensor']

        _def_sens = _params.Tip.Sensitivity['Value']
        _spr_const = _params.Tip.Prop0['Value']

        self.def_sens = float(_def_sens)
        self.spr_const = float(_spr_const)
        self.samps_line = int(_params['Header Dump']['DataSet-Info']['Data points'])

        self.approach_raw = np.array(_approach, dtype=object)
        self.retract_raw = np.array(_withdraw, dtype=object)
        self.z_approach_raw = np.array(_z_approach, dtype=object)
        self.z_withdraw_raw = np.array(_z_withdraw, dtype=object)

        self.measurements = self.approach_raw.shape[0]

    def plot_raw(
        self,
        curve_number = 1,
        return_fig = False
    ):
        '''
        Function to plot individual, unprocessed force curves. Curve number to
        plot must be given as an input <.plot_raw(n)>
        '''
        if self.file_name[-3:] != 'nid':
            fig = go.Figure()
            fig.add_trace(go.Scatter(y = self.approach_raw[:,curve_number], x = self.z_position_raw[:,curve_number], mode='lines', name = 'Approach curve (raw)'))
            fig.add_trace(go.Scatter(y = self.retract_raw[:,curve_number], x = self.z_position_raw[:,curve_number], mode='lines', name = 'Retract curve (raw)'))
            fig.update_layout(
                yaxis_title_text='Force (nN)',
                xaxis_title_text='Piezo position (nm)',
            )
            fig.show()
            
            if return_fig == True:
                return fig


        else:
            fig = go.Figure()
            fig.add_trace(go.Scatter(y = self.approach_raw[curve_number], x = self.z_approach_raw[curve_number], mode='lines', name = 'Approach curve (raw)'))
            fig.add_trace(go.Scatter(y = self.retract_raw[curve_number], x = self.z_withdraw_raw[curve_number], mode='lines', name = 'Retract curve (raw)'))
            fig.update_layout(
                yaxis_title_text='Force (N)',
                xaxis_title_text='Piezo position (m)',
            )
            fig.show()
            
            if return_fig == True:
                return fig

    def baseline(
        self,
        start_pos = 0.45,
        end_pos = 0.8,
        max_approach_noise = 1000,
        max_retract_noise = 1000
    ):
        '''
        Function to adjust force curve baseline to zero by taking the mean value
        of a specified region of the approach curve. The default is from 0.45*z
        to 0.8*z, starting at the contact side of the curve. The start and end
        points may be specified using the 'start_pos' and 'end_pos' inputs to
        account for a longer/shorter baseline or regions of noise. Noisy curves
        may be removed by specifying a maximum standard deviation for the baseline
        region separatley for the approach and retract curves using the inputs
        'max_approach_noise' and 'max_retract_noise' respectivley. The defaults for
        each are 1000 nN (i.e. all curves retained).
        '''
        self.approach = np.zeros([self.samps_line, len(self.approach_raw)])
        self.retract = np.zeros([self.samps_line, len(self.approach_raw)])
        self.z_approach = np.zeros([self.samps_line, len(self.approach_raw)])
        self.z_withdraw = np.zeros([self.samps_line, len(self.approach_raw)])

        i = 0
        
        for curve_number in range(0, self.measurements):

            try:

                if self.file_name[-3:] != 'nid':
                    _approach = self.approach_raw[:,curve_number]
                    _retract = self.retract_raw[:,curve_number]
                else:
                    _approach = self.approach_raw[curve_number]
                    _retract = self.retract_raw[curve_number]
                    

                baseline_start = int(len(_approach) * start_pos)
                baseline_end = int(len(_approach) * end_pos)
                baseline_region = np.arange(baseline_start,baseline_end)

                _approach_region = _approach[baseline_region]
                _retract_region = _retract[baseline_region]

                _approach_mean = np.mean(_approach_region)

                adjusted_approach = _approach - _approach_mean
                adjusted_retract =  _retract - _approach_mean

                approach_dev = np.std(_approach_region)
                retract_dev = np.std(_retract_region)

                if self.file_name[-3:] != 'nid':
                    _z = self.z_position_raw[:,curve_number]
                else:
                    _z_a = self.z_approach_raw[curve_number]
                    _z_w = self.z_withdraw_raw[curve_number]

                if len(adjusted_approach) < self.samps_line:
                    blank = np.empty(self.samps_line - len(adjusted_approach))
                    blank[:] = np.nan

                    adjusted_approach = np.append(adjusted_approach, blank)
                    _z_a = np.append(_z_a, blank)

                if len(adjusted_retract) < self.samps_line:
                    blank = np.empty(self.samps_line - len(adjusted_retract))
                    blank[:] = np.nan
                    
                    adjusted_retract =  np.append(adjusted_retract, blank)
                    _z_w = np.append(_z_w, blank)

                if approach_dev < max_approach_noise and retract_dev < max_retract_noise:

                    if self.file_name[-3:] != 'nid':
                        self.z_approach[:,i] = _z
                        self.z_withdraw[:,i] = _z
                        self.approach[:,i] = adjusted_approach
                        self.retract[:,i] = adjusted_retract

                    else:
                        self.z_approach[:,i] = _z_a[::-1] * -1 * 1e9
                        self.z_withdraw[:,i] = _z_w[::-1] * -1 * 1e9
                        self.approach[:,i] = adjusted_approach[::-1] * 1e9
                        self.retract[:,i] = adjusted_retract[::-1] * 1e9

                    i += 1
            
            except:
                print('Error processing force curve number', curve_number, ' (data skipped)') 

        self.approach = self.approach[:,:i]
        self.retract = self.retract[:,:i]

        if self.file_name[-3:] != 'nid':
            self.z_approach = self.z_approach[:,:i]
            self.z_withdraw = self.z_withdraw[:,:i]

    def contact(self):
        '''
        Function to align the contact point of the approach curve with zero by
        finding the first point to cross the axis and interpolating between this
        and the previous value. Note this method may be unstable for noisy curves.
        The tip contact height and maximum indentation depth are also saved.
        '''

        self.contact_point = np.zeros(self.z_approach.shape[1])
        self.indent_depth = np.zeros(self.z_approach.shape[1])
        
        for i in range(0, self.z_approach.shape[1]):
            _approach = self.approach[:,i]
            _retract = self.retract[:,i]
            _z = self.z_approach[:,i]

            try:
                j = 0

                while _approach[j] > 0 or np.isnan(_approach[j]):
                    j += 1

                y = _z[j-1], _z[j]
                x = _approach[j-1], _approach[j]

                f = interp.interp1d(x,y)
                intercept = f(0)

                if np.isnan(intercept) == False:
                    self.z_approach[:,i] = self.z_approach[:,i] - intercept
                    self.z_withdraw[:,i] = self.z_withdraw[:,i] - intercept
                    self.contact_point[i] = intercept
                    self.indent_depth[i] = next(n for n in self.z_approach[:,i] if n == n)

            except:
                print('WARNING: Could not locate contact point for curve number ', i, '. Consider checking baseline alignment.')

    def adjust_tip_position(
        self
    ):
        '''
        Convert piezo position to actual tip position.
        '''

        self.z_approach_piezo = self.z_approach
        self.z_withdraw_piezo = self.z_withdraw

        for i in range(0, self.z_approach.shape[1]):

            _z_approach = self.z_approach[:,i]
            _z_withdraw = self.z_withdraw[:,i]
            _approach = self.approach[:,i]
            _retract = self.retract[:,i]
                
            tip_approach = _z_approach + _approach / self.spr_const
            tip_retract = _z_withdraw + _retract / self.spr_const

            self.z_approach[:,i] = tip_approach
            self.z_withdraw[:,i] = tip_retract

            self.indent_depth[i] = next(n for n in self.z_approach[:,i] if n == n)

    def plot_adjusted(
        self,
        curve_number = 1,
        return_fig = False
    ):
        '''
        Function to plot individual, processed force curves. Curve number to
        plot must be given as an input <.plot_adjusted(n)>
        '''
        fig = go.Figure()
        fig.add_trace(go.Scatter(y = self.approach[:,curve_number], x = self.z_approach[:,curve_number], mode='lines', name = 'Approach curve'))
        fig.add_trace(go.Scatter(y = self.retract[:,curve_number], x = self.z_withdraw[:,curve_number], mode='lines', name = 'Retract curve'))
        fig.update_layout(
            yaxis_title_text='Force (nN)',
            xaxis_title_text='Distance, z (nm)',
        )
        fig.show()
            
        if return_fig == True:
            return fig

    def plot_curves(self,
        return_fig = False):
        '''
        Function to plot all processed force curves
        '''

        trace_1 = []
        trace_2 = []

        for step in range(0, self.z_approach.shape[1]):

            trace_1.append(go.Scatter(
                        visible=False,
                        name= 'Approach ' + str(step),
                        y = self.approach[:, step],
                        x = self.z_approach[:, step]
                    ))

            trace_2.append(go.Scatter(
                        visible=False,
                        name= 'Retract ' + str(step),
                        y = self.retract[:, step],
                        x = self.z_withdraw[:, step]
                    ))

        fig = go.Figure(data = trace_1 + trace_2)

        n_trace = int(len(fig.data) / 2)

        # Make 1st trace visible
        fig.data[0].visible = True
        fig.data[n_trace].visible = True

        # Create and add slider
        steps = []
        for i in range(n_trace):
            step = dict(
                method="update",
                args=[{"visible": [False] * len(fig.data)},
                    {"title": "Slider switched to experiment: " + str(i)}],
            )
            j = int(n_trace+i)
            step["args"][0]["visible"][i] = True
            step["args"][0]["visible"][j] = True
            steps.append(step)

        sliders = [dict(
            pad={"t": 50},
            steps=steps
        )]

        fig.update_layout(
            sliders=sliders,
            yaxis_title_text='Force (nN)',
            xaxis_title_text='Distance, z (nm)',
        )

        fig.show()
            
        if return_fig == True:
            return fig

    def delete_curve(self,*args):
        '''
        Function to manually remove erroneous or highly noisy curves. Specify the
        curve(s) to remove in the input <.delete_curve(i,j,k)>
        '''

        curves = []
        for curve_i in args:
            curves = np.append(curves, curve_i)

        i = 0
        for curve_number in curves:

            curve_int = int(curve_number)

            self.approach = np.delete(self.approach, curve_int, axis = 1)
            self.retract = np.delete(self.retract, curve_int, axis = 1)
            self.z_approach = np.delete(self.z_approach, curve_int, axis = 1)
            self.z_withdraw = np.delete(self.z_withdraw, curve_int, axis = 1)

            try:
                self.adhesion = np.delete(self.adhesion, curve_int, axis = 1)
            except:
                pass

            try:
                self.modulus = np.delete(self.modulus, curve_int, axis = 1)
            except:
                pass

            try:
                self.z_approach_piezo = np.delete(self.z_approach_piezo, curve_int, axis = 1)
            except:
                pass

            try:
                self.z_withdraw_piezo = np.delete(self.z_withdraw_piezo, curve_int, axis = 1)
            except:
                pass

            try:
                self.contact_point = np.delete(self.contact_point, curve_int, axis = 1)
            except:
                pass

            try:
                self.indent_depth = np.delete(self.indent_depth, curve_int, axis = 1)
            except:
                pass

            try:
                self.snap_in = np.delete(self.snap_in, curve_int, axis = 1)
            except:
                pass

            try:
                self.max_force = np.delete(self.max_force, curve_int, axis = 1)
            except:
                pass
            

            i += 1
            for j in range(i, len(args)):
                if curves[j] > curve_number:
                    curves[j] = curves[j] - 1
    
    def save_data(
        self,
        filename = []
    ):
        '''
        Function to save current variables in '.npz' format. The file name and path
        for saving can be given as an input. If no input is given a GUI will prompt
        the user to select a location and file name. In both case no file extension
        '''
        if len(filename) == 0:
            output_path = gui.filesavebox()
        else:
            output_path = filename

        np.savez(
            output_path,
            approach = self.approach,
            retract = self.retract,
            z_approach = self.z_approach,
            z_withdraw = self.z_withdraw,
            z_approach_piezo = self.z_approach_piezo,
            z_withdraw_piezo = self.z_withdraw_piezo,
            adhesion = self.adhesion,
            modulus = self.modulus,
            data_offset = self.data_offset,
            data_length =self.data_length,
            ramp_size = self.ramp_size,
            samps_line = self.samps_line,
            zsens = self.zsens,
            zscale = self.zscale,
            def_sens = self.def_sens,
            spr_const = self.spr_const,
            file_name = self.file_name,
            run_name = self.run_name,
            measurements = self.measurements,
            contact_point = self.contact_point,
            indent_depth = self.indent_depth,
            snap_in = self.snap_in,
            max_force = self.max_force
        )

    def load_data(
        self,
        filename = []
    ):
        '''
        Function to import previously saved variables in '.npz' format. As with saving,
        the file name and path can be given as an input or left blank to use a GUI.
        '''

        if len(filename) == 0:
            input_path = gui.fileopenbox()
        else:
            input_path = filename
        
        data = np.load(input_path)

        self.approach = data['approach']
        self.retract = data['retract']
        self.z_approach = data['z_approach']
        self.z_withdraw = data['z_withdraw']
        self.adhesion = data['adhesion']
        self.modulus = data['modulus']
        self.data_offset = data['data_offset']
        self.data_length = data['data_length']
        self.ramp_size = data['ramp_size']
        self.samps_line = data['samps_line']
        self.zsens = data['zsens']
        self.zscale = data['zscale']
        self.def_sens = data['def_sens']
        self.spr_const = data['spr_const']
        self.file_name = data['file_name']
        self.run_name = data['run_name']
        self.measurements = data['measurements']
        self.z_approach_piezo = data['z_approach_piezo']
        self.z_withdraw_piezo = data['z_withdraw_piezo']
        self.contact_point = data['contact_point']
        self.indent_depth = data['indent_depth']
        self.snap_in = data['snap_in']
        self.max_force = data['max_force']

    def calc_adhesion(
        self,
        plot_hist = False,
        return_fig = False
    ):
        '''
        Funciton to calculate the adhesion value for each curve by finding the minimum
        point on the retact curve. A histogram of calculated values can be plotted by
        setting the 'plot_hist' input to 'True'. The snap in force and maximum indentation
        force are also saved.
        '''

        self.adhesion = np.zeros(self.z_approach.shape[1])
        self.snap_in = np.zeros(self.z_approach.shape[1])
        self.max_force = np.zeros(self.z_approach.shape[1])

        for curve_number in range(0, self.z_approach.shape[1]):
            self.adhesion[curve_number] = np.nanmin(self.retract[:, curve_number]) * -1
            self.snap_in[curve_number] = np.nanmin(self.approach[:, curve_number]) * -1
            self.max_force[curve_number] = np.nanmax(self.approach[:, curve_number])

        if plot_hist is True:
            fig = go.Figure(data = [go.Histogram(x = self.adhesion)])
            fig.update_layout(
                xaxis_title_text='Adhesion (nN)',
                yaxis_title_text='Count',
            )
            fig.show()
            
            if return_fig == True:
                return fig

        print('')
        try:
            print(self.run_name)
        except:
            pass

        print('Mean adhesion = %(mean).2f nN' % {'mean': np.mean(self.adhesion)})
        print('Standard deviation = %(std).2f nN' % {'std': np.std(self.adhesion)})

    def overlay_adhesion_hist(
        self,
        *all_adhesion,
        return_fig = False
    ):
        '''
        Funciton to plot a histogram comparing adhesion values for multiple experiments.
        A separate instance of the AFM class containing the data for each should be
        given as the inputs
        '''
        fig = go.Figure()

        for single in all_adhesion:
            fig.add_trace(go.Histogram(x = single.adhesion,
            name = single.run_name
        ))

        fig.update_layout(
                xaxis_title_text='Adhesion (nN)',
                yaxis_title_text='Count',
                barmode='overlay'
            )
        fig.update_traces(opacity=0.75)
        fig.show()
            
        if return_fig == True:
            return fig

    def overlay_adhesion_box(
        self,
        *all_adhesion,
        return_fig = False
    ):
        '''
        Funciton to produce a box plot comparing adhesion values for multiple experiments.
        A separate instance of the AFM class containing the data for each should be
        given as the inputs
        '''
        fig = go.Figure()

        for single in all_adhesion:
            fig.add_trace(go.Box(x = single.adhesion,
            name = single.run_name
        ))

        fig.update_layout(
                xaxis_title_text='Adhesion (nN)'
            )
            
        fig.show()
            
        if return_fig == True:
            return fig

    def overlay_adhesion_violin(
        self,
        *all_adhesion,
        return_fig = False
    ):
        '''
        Funciton to produce a violin plot comparing adhesion values for multiple experiments.
        A separate instance of the AFM class containing the data for each should be
        given as the inputs
        '''
        fig = go.Figure()

        for single in all_adhesion:
            fig.add_trace(go.Violin(x = single.adhesion,
            name = single.run_name
        ))

        fig.update_layout(
                xaxis_title_text='Adhesion (nN)'
            )
            
        fig.show()
            
        if return_fig == True:
            return fig

    def overlay_adhesion_bar(
        self,
        *all_adhesion,
        return_fig = False
    ):
        '''
        Funciton to produce a bar chart comparing adhesion values for multiple experiments.
        A separate instance of the AFM class containing the data for each should be
        given as the inputs
        '''
        fig = go.Figure()

        mean_adhesion = []
        std_adhesion = []
        trace = []

        for single in all_adhesion:
            mean_adhesion = np.append(mean_adhesion, np.mean(single.adhesion))
            std_adhesion = np.append(std_adhesion, np.std(single.adhesion))
            trace = np.append(trace, single.run_name)
        
        fig.add_trace(go.Bar(
            y = mean_adhesion,
            x = trace,
            error_y = dict(type = 'data', array = std_adhesion)
        ))

        fig.update_layout(
                yaxis_title_text='Adhesion (nN)'
            )
            
        fig.show()
            
        if return_fig == True:
            return fig

    def calc_modulus(
        self,
        poisson_ratio = 0.5,
        indenter_radius = 10 * 1e-9,
        plot_hist = False,
        return_fig = False,
        soft_indenter = False,
        indenter_poisson_ratio = 0.5,
        indenter_modulus = 1000
    ):
        '''
        Funciton to calculate the modulus value for each curve using the Hertz model.
        A histogram of calculated values can be plotted by setting the 'plot_hist'
        input to 'True'
        '''
        self.modulus = np.zeros(self.z_approach.shape[1])

        if soft_indenter is True:
            indenter_term = (1 - indenter_poisson_ratio ** 2) / (indenter_modulus * 1e6)
        else:
            indenter_term = 0

        for curve_number in range(0, self.z_approach.shape[1]):

            force = self.approach[:,curve_number] * 1e-9
            depth = self.z_approach[:,curve_number] * 1e-9

            indent_fit = LinearRegression(fit_intercept = False)

            x = depth
            y = force

            x = x[~np.isnan(y)]
            y = y[~np.isnan(y)]

            y = y[~np.isnan(x)]
            x = x[~np.isnan(x)]

            x = x[y>0]
            y = y[y>0]

            y = y[x<0]
            x = x[x<0]
            
            x = x.reshape(-1, 1)
            y = y.reshape(-1, 1)

            max_depth = np.min(x)

            if len(x) == 0:

                self.modulus[curve_number] = np.nan
                
            else:

                indent_fit.fit(x, y)
                max_force = indent_fit.predict(max_depth.reshape(-1, 1))

                term_1 = (4/3)
                term_2 = 1 / (1 - poisson_ratio ** 2)
                term_3 = 1 / max_force
                term_4 = np.sqrt(indenter_radius)
                term_5 = np.absolute(max_depth) ** (3/2)

                terms = (term_1* term_3 * term_4 * term_5 - indenter_term) * term_2

                self.modulus[curve_number] = (1 / terms) * 1e-6

        
        if plot_hist is True:
            fig = go.Figure(data=[go.Histogram(x = self.modulus)])
            fig.update_layout(
                xaxis_title_text='Modulus (MPa)',
                yaxis_title_text='Count',
            )
            fig.show()
            
        if return_fig == True:
            return fig

        print('')
        try:
            print(self.run_name)
        except:
            pass

        print('Mean modulus = %(mean).2f MPa (Hertz model)' % {'mean': np.mean(self.modulus)})
        print('Standard deviation = %(std).2f MPa' % {'std': np.std(self.modulus)})

    def calc_modulus_sneddon(
        self,
        poisson_ratio = 0.5,
        opening_angle = 35,
        plot_hist = False,
        return_fig = False,
        start_dist = 1,
        end_dist = 0,
        intercept = True
    ):
        '''
        Funciton to calculate the modulus value for each curve using the Sneddon model.
        This model is appropriate for a conical indenter where the indentation depth is
        at least 3 times greater than the tip radius. The fitting region on the indentation
        curve can be selected by setting the 'start_dist' and 'end_dist' as a fraction
        of the total indent depth, where start distance is the highest indentation depth to use.
        The intercept option can be set to 'False' to fix the intercept at zero.
        A histogram of calculated values can be plotted by setting the 'plot_hist'
        input to 'True'.
        '''
        self.modulus = np.zeros(self.z_approach.shape[1])

        for curve_number in range(0, self.z_approach.shape[1]):

            force = self.approach[:,curve_number] * 1e-9
            depth = self.z_approach[:,curve_number] * 1e-9

            max_depth = next(n for n in depth if n == n) * np.array(start_dist)
            min_depth = next(n for n in depth if n == n) * np.array(end_dist)

            force = force[depth < min_depth]
            depth = depth[depth < min_depth]
            force = force[depth > max_depth]
            depth = depth[depth > max_depth]

            indent_fit = LinearRegression(fit_intercept = intercept)

            x = depth
            y = force

            x = x[~np.isnan(y)]
            y = y[~np.isnan(y)]

            y = y[~np.isnan(x)]
            x = x[~np.isnan(x)]

            x = x[y>0]
            y = y[y>0]

            y = np.sqrt(y)
            
            x = x.reshape(-1, 1)
            y = y.reshape(-1, 1)

            if len(x) == 0:

                self.modulus[curve_number] = np.nan
                
            else:

                indent_fit.fit(x, y)

                c = indent_fit.coef_

                term_1 = np.pi/2
                term_2 = 1 / np.tan(np.deg2rad(opening_angle))
                term_3 = (1 - np.array(poisson_ratio) ** 2)

                E = c ** 2 * term_1 * term_2 * term_3  * 1e-6

                self.modulus[curve_number] = E
        
        if plot_hist is True:
            fig = go.Figure(data=[go.Histogram(x = self.modulus)])
            fig.update_layout(
                xaxis_title_text='Modulus (MPa)',
                yaxis_title_text='Count',
            )
            fig.show()
            
        if return_fig == True:
            return fig

        print('')
        try:
            print(self.run_name)
        except:
            pass

        print('Mean modulus = %(mean).2f MPa (Sneddon Model)' % {'mean': np.mean(self.modulus)})
        print('Standard deviation = %(std).2f MPa' % {'std': np.std(self.modulus)})

    def calc_modulus_pyramid(
        self,
        poisson_ratio = 0.5,
        face_angle = 35,
        plot_hist = False,
        return_fig = False
    ):
        '''
        Funciton to calculate the modulus value for each curve using the four sided pyramid model.
        A histogram of calculated values can be plotted by setting the 'plot_hist'
        input to 'True'
        '''
        self.modulus = np.zeros(self.z_approach.shape[1])

        for curve_number in range(0, self.z_approach.shape[1]):
            _approach = self.approach[:,curve_number]
            _z = self.z_approach[:,curve_number]

            force = _approach[np.isfinite(_approach)][0] * 1e-9
            depth = _z[np.isfinite(_approach)][0] * 1e-9

            term_1 = 1/np.sqrt(2)
            term_2 = 1 / (1 - poisson_ratio ** 2)
            term_3 = 1 / force
            term_4 = np.tan(np.deg2rad(face_angle))
            term_5 = np.absolute(depth) ** 2

            terms = term_1 * term_2 * term_3 * term_4 * term_5

            self.modulus[curve_number] = (1 / terms) * 1e-6
        
        if plot_hist is True:
            fig = go.Figure(data=[go.Histogram(x = self.modulus)])
            fig.update_layout(
                xaxis_title_text='Modulus (MPa)',
                yaxis_title_text='Count',
            )
            fig.show()
            
        if return_fig == True:
            return fig

        print('')
        try:
            print(self.run_name)
        except:
            pass

        print('Mean modulus = %(mean).2f MPa (Four sided pyramid)' % {'mean': np.mean(self.modulus)})
        print('Standard deviation = %(std).2f MPa' % {'std': np.std(self.modulus)})

    def overlay_modulus_hist(
        self,
        *all_modulus,
        return_fig = False
    ):
        '''
        Funciton to plot a histogram comparing modulus values for multiple experiments.
        A separate instance of the AFM class containing the data for each should be
        given as the inputs
        '''
        fig = go.Figure()

        for single in all_modulus:
            fig.add_trace(go.Histogram(x = single.modulus,
            name = single.run_name
        ))

        fig.update_layout(
                xaxis_title_text='Modulus (MPa)',
                yaxis_title_text='Count',
                barmode='overlay'
            )
        fig.update_traces(opacity=0.75)
        fig.show()
            
        if return_fig == True:
            return fig
    
    def overlay_modulus_box(
        self,
        *all_modulus,
        return_fig = False
    ):
        '''
        Funciton to produce a box plot comparing modulus values for multiple experiments.
        A separate instance of the AFM class containing the data for each should be
        given as the inputs
        '''
        fig = go.Figure()

        for single in all_modulus:
            fig.add_trace(go.Box(x = single.modulus,
            name = single.run_name,
        ))

        fig.update_layout(
                xaxis_title_text='Modulus (MPa)'
            )
            
        fig.show()
            
        if return_fig == True:
            return fig

    def overlay_modulus_violin(
        self,
        *all_modulus,
        return_fig = False
    ):
        '''
        Funciton to produce a violin plot comparing modulus values for multiple experiments.
        A separate instance of the AFM class containing the data for each should be
        given as the inputs
        '''
        fig = go.Figure()

        for single in all_modulus:
            fig.add_trace(go.Violin(x = single.modulus,
            name = single.run_name,
        ))

        fig.update_layout(
                xaxis_title_text='Modulus (MPa)'
            )
            
        fig.show()
            
        if return_fig == True:
            return fig

    def overlay_modulus_bar(
        self,
        *all_modulus,
        return_fig = False
    ):
        '''
        Funciton to produce a bar chart comparing modulus values for multiple experiments.
        A separate instance of the AFM class containing the data for each should be
        given as the inputs
        '''
        fig = go.Figure()
        mean_modulus = []
        std_modulus= []
        trace = []

        for single in all_modulus:
            mean_modulus = np.append(mean_modulus, np.mean(single.modulus))
            std_modulus = np.append(std_modulus, np.std(single.modulus))
            trace = np.append(trace, single.run_name)
        
        fig.add_trace(go.Bar(
            y = mean_modulus,
            x = trace,
            error_y = dict(type = 'data', array = std_modulus)
        ))

        fig.update_layout(
                yaxis_title_text='Modulus (MPa)',
            )

        fig.show()

        if return_fig == True:
            return fig

    def plot_adhesion_modulus(self,
        return_fig = False):
        '''
        Function to produce a scatter plot of adhesion vs. modulus values for a single
        experiment
        '''
        fig = go.Figure(go.Scatter(x = self.adhesion, y = self.modulus, mode='markers'))
        fig.update_layout(
                xaxis_title_text='Adhesion (nN)',
                yaxis_title_text='Modulus (MPa)'
            )
        fig.show()
            
        if return_fig == True:
            return fig

    def force_map(self,
        x_cells = 10,
        y_cells = 10,
        x_scale = 10,
        y_scale = 10,
        return_fig = False,
        auto_cell = True,
        plot = 'adhesion',
        topography_3d = False
    ):

        plot_types = ['adhesion', 'modulus', 'topography', 'indent', 'max_force', 'snap_in']
        member = plot in plot_types

        if member == False:
            print('Incorrect plot type specified. Available plots are adhesion, modulus, topography, indent, max_force and snap_in.')

        else:

            if auto_cell == True:
                x_cells = int(np.sqrt(self.approach.shape[1]))
                y_cells = x_cells

            x_pos = np.zeros(x_cells * y_cells)
            y_pos = np.zeros(x_cells * y_cells)
            adhesion = np.zeros(x_cells * y_cells)
            modulus = np.zeros(x_cells * y_cells)
            height = np.zeros(x_cells * y_cells)
            depth = np.zeros(x_cells * y_cells)
            force = np.zeros(x_cells * y_cells)
            snap = np.zeros(x_cells * y_cells)

            x_counter = 1
            y_counter = 1
            loop_counter = 0
            updown = 1

            j = 0

            while j < x_cells * y_cells:

                x_pos[j] = x_counter
                y_pos[j] = y_counter

                if plot == 'adhesion':
                    adhesion[j] = self.adhesion[j]

                if plot == 'modulus':
                    modulus[j] = self.modulus[j]

                if plot == 'indent':
                    depth[j] = self.indent_depth[j]

                if plot == 'max_force':
                    force[j] = self.max_force[j]

                if plot == 'snap_in':
                    snap[j] = self.snap_in[j]

                height[j] = self.contact_point[j]

                loop_counter += 1

                if loop_counter == x_cells:

                    y_counter += 1
                    j += 1

                    if j == x_cells * y_cells:
                        break

                    x_pos[j] = x_counter
                    y_pos[j] = y_counter
                    
                    if plot == 'adhesion':
                        adhesion[j] = self.adhesion[j]

                    if plot == 'modulus':
                        modulus[j] = self.modulus[j]

                    if plot == 'indent':
                        depth[j] = self.indent_depth[j]

                    if plot == 'max_force':
                        force[j] = self.max_force[j]

                    if plot == 'snap_in':
                        snap[j] = self.snap_in[j]

                    height[j] = self.contact_point[j]

                    if updown == 1:
                        updown = 2
                        loop_counter = 1
                    elif updown == 2:
                        updown = 1
                        loop_counter = 1

                if updown == 1:
                    x_counter += 1
                elif updown == 2:
                    x_counter -= 1

                j += 1

            x_grid = x_pos
            y_grid = y_pos

            x_pos = x_pos * x_scale/x_cells
            y_pos = y_pos * y_scale/y_cells

            height = height - height[0]

            if plot == 'adhesion':
                plt_title = 'Adhesion (nN)'
                plt_data = adhesion
            elif plot == 'modulus':
                plt_title = 'Young''s modulus (MPa)'
                plt_data = modulus
            elif plot == 'topography':
                plt_title = 'Height (nm)'
                plt_data = height
            elif plot == 'indent':
                plt_title = 'Indentation depth (nm)'
                plt_data = depth
            elif plot == 'max_force':
                plt_title = 'Max. indentation force (nN)'
                plt_data = force
            elif plot == 'snap_in':
                plt_title = 'Snap in force (nN)'
                plt_data = snap

            if topography_3d == False:

                fig = go.Figure(data=go.Heatmap(
                        x = x_pos,
                        y = y_pos,
                        z = plt_data,
                        type = 'heatmap',
                        colorscale = 'YlOrBr',
                        colorbar=dict(title=plt_title)
                        ))

                fig.update_layout(yaxis = dict(scaleanchor = 'x'))
                fig.update_layout(plot_bgcolor='rgba(0,0,0,0)')

                axis_template = dict(
                            showgrid = False, zeroline = False,
                            linecolor = 'white', showticklabels = True,
                            ticks = '' )

                fig.update_layout(margin = dict(t=200,r=200,b=200,l=200),
                    xaxis = axis_template,
                    yaxis = axis_template,
                    showlegend = False,
                    width = 700, height = 700,
                    autosize = False,
                    xaxis_title="X Position (um)",
                    yaxis_title="Y Position (um)")

                fig.update_layout(
                    xaxis = dict(
                        tickmode = 'linear',
                        tick0 = 0,
                        dtick = 1
                    ),
                        yaxis = dict(
                        tickmode = 'linear',
                        tick0 = 0,
                        dtick = 1
                    )
                )

            elif topography_3d == True:

                x3 = np.zeros([x_cells, y_cells])
                y3 = np.zeros([x_cells, y_cells])
                z3 = np.zeros([x_cells, y_cells])
                d3 = np.zeros([x_cells, y_cells])

                for i in range(0,len(plt_data)):

                    x3[int(x_grid[i])-1 , int(y_grid[i])-1] = x_pos[i]
                    y3[int(x_grid[i])-1 , int(y_grid[i])-1] = y_pos[i]
                    z3[int(x_grid[i])-1 , int(y_grid[i])-1] = height[i]
                    d3[int(x_grid[i])-1 , int(y_grid[i])-1] = plt_data[i]

                fig = go.Figure(go.Surface(x=x3, y=y3, z=z3, surfacecolor=d3,
                                colorbar=dict(title=plt_title)))

                fig.update_layout(scene = dict(
                                xaxis_title='X Position (um)',
                                yaxis_title='Y Position (um)',
                                zaxis_title='Z Position (nm)'),
                                margin=dict(r=20, b=10, l=10, t=10))

            fig.show()

            if return_fig == True:
                return fig