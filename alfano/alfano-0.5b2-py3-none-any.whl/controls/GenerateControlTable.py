#!python
# -*- coding: utf-8 -*-
"""
Created on Sun May  6 18:36:48 2018
@version 0.5a1

@description:
This Module generates a JSON file containing the values of the Alfano control variable
by orbit ratio for any valid value of the Alfano costate. This file is used by 
YawAngles.py to return the yaw plane thrust angle to a GMAT mission script for any
value of orbit ratio from 1-to-10.

An Excel workbook named YawAngleGenerator.xlsx is created in the current directory 
when the module is executed. The workbook is not used further, but is provided for 
inspection and numerical analysis.
  
AlfanoLib.py from the alfano utilities package is used to compute the values
of lambda given linear arrays of cv and orbit ratio.  Once this array is computed 
the array is inverted such given a value of lambda the corresponding thrust control
value can be returned for each value of orbit ratio.  This is the solution to the
inverse function of Phi() in Alfano's paper.  

The optimum value of the lambda costate must be determined by the mission planner
in order to obtain the feasible values for his mission.  The output workbook provides
the "dida" worksheet to assist an initial guess which gives the increment of inclination
change per increment of orbit ratio in columns for each valid lambda value.

Graphical means of determining the optimum lambda value are given in Vallado, 
Figure 6-24.

Error analysis of this algorithm shows that for a 500x500 table size,
the max error in lambda is 0.004 and in orbit ratio 0.01.  The error
is computed on inv_phi as the difference in given value and table value.

Reference Wiesel and Alfano, 1983, "Optimal Many-Revolution Orbit Transfer".
Reference Sec. 6.7, Vallado, "Fundamentals of Astrodynamics and Applications," 
4th edition.

@author: Colin Helms
@author_email: colinhelms@outlook.com

@license
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>

@license
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>

@change Log:
    06 May 2018, baseline version, generates 3D plot using AlfanoLib.
    13 May 2018, added mainline code to generate YawAngleGenerator.xlsx.
    15 May 2018, added functions to read workbook, write ControlScaleFactors.json.
    20 May 2018, changed names of output files to be more general and terse.
    09 Mar 2019, added capabilty to generate full controls in Transfer sheet using macros
    15 Mar 2019, New high precision algorithm, per "Simulating Alfano Trajectory ...r0.4.docx"
    21 May 2019, Factored out lin_interp() to AlfanoLib.  Used in YawAngles.py.
    23 Feb 2022, Fixed Issue 02212022, Implemented a shared file containing path to controls file.
"""
import os
import platform
import getpass
import logging
import traceback
import numpy as np
import xlsxwriter as xl
from xlsxwriter import utility as xlut
from PyQt5.QtWidgets import(QApplication, QFileDialog)
from pathlib import Path
from alfano import AlfanoLib as alf

jfilename = 'Controls.json'
""" This file is named following an interface convention with "YawAngles.py". """

def altitude(a, cv):
    """ Compute phi all at once.
    Note that if computing the costate, the costate function should take the
    reciprocal of alfano.phi().
    """
    k = alf.cmp_ell_int_1st_kind(cv)
    e = alf.cmp_ell_int_2nd_kind(cv)
    
    p = alf.alfano_P(cv, k)
    r = alf.alfano_R(cv, k, e)
    
    r_over_p = np.true_divide(r, p)
    
    with np.errstate(divide='ignore', invalid='ignore'):
        """ Avoid divide by zero warning. Courtesy of Stack Overflow.       
        https://stackoverflow.com/questions/26248654/numpy-return-0-with-divide-by-zero 
        """
        alt = alf.PREC_ORBITR * np.true_divide(r_over_p, 2*a)
        alt[alt == np.inf] = 0
        """ alt[ alt = np.inf( alt )] = 0 means find the positions where alt is infinite  
        and set the not-finite values to 0.
        """
        
        alt = np.nan_to_num(alt)
        """ Invalid sets to NaN """
        
    return alt

def lin_interp(l_hi, l_lo, lamb, u_lo, u_hi):
    """ linear interpolation returning value between u_hi and u_lo proportional to 
    lamb between l_hi and l_lo.
    
    Calling procedure may need to round.
    """
    return u_lo + (u_hi - u_lo) * (l_hi - lamb)/(l_hi - l_lo)

