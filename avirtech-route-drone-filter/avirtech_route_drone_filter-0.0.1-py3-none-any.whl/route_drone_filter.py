import tkinter
from tkinter import filedialog
from tkinter import messagebox
from tkinter import *
import os
import pandas as pd

class filter_drone_route:
    @staticmethod
    def filter_drone_route():
        root = Tk()
        root.withdraw()
        # file_selected = askopenfilename()
        # messagebox.showinfo("showinfo","Please input your Palm Tree Plot")
        # folder_plot = filedialog.askdirectory()
        messagebox.showinfo("showinfo","Please input Your Drone Route .bin file")
        folder_result = filedialog.askdirectory()
        messagebox.showinfo("showinfo","Please insert folder to store result")
        gdb_location = filedialog.askdirectory()

        root.destroy

        list_directory = ["merge_drone","last_result","geodatabase"]
        for dir in list_directory:
            path = os.path.join(gdb_location,dir)
            os.makedirs(path)

        merge_drone_loc = os.path.join(gdb_location,list_directory[0])
        # titik_sawit_loc = os.path.join(gdb_location,list_directory[1])
        last_result = os.path.join(gdb_location,list_directory[1])
        geodatabase_loc = os.path.join(gdb_location,list_directory[2])

        substring = ".log"
        substring_error = ".txt"
        for file in os.listdir(folder_result):
            if file.find(substring) != -1:
                base = os.path.splitext(file)[0]
                print("Processing " + base + "...")
                with open(os.path.join(folder_result,file),"r") as f:
                    gps_all = []
                    lines = f.readlines()
                    try:
                        for i in range(0,len(lines)-1,1):
                            if(lines[i].split(", ")[0]=="GPS"):
                                gps_all.append(lines[i])
                    except:
                        pass

                    gps_used = []

                    for i in range(0,len(gps_all)-1,1):
                        if int(gps_all[i].split(", ")[15]) == int(1):
                            gps_used.append(gps_all[i])
                    
                    longitude = []
                    latitude = []

                    for row in gps_used:
                        longitude.append(row.split(", ")[9])
                        latitude.append(row.split(", ")[8])
                    
                    dict = {"X":longitude, "Y":latitude}
                    df = pd.DataFrame(dict)
                    print("Generating " + base + " to csv")
                    df.to_csv(os.path.join(merge_drone_loc,base + ".csv"))
                    
            elif file.find(substring_error) != -1:
                base = os.path.splitext(file)[0]
                print("Processing " + base + "....")
                with open(os.path.join(folder_result,file),"r") as f:
                    gps_raw = []
                    lines = f.readlines()
                    for i in range(0,len(lines),1):
                        gps_raw.append(lines[i].split(" "))
                    
                    gps_used = []
                    for gs in gps_raw:
                        if gs.count("mavlink_gps2_raw_t") > 0:
                            gps_used.append(gs)
                    latitude = []
                    longitude = []
                    for r in gps_used:
                        lat_index = r.index('lat') + 1
                        lon_index = r.index('lon') + 1
                        latitude.append(r[lat_index])
                        longitude.append(r[lon_index])
                    latitude = [int(x) * 0.0000001 for x in latitude]
                    longitude = [int(x) * 0.0000001 for x in longitude]
                    dict = {"X":longitude, "Y":latitude}
                    df = pd.DataFrame(dict)
                    print("Generating " + base + " to csv")
                    df.to_csv(os.path.join(merge_drone_loc,base + ".csv"))
        file_csv_merge = []
        for file in os.listdir(merge_drone_loc):
            file_csv_merge.append(os.path.join(merge_drone_loc,file))

        print("All process done, generating merge file")
        df_merge = pd.concat(map(pd.read_csv,file_csv_merge),ignore_index=True)

        df_merge = df_merge[df_merge['X'] != 0]

        df_merge = df_merge[df_merge['X'] > 0]

        df_merge.to_csv(os.path.join(merge_drone_loc,"merge.csv"))

        merge_csv = os.path.join(merge_drone_loc,"merge.csv")
        print("Process Done")
