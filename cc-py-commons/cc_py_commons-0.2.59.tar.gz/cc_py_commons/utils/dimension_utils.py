
def kg_to_lbs(weight_in_kg):
	weight_in_lbs = None
	if weight_in_kg:
		weight_in_lbs = round(weight_in_kg * 2.2046, 2)
	return weight_in_lbs

def inch_to_ft(length_in_inch):
	length_in_ft = None
	if length_in_inch:
		length_in_ft = round(length_in_inch * 0.0833, 2)
	return length_in_ft

def centimeter_to_ft(length_in_cm):
	length_in_ft = None
	if length_in_cm:
		length_in_ft = round(length_in_cm * 0.032808, 2)
	return length_in_ft

def meter_to_ft(length_in_m):
	length_in_ft = None
	if length_in_m:
		length_in_ft = round(length_in_m * 3.28084, 2)
	return length_in_ft
