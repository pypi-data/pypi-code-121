import mysql.connector
import schedule
import time
import tkinter
from tkinter import messagebox



def mysqlconnect():
    # To connect MySQL database
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password="24682468AN",
        db='hello',
    )

    #transfering data into archival
    begin = time.time()
    cur = conn.cursor()
    cur.execute("set sql_safe_updates=0")

    #insertion into archival
    print("data inserted into archival is")
    cur.execute("select * from main where MONTH(date)+1 = month(now())")
    x = cur.fetchall()
    if x!=[]:
        print(x)
        cur.execute("insert into Archival (id,name,regno,date) select * from main where MONTH(date)+1 = month(now())")

    #deletion in main table
    print("data removed from main table is")
    cur.execute("select * from Main where MONTH(date)+1 = month(now())")
    y = cur.fetchall()
    if y!=[] and x==y:
        print(y)
        cur.execute("delete from Main where MONTH(date)+1 = month(now())")

    if(x==y and x != []):
        root = tkinter.Tk()
        root.withdraw()
        messagebox.showinfo("Archival Transfer", "Succesfully transfered historic data from main table to archival table")

    #commit changes
    conn.commit()
    time.sleep(1)

    end = time.time()
    print(f"Total runtime of the program is {end - begin}")


    # To close the connection
    conn.close()


# Driver Code
if __name__ == "__main__":
    schedule.every(20).seconds.do(mysqlconnect)
    while True:
        schedule.run_pending()
        time.sleep(1)