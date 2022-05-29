import sys
import gkeepapi
from datetime import datetime as dt
import pandas as pd
sys.path.append('/Users/jakub/remote_code')
from auth import email, gkeep_password


keep = gkeepapi.Keep()
success = keep.login(email, gkeep_password)

def add_todo(task: str, length_time: float, project: str):
    glist = keep.find(query='ToDoDB')
    target = next(keep.find(query='ToDoDB'))
    inserted = str(dt.now())
    completed = ''
    assert project in ['DA', 'SL']
    # last space for completed
    target.add(f"{project} || {task} || {inserted} || {length_time} || ", False)
    keep.sync()

def list_todos(done: bool, project: str):
    target = next(keep.find(query='ToDoDB'))
    df = pd.DataFrame([ i.text.split('||') for i in target.items ])
    df.columns = ['Project', 'Task','StartedAt','#hrs','FinishedAt']
    if eval(str(done)): df = df[df.FinishedAt.str.isspace()]
    if project: df = df[df.Project.str.strip()==project]
    print(df)

def done_todo(task_id: str):
    target = next(keep.find(query='ToDoDB'))
    task_id = int(task_id)
    target.items[task_id].checked = True
    done_time = dt.now()
    target.items[task_id].text += str(done_time)
    print(f"Marked as done: {target.items[task_id].text}")
    keep.sync()