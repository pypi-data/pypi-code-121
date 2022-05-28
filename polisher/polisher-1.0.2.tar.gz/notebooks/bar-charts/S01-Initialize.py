"""
# bar-charts

This notebook will use the library polisher demonstrate how you can clean
your plot by removing clutter.

It is important to say that the concept of cleaning up the graphs is explained
in detail in the [book](https://www.kobo.com/us/en/ebook/storytelling-with-data)
Storytelling with Data by Cole Nussbaumer Knaflic. Thus, I am not going to go
over in great detail why this is being done.
"""
import cauldron as cd
import pandas as pd

cd.display.markdown(__doc__)

report_data = [
    {'name': 'Time Sheets', 'exported': 394},
    {'name': 'Schedules', 'exported': 171},
    {'name': 'overtime', 'exported': 457},
    {'name': 'Time-off', 'exported': 93},
    {'name': 'Shift Requests', 'exported': 30},
]

cd.shared.put(report_data=pd.DataFrame(report_data))
