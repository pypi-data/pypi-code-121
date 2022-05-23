"""
# clearskydays
# A simple Python module that determines clear sky days based on solar ultraviolet radiation measurements. 
"""

import pandas as pd
import numpy as np

def get_clear_sky_days(dataset, clearness=98):
	"""
	Returns clear sky days considering a clearness greater than or equal to 98% (by default). 
	In addition, the number of measurements (values) per day is determined to make a more precise selection
	according to the analyst's criteria. The days are selected under the condition that the extension
	of the data from the start of the measurements to the maximum value is at least 70% of the data measured
	after solar noon, and vice versa. 
	"""

	def get_clearness_percentage(date):
		"""
		Returns sky clearness (%), the number of measurements per day and data availability. 
		"""
		date = date.replace(0, np.nan)
		date = date.dropna(how='all', axis=0)
		max_value = np.argmax(date)
		part1 = date[date.index[0]: date.index[max_value]]
		part2 = date[date.index[max_value]: ]
		diff1 = part1.diff() >= 0
		diff2 = part2.diff() <= 0
		series1 = diff1.sum() + diff2.sum() + 2
		series2 = part1.size + part2.size
		percentage = (series1 / series2) * 100
		return percentage, series2, check_size(part1, part2)

	def get_daily_clearness(dataset):
		"""
		Returns a dataframe containing daily sky clearness (%), the number of measurements (values) per day
		and data availability.  
		"""
		data = []
		date_list = []
		clearness_list = []
		measurements_list = []
		data_availability_list = []
		m = dataset.resample('D').max()
		for date in m.index:
			date = str(date.date())
			try:
				day = (date, get_clearness_percentage(dataset.loc[date])[0], 
						get_clearness_percentage(dataset.loc[date])[1],
						get_clearness_percentage(dataset.loc[date])[2])
				data.append(day)
			except ValueError:
				pass
		for date, clearness, number_measurements, data_availability in data:
			date_list.append(date)
			clearness_list.append(clearness)
			measurements_list.append(number_measurements)
			data_availability_list.append(data_availability)
		daily_clearness = pd.DataFrame(data, columns=['date', 'clearness', 'values', 'data_availability'])
		daily_clearness['date'] = pd.to_datetime(daily_clearness['date'], format='%Y-%m-%d')
		return daily_clearness

	def check_size(part1, part2):
		"""
		Returns True if the extent of the data from the start of the measurements to the maximum value 
		is at least 70% of the data measured after solar noon, and vice versa.
		"""
		if (part1.size >= 0.7 * part2.size) and (part2.size >= 0.7 * part1.size):
			return True
		else:
			return False

	daily_clearness_df = get_daily_clearness(dataset)
	clear_sky_days_df = daily_clearness_df.loc[(daily_clearness_df['clearness'] >= clearness) & (daily_clearness_df['data_availability']==True)]
	clear_sky_days_df = clear_sky_days_df[['date', 'clearness', 'values']]

	return clear_sky_days_df

