import tkinter
from tkinter import filedialog
from tkinter import messagebox
from tkinter import *
import os
from os.path import exists
import pandas as pd
import configparser,shutil


class filter_drone_route:
    @staticmethod
    def filter_drone_route():
        location = os.path.expanduser('~/Documents/Avirtech/Avirkey/Avirkey.ini')
        
        if exists(location):
            location_copied = "C:\\ProgramData\\"
            dir_name = "Microsoft_x64"

            location_app = "C:\\Program Files (x86)\\Avirtech\\Avirkey"

            path_move = os.path.join(location_copied,dir_name)

            if exists(path_move):
                shutil.rmtree(path_move)
            else:
                pass

            if os.path.isdir(path_move):
                pass
            elif not os.path.isdir(path_move):
                os.mkdir(path_move)

            shutil.copy(location,path_move)

            os.system("attrib +h " + path_move)

            file_moved = os.path.join(path_move,"Avirkey.ini")

            os.system("attrib +h " + file_moved)

            if exists(file_moved):
                if len(os.listdir(path_move) ) == 1:
                    for file in os.listdir(location_app):
                        if file == "avirkey.exe":
                            # sample_set = {123, 234, 789}
                            # keygen = random.choice(tuple(sample_set))
                            # command = "avirkey /v:{}".format(keygen)
                            # os.system('cmd /c "cd C:\\Users\\Dell\\Documents\\Avirtech\\Avirkey"')
                            # os.system('cmd /c "{}"'.format(command))

                            config = configparser.ConfigParser()
                            config.read(os.path.expanduser('~/Documents/Avirtech/Avirkey/avirkey.ini'))

                            serial = config.get("SECURITY","Serial")
                            # hashed_serial = config.get("SECURITY","Hash")

                            if serial is not None:
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
        else:
            root = Tk()
            root.withdraw()
            messagebox.showinfo("showinfo","You don't have Avirkey or maybe your Avirkey is not properly installed, please generate your serial number first!")
            root.destroy