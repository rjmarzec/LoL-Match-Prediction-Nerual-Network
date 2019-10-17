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

def increment_current_match_row():
	global current_match_row

	time.sleep(1)
	sheet.update_acell('Q1', int(sheet.acell('Q1').value) + 1)
	time.sleep(1)
	current_match_row = current_match_row + 1

def get_current_match_row():
	time.sleep(1)
	return int(sheet.acell('Q1').value)

def format_current_match_data(match_data):
	output_string = ''

	# match start time
	output_string += str(match_data['gameCreation']) + ','

	# team and role of each player in order
	match_participants = match_data['participants']
	for participant in match_participants:
		output_string += str(participant['teamId']) + ','

		if participant['timeline']['role'] == 'SOLO' and participant['timeline']['lane'] == 'TOP':
			output_string += '1,'
		elif participant['timeline']['role'] == 'NONE' and participant['timeline']['lane'] == 'JUNGLE':
			output_string += '2,'
		elif participant['timeline']['role'] == 'SOLO' and participant['timeline']['lane'] == 'MIDDLE':
			output_string += '3,'
		elif participant['timeline']['role'] == 'DUO_CARRY' and participant['timeline']['lane'] == 'BOTTOM':
			output_string += '4,'
		elif participant['timeline']['role'] == 'DUO_SUPPORT' and participant['timeline']['lane'] == 'BOTTOM':
			output_string += '5,'
		else:
			output_string += '0,'

	return output_string

def format_previous_match_data(match_data, players_id_in_match, found_match):
	output_string = ''
	if found_match:
		player_data = match_data['participants'][players_id_in_match - 1]	

		# general inforamtion about the game
		output_string += str(match_data['gameCreation']) + ','
		output_string += str(match_data['gameDuration']) + ','
		output_string += str(match_data['queueId']) + ','
		output_string += str(match_data['mapId']) + ','

		# whether or not the player won the game and their champion
		output_string += '1,' if player_data['stats']['win'] == 'true' else '0,'
		output_string += str(player_data['championId']) + ','

		# player stats
		output_string += str(player_data['stats']['kills']) + ','
		output_string += str(player_data['stats']['deaths']) + ','
		output_string += str(player_data['stats']['assists']) + ','
		output_string += str(player_data['stats']['largestKillingSpree']) + ','
		output_string += str(player_data['stats']['largestMultiKill']) + ','
		output_string += str(player_data['stats']['killingSprees']) + ','
		output_string += str(player_data['stats']['longestTimeSpentLiving']) + ','
		output_string += str(player_data['stats']['totalDamageDealt']) + ','
		output_string += str(player_data['stats']['totalDamageDealtToChampions']) + ','
		output_string += str(player_data['stats']['totalHeal']) + ','
		output_string += str(player_data['stats']['damageSelfMitigated']) + ','
		output_string += str(player_data['stats']['damageDealtToObjectives']) + ','
		output_string += str(player_data['stats']['visionScore']) + ','
		output_string += str(player_data['stats']['totalDamageTaken']) + ','
		output_string += str(player_data['stats']['goldEarned']) + ','
		output_string += str(player_data['stats']['totalMinionsKilled']) + ','
		output_string += str(player_data['stats']['neutralMinionsKilled']) + ','
		output_string += str(player_data['stats']['totalTimeCrowdControlDealt']) + ','
		output_string += str(player_data['stats']['champLevel']) + ','

		'''
		# since not all matches will have deltas or the same number of deltas, they will be exlcuded to avoid potential issues
		# player's 'timeline' stats
		output_string += str(player_data['timeline']['creepsPerMinDeltas']['0-10']) + ','
		output_string += str(player_data['timeline']['xpPerMinDeltas']['0-10']) + ','
		output_string += str(player_data['timeline']['goldPerMinDeltas']['0-10']) + ','
		output_string += str(player_data['timeline']['damageTakenPerMinDeltas']['0-10']) + ','
		'''
	else:
		# fills in 0 for all 25 datapoints if the player's previous match was not very recent
		for i in range(0, 25):
			output_string += '0,'

	return output_string