def export_controls(data: dict, jfile = Path(jfilename)):
    """ Function is used to write out a JSON file containing computed Alfano 
    control values by rows of orbit ratio and columns of lambda costate.
    """
    msg = 'Please wait again.  Translating controls to JSON format via AlfanoLib.dump'
    logging.info(msg)
    print(msg)

    try:       
        """ Dump data to JSON formatted text file """
        with open(jfile, 'w+') as fp:
            alf.dump(data, fp)
            """ Use overloaded dump function.  Fixed to serialize numpy ndarray. """
            
    except OSError as e:
        logging.error("Unable to write file: %s. %s", e.filename, e.strerror)

    except Exception as e:
        lines = traceback.format_exc().splitlines()
        logging.error("Exception writing JSON file: %s\n%s\n%s", e.__doc__, lines[0], lines[-1])
        
    logging.info("{0} trajectory data file written.".format(jfile))
        
if __name__ == "__main__":
    """ Build and export the control table for simulation and flight. """
    
    __spec__ = None
    """ Necessry tweak to get Spyder IPython to execute this code. 
    See:
    https://stackoverflow.com/questions/45720153/
    python-multiprocessing-error-attributeerror-module-main-has-no-attribute
    """
                
    logging.basicConfig(
            filename='./GenControls.log',
#            level=logging.INFO,
            level=logging.DEBUG,
            format='%(asctime)s %(filename)s %(levelname)s:\n%(message)s', datefmt='%d%B%Y_%H:%M:%S')

    logging.info("!!!!!!!!!! Control Table Generation Started !!!!!!!!!!")
    
    host_attr = platform.uname()
    logging.info('User Id: %s\nNetwork Node: %s\nSystem: %s, %s, \nProcessor: %s', \
                 getpass.getuser(), \
                 host_attr.node, \
                 host_attr.system, \
                 host_attr.version, \
                 host_attr.processor)
   

    app = QApplication([])
    
    xfile = QFileDialog().getSaveFileName(None, 
                       'Select Excel File to Record Generated Costates.', 
                       os.getenv('USERPROFILE'),
                       filter='Excel files(*.xlsx *.xlsm)')

    #xfile = r'./YawAngleGeneratorV2.xlsx'    
    logging.info('Selected Excel Costate file is %s', xfile[0])
    
    wb = xl.Workbook(xfile[0], {'nan_inf_to_errors': True})
    
    cell_format1 = wb.add_format() 
    cell_format1.set_text_wrap()
    cell_format1.set_align('top')
    cell_format1.set_align('left')
    
    cell_bold = wb.add_format() 
    cell_bold.set_bold()
    cell_bold.set_text_wrap()
    cell_bold.set_align('top')
    cell_bold.set_align('center')

    summarySht = wb.add_worksheet('summary')
    costateSht = wb.add_worksheet('costate')
    trajSht = wb.add_worksheet('cv')
    iaSht = wb.add_worksheet('dida')
    xferSht = wb.add_worksheet('transfers')

    """ Documentation of Controls.xlsx workbook, to be written to the summary sheet.   
    """
    summary_textB1 = ('Reference Wiesel and Alfano,'
                      '"Optimal Many-Revolution Orbit Transfer"')
    summary_textA2 = ('Description: ')
    summary_textB3 = ('This workbook is generated by "GenerateControlTable.py". '
                      'The table include in worksheet "cv" is used to generate trajectories '
                      'of combined inclination and orbit raising for spacecraft flight software.')
    summary_textB4 = ('"ExportControls.py" is reads the "cv" table and exports it ' 
                      'as a JSON file.  "YawAngles.py" reads the JSON file and generates thrust '
                      'yaw commands.') 
    summary_textB5 = ('The orbit ratio is elaborated as a linear series from 1-to-10 ' 
                      'in intervals of 0.01. These values are written to the first column, '
                      'rows 2 to 902 in sheets "costate", and "cv".')
    summary_textB6 = ('The control variable cv is elaborated as a linear series '
                      'in 0.001 steps from 0.1000 to 0.9995. These values are '
                      'written  to the first row, columns 1 - 1471 of sheet "costate".')
    summary_textB7 = ('Sheet "costate" contains values of lambda ordered by rows of orbit ratio '
                      'and columns of cv. Lambda is computed using Phi(cv). '
                      'Successive values of lambda are proportional to the first row values '
                      'by the inverse square root of orbit ratio. '
                      'Only the first row values are independent.')
    summary_textB8 = ('Knowing the orbit ratio, and given a value of lambda, the costate table '
                      'is searched in successive rows for value less than or equal to the given lambda.')
    summary_textB9 = ('Sheet "cv" contains columns of cv by rows of orbit ratio and columns of lambda. '
                      'The columns are formed by searching along the rows of sheet "costate" for '
                      'each value of lambda, and identifying each cv value in the same column as found. '
                      'Sheet "cv" represents the Alfano Inverse Phi function. ')
    summary_textB10 = ('The current resolution of 901 x 1470 has been chosen based upon the '
                       'precision required in lambda to achieve a geosynchronous ' 
                       'orbit ratio 6.13 and 28.5 degree inclination change with less than 0.01 '
                       'error in eccentricity.')
    summary_textB11 = ('Sheet "transfers" contains the values of inclination change by rows of '
                       'orbit ratio and columns of lambda. This sheet maps direction to the columns '
                       'of the "cv" sheet.')
    summary_textB12 = ('Text file of cv by rows of Orbit Ratio by columns of Lambda is written out '
                       'in JSON format at conclusion.')


    """ Write out the documentation """    
    summarySht.set_column('A:A',12)
    summarySht.set_column('B:B',76)
    
    summarySht.write_string('B1', summary_textB1, cell_format1)
    summarySht.write_string('A2', summary_textA2, cell_format1)
    summarySht.write_string('B3', summary_textB3, cell_format1)
    summarySht.write_string('B4', summary_textB4, cell_format1)
    summarySht.write_string('B5', summary_textB5, cell_format1)
    summarySht.write_string('B6', summary_textB6, cell_format1)
    summarySht.write_string('B7', summary_textB7, cell_format1)
    summarySht.write_string('B8', summary_textB8, cell_format1)
    summarySht.write_string('B9', summary_textB9, cell_format1)
    summarySht.write_string('B10', summary_textB10, cell_format1)
    summarySht.write_string('B11', summary_textB11, cell_format1)
    summarySht.write_string('B12', summary_textB12, cell_format1)
    

    wb.define_name('cv','cv!$A$1:$BDO${0}'.format(alf.nrows+1))
    wb.define_name('costates','costate!$A$1:$BDO${0}'.format(alf.nrows+1))

    costates = np.zeros((alf.nrows, alf.ncols))
    """ This stores the 901 x 1471 element range of lambda. """
                
    costateSht.write_string('A1', 'Lambda = f(R,U)', cell_bold)
    costateSht.write_row('B1', alf.u, cell_bold)
    costateSht.write_column('A2', alf.a, cell_bold)
    
    row=0
    mu = 1
    for R in alf.a:
        """ R is the current orbit ratio """
        col=0
        
        L = np.round((mu/np.sqrt(R)) * alf.Lambda, 4)
        """ Compute each row of lambda as a linear combination of the first row. """

        costateSht.write_row(row + 1, col + 1, L)
        
        costates[row] = L
        
        print('Lambda costates calculated for orbit ratio {0}'.format(R))
        
        for lamb in alf.Lambda:
            """ Collect the set of u that is mapped to this costate, each element
            is an instance of u for a particular orbit ratio.  
            There are two tricks to this algorithm:
            (1) Each row of costates is the first row multiplied by a factor.
            Those values appearing in the first row are canonical. It is only
            necessary to search for the costate values that appear in the first row.
            (2) Costate values in rows decrease (become more negative) from left
            to right.
            Lambda and costate are synonyms, Lambda refers to the solution to the 
            Lagrangian multiplier for the constraint on the boundary value problem.
            Control specialists refer to these as costates.
            """
            isfound = np.where(costates[row] <= lamb)
            
            if np.size(isfound[0], 0) > 0:
                """ Values of lambda do not exist in all rows. """
                
                found_index = isfound[0][0]
                """ np.where returns an array with sequence in elemnt [0]
                in which sequence the index of the location is in element [0]
                """
                l_found = costates[row][found_index]
                
                if lamb == l_found:
                    alf.UbyRbyL[lamb][row] = alf.u[found_index]
                else:
                    l_lo = costates[row][found_index]
                    l_hi = costates[row][found_index - 1]
                    u_hi = alf.u[found_index]
                    u_lo = alf.u[found_index - 1]
                    
                    alf.UbyRbyL[lamb][row] = np.round(alf.lin_interp(l_hi, l_lo, lamb, u_lo, u_hi), 4)
            else:
                logging.warning("Costate Table row %d stops at lambda value = %d.", row, lamb)
                break
                
            col += 1
        row += 1

    msg = 'Completed Calculation of lambda costates. Rows: {0}, Columns: {1}.'.format(row, col)
    logging.info(msg)
    
    trajSht.write_string('A1', 'cv = f(R,Lambda)', cell_bold)
    trajSht.write_row('B1', alf.Lambda, cell_bold)
    trajSht.write_column('A2', alf.a, cell_bold)
    
    iaSht.write_string('A1', 'di/da = f(R, U)', cell_bold)
    iaSht.write_row('B1', alf.Lambda, cell_bold)
    iaSht.write_column('A2', alf.a, cell_bold)

    xferSht.write_row('B1', alf.Lambda, cell_bold)
    xferSht.write_column('A2', alf.a, cell_bold)

    col = 0  
    for lamb in alf.UbyRbyL:
        """ Write out the 'cv' worksheet.  This is essentially the Alfano Inverse Phi().
        The costate value and orbit ratio are the domain, u as the range. 
        This function is formed by writing out the UbyRbyL dictionary as rows and columns.
    
        The deprecated excel macro is preserved here:
        '=INDEX(cv!$A$1:$SF$500,MATCH($D2,'orbit R'!$A:$A,1),MATCH(E$1,INDIRECT(CONCAT("costate!",$A2,":",$A2)),-1))'
        
        ExportControls.py will read in then write this sheet out as a JSON file.
        """     
        
        UforL = alf.UbyRbyL[lamb]
        """ UforL an array of u. """
        
        try:
            delta_i = altitude(alf.a, UforL)
            
        except Exception as e:
            lines = traceback.format_exc().splitlines()
            
            logging.error("Exception: %s, %s, %s\n%s\n%s", e.__class__, e.__doc__, e.__cause__, lines[0], lines[-1])
            print("Error calculating altitude change: {0}. Continuing.".format(e.__doc__))
            

        """ From the U by R by L data, calculate the incl change for each value of cv 
        by columns of costate and rows of R.  Write to workbook.
        Equation 23 of "Simulating and Alfano Transfer with GMAT is used. 
        """
        
        trajSht.write_column(1, col + 1, UforL)
        iaSht.write_column(1, col + 1, delta_i)
        
        msg ="Writing U column vector for costate {0}".format(lamb)
        print(msg)
        logging.debug(msg)
           
        col += 1

    col = 0

    print('Please be patient, creating dida worksheet - change of inclination with R for each lambda, requires minutes.')

    for cv in alf.u:
        """ Fill in altitude summation formula """
        row = 0
        for R in alf.a:
            #xferSht.write_formula('=SUM(dida!${0}2:{0}:{1}'.format(row + 1, col + 1))
            start_cell = xlut.xl_rowcol_to_cell(2, col + 1)
            sum_cell = xlut.xl_rowcol_to_cell(row + 1, col + 1)
            xferSht.write_formula(sum_cell,'=SUM(dida!${0}:{1})'.format(start_cell, sum_cell))
            
            row +=1
        col+=1

    msg = 'Completed computation of Alfano Phi() for all costates in Lambda. {0} column vectors.).'.format(col)
    logging.info(msg)
    print(msg)

    jfile = QFileDialog().getSaveFileName(None, 
                       'Select JSON Control File for Output.', 
                       os.getenv('USERPROFILE'),
                       filter='Text files(*.json)')

    # AlfanoLib Issue 02212022-001, Bad Default Path in YawAngles
    sharedfname = Path.cwd() / Path('SavedJsonPath')

    try:
        with open(sharedfname, 'w+') as fd:
            """ Filename 'SavedJsonPath' located in CWD constitutes an interface agreement with YawAngles.py."""
            rval = fd.write(jfile[0])

        logging.info('{0} contains controls filename {1}'.format(sharedfname, jfile[0]))

    except OSError as e:
        logging.exception('SaveJsonPath could not be opened for writing.\n{0}'.format(__doc__))
        print('SaveJsonPath could not be opened for writing {0}.'.format(jfile[0]))
    
    export_controls(alf.UbyRbyL, jfile[0])

    """
    TODO: Recreate the Alfano nomograph, figure 6-4 in Vallado. Plot the costate
    value and delta-v as function of orbit ratio and inclination change.  Requires
    rotating the cv axis into the inclination axis, likewise into the delta-V axis.
    """
    
    print("Cleaning up and writing files.")
    wb.close()
        