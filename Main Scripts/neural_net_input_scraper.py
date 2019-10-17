import gspread
from oauth2client.service_account import ServiceAccountCredentials

def get_sheet():
	# GSpread Setup
	scope = ['https://spreadsheets.google.com/feeds',
		 'https://www.googleapis.com/auth/drive']
	credentials = ServiceAccountCredentials.from_json_keyfile_name('[REDACTED]', scope)
	gc = gspread.authorize(credentials)
	return gc.open_by_key('[REDACTED]').sheet1

sheet = get_sheet()

match_ids = sheet.range(3, 1, 502, 1)
input_label_list_from_sheet = sheet.range(3, 2, 502, 2)
input_data_list_from_sheet = sheet.range(3, 17, 502, 17)

input_label_list = []
input_data_list = []
for i in range(500):
	if match_ids[i] != 0:
		input_label_list.append('0' if input_label_list_from_sheet[i].value == 'Red' else '1')
		
		input_data_list.append(input_data_list_from_sheet[i].value.split(','))
	print(i)

# repl.it doesn't like to *actually* save to the file, so this is pointless unless run outside of this environment
input_labels_doc = open('input_labels.txt', 'w')
input_labels_doc.write(str(input_label_list))
input_labels_doc.close()

input_data_doc = open('input_data.txt', 'w')
input_data_doc.write(str(input_data_list))
input_data_doc.close()
