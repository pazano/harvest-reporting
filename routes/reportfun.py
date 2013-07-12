import datetime

def billablePercentage(billable, nonbill, exception, pto):
	billable = float(billable)
	nonbill = float(nonbill)
	exception = float(exception)
	pto = float(pto)
	if pto >= 40:
		return  "N/A"
	else:
		return  "{0:.0f}%".format((billable / (40-pto))*100)

def productivityPercentage(billable, nonbill, exception, pto):
	billable = float(billable)
	nonbill = float(nonbill)
	exception = float(exception)
	pto = float(pto)
	if pto >= 40:
		return "N/A"
	else:		
		productivity = ((billable + exception) / (40-pto))*100
		return "{0:.0f}%".format(productivity)

def datetimeInt(date):
	# assumes the input is a datetime.date
	date = str(date).split('-')
	date = date[0] + date[1] + date[2]
	return int(date)

def intDatetime(date):
	# assumes the input is an eight-digit int, YYYYMMDD
	date = str(date)
	year = int(date[:4])
	month = int(date[4:6])
	day = int(date[6:8])
	return datetime.date(year, month, day)