def format_ranked_stats_data(input_stats_data):
	output_string = ''

	try:
		# for some reason, the input data comes in as a list with the dict we want as a single entry?
		stats_data = input_stats_data[0]

		tier_dict = {'IRON': '1', 'BRONZE': '2', 'SILVER': '3', 'GOLD': '4', 'PLATINUM': '5', 'DIAMOND': '6'}
		if str(stats_data['tier']) in tier_dict:
			output_string += tier_dict[str(stats_data['tier'])] + ','
		else:
			output_string += '0,'

		rank_dict = {'I': '1', 'II': '2', 'III': '3', 'IV': '4'}
		if str(stats_data['rank']) in rank_dict:
			output_string += rank_dict[str(stats_data['rank'])] + ','
		else:
			output_string += '0,'

		output_string += str(stats_data['leaguePoints']) + ','
		output_string += str(stats_data['wins']) + ','
		output_string += str(stats_data['losses']) + ','
		output_string += '0, ' if stats_data['veteran'] == 'False' else '1,'
		output_string += '0, ' if stats_data['inactive'] == 'False' else '1,'
		output_string += '0, ' if stats_data['freshBlood'] == 'False' else '1,'
		output_string += '0, ' if stats_data['hotStreak'] == 'False' else '1,'
	except:
		print('\tError occured when handling a player\'s ranked stats. Logging all 0s and continuing...')
		output_string = ''
		for i in range(0, 9):
			output_string += '0,'
	return output_string

def log_formatted_data(formatted_data):
	global current_match_row
	sheet.update_cell(current_match_row, 17, formatted_data)

	# Remove old matches after we have processed their info
	if current_match_row > 52:
		sheet.update_cell(current_match_row, 3, 'Match data removed from sheet to prevent data overload issues.')

	# Delay to ensure that API rates are not passed.
	print('\tDelaying before next match...')
	time.sleep(25)

sheet = get_sheet()
watcher = get_riot_watcher()
current_match_row = get_current_match_row()

unexpected_api_error_occured = False

print('Starting...')
if(current_match_row <= 2):
	current_match_row = 3
while current_match_row <= 2002 and not unexpected_api_error_occured:
	print('Current Match Row: ' + str(current_match_row))

	# Check the stored match id. If it is 0, it played before patch 9.4, and it should be ignored.
	current_match_id = sheet.cell(current_match_row, 1).value
	if current_match_id != '0':
		formatted_output = ''
		current_match_start_time = sheet.cell(current_match_row, 4).value

		current_match_player_list = sheet.range(current_match_row, 5, current_match_row, 14)

		# Store everything important from the current match
		formatted_output += format_current_match_data(watcher.match.by_id('na1', current_match_id))

		for player_counter in range(0, 10):
			players_account_id = current_match_player_list[player_counter].value

			try:
				# Get the match that the player has played before the stored ranked match
				players_previous_match_from_matchlist = watcher.match.matchlist_by_account(region='na1', encrypted_account_id=players_account_id, queue=None, end_time=current_match_start_time, begin_time=str(int(current_match_start_time) - 604800000))['matches'][0]

				players_previous_match = watcher.match.by_id(region='na1', match_id=players_previous_match_from_matchlist['gameId'])

				# Find what their id is relative to that match and get their summoner ID
				players_summoner_id = None
				players_id_in_match = None
				for participantIdentity in players_previous_match['participantIdentities']:
					if participantIdentity['player']['accountId'] == players_account_id:
						players_summoner_id = participantIdentity['player']['summonerId']
						players_id_in_match = participantIdentity['participantId']
						break

				# Log that previous match information given the above
				formatted_output += format_previous_match_data(players_previous_match, players_id_in_match, True)

			except ApiError as err:
				if err.response.status_code == 404:
					# API Error code 404: no matches found within the time frame
					print('\t404 error from finding a previous match. Logging all 0s for it...')
					formatted_output += format_previous_match_data(False, False, False)
				else:
					unexpected_api_error_occured = True
					#print('Error! Write in a case for handling a RiotWatcher 404 error (match not found given parameters) and others here')
					print('Unexpected API error occured! Stopping script. Please find a way to get around this case.')
					print('Error Status Code: ' + str(err.response.status_code))
					break

			# Find and log their specific ranked information. This will return ranked information from multiple queues, so only take the one for 
			players_ranked_information = watcher.league.positions_by_summoner(region='na1', encrypted_summoner_id=players_summoner_id)
			
			formatted_output += format_ranked_stats_data(players_ranked_information)

			'''
			# Test Print statements to both see if requesting API information is good and to see the formatting of said data
			print(players_previous_match_from_matchlist)
			print('@@@@@@@@@@')
			print(players_previous_match)
			print('##########')
			print(players_ranked_information)
			print('**********')
			print(participantIdentity)
			print(players_id_in_match)
			'''

		if not unexpected_api_error_occured:
			# Log the formatted data in the spreadsheet, and increment the row counter.
			log_formatted_data(formatted_output.strip(','))
			increment_current_match_row()
	else:
		print('\tMatch played on a patch other than 9.4. Moving to next match.')
		increment_current_match_row()
