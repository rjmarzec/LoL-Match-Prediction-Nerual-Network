import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from riotwatcher import RiotWatcher, ApiError

def get_sheet():
	# GSpread Setup
	scope = ['https://spreadsheets.google.com/feeds',
		 'https://www.googleapis.com/auth/drive']
	credentials = ServiceAccountCredentials.from_json_keyfile_name('[REDACTED]', scope)
	gc = gspread.authorize(credentials)
	return gc.open_by_key('[REDACTED]').sheet1

def get_riot_watcher():
	# Riot Watcher Setup
	rg_api_key = '[REDACTED]'
	return RiotWatcher(rg_api_key)

def get_match_data(match_id):
	try:
		return watcher.match.by_id('na1', match_id)
	except ApiError as err:
		if err.response.status_code == 429:
			print('We should retry in {} seconds.'.format(err.headers['Retry-After']))
			print('this retry-after is handled by default by the RiotWatcher library')
			print('future requests wait until the retry-after time passes')
		elif err.response.status_code == 404:
			print('Summoner with that ridiculous name not found.')
		else:
			print('Some error with the watch API occurred. Error Code: ' + str(err))
			raise
		time.sleep(50)
		get_match_data(match_id)

def increment_current_match_row():
	global current_match_row

	time.sleep(1)
	sheet.update_acell('B1', int(sheet.acell('B1').value) + 1)
	time.sleep(1)
	current_match_row = int(sheet.acell('B1').value)

def get_current_match_row():
	time.sleep(1)
	return int(sheet.acell('B1').value)

def log_match_data(match):
	global current_match_row

	#Store the match ID
	time.sleep(1)
	sheet.update_cell(current_match_row, 1, str(match['gameId']))

	#Store the outcome of the match
	time.sleep(1)
	if match['teams'][0]['win'] == 'Win':
		sheet.update_cell(current_match_row, 2, str('Red'))
	else:
		sheet.update_cell(current_match_row, 2, str('Blue'))

	#Store the raw match data in case it is needed later
	time.sleep(1)
	sheet.update_cell(current_match_row, 3, str(match))

	#Store the starting time of the match
	time.sleep(1)
	sheet.update_cell(current_match_row, 4, match['gameCreation'])

	#Store all the ID's of all the players in the match
	time.sleep(10)
	for i in range (0, 10):
		sheet.update_cell(current_match_row, 5 + i, str(match['participantIdentities'][i]['player']['accountId']))

sheet = get_sheet()
watcher = get_riot_watcher()
current_match_row = get_current_match_row()

repeat_counter = 0
print('Starting...')

ignore_previous_match_id = False
while(current_match_row <= 2002):
	if(current_match_row <= 3):
		match = get_match_data(sheet.acell('D1').value)
		log_match_data(match)
		current_match_row = 4
		increment_current_match_row()
	else:
		print('Current Match Row: ' + str(current_match_row))

		player_counter = 0
		if not ignore_previous_match_id:
			previous_match_id = sheet.cell(current_match_row - 1, 1).value
		found_next_match = False

		for player_counter in range(0, 10):
			if not found_next_match:
				try:
					# Queue 420 = Ranked Solo
					matchlist = watcher.match.matchlist_by_account('na1', sheet.cell(current_match_row - 1, player_counter + 5).value, 420)

					for match in matchlist['matches']:
						if (int(match['gameId']) != int(previous_match_id)) and (not (str(match['gameId']) in sheet.col_values(1))):
							if ignore_previous_match_id:
								current_match_row = get_current_match_row()
							log_match_data(watcher.match.by_id('na1', match['gameId']))
							increment_current_match_row()
							found_next_match = True
							repeat_counter = 0
							break
				except ApiError as err:
					if err.response.status_code == 429:
						print('We should retry in {} seconds.'.format(err.headers['Retry-After']))
						print('this retry-after is handled by default by the RiotWatcher library')
						print('future requests wait until the retry-after time passes')
					elif err.response.status_code == 404:
						print('Matches of that queue not found for the player id \"' + str(sheet.cell(current_match_row - 1, player_counter + 5).value) + '\". Moving onto the next player.')
			else:
				break
		repeat_counter += 1

		if repeat_counter > 1:
			print('No suitable matches found from previous players. Attempting to find another match using previous match data.')
			
			ignore_previous_match_id = True
			current_match_row -= 10
