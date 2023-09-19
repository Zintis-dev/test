import requests
import json
import datetime
import time
import yaml

from datetime import datetime
print('Asteroid processing service')

# Initiating and reading config values
print('Loading configuration from file')

# 
nasa_api_key = "eW2lamWLrciRFgUL8h6qJeMM8OytxMlyyoYOtTTQ"
nasa_api_url = "https://api.nasa.gov/neo/"

# Getting todays date
dt = datetime.now()
request_date = str(dt.year) + "-" + str(dt.month).zfill(2) + "-" + str(dt.day).zfill(2)  
print("Generated today's date: " + str(request_date))


print("Request url: " + str(nasa_api_url + "rest/v1/feed?start_date=" + request_date + "&end_date=" + request_date + "&api_key=" + nasa_api_key))
#Makes request to NASA API using needed parameters
r = requests.get(nasa_api_url + "rest/v1/feed?start_date=" + request_date + "&end_date=" + request_date + "&api_key=" + nasa_api_key)

print("Response status code: " + str(r.status_code))
print("Response headers: " + str(r.headers))
print("Response content: " + str(r.text))

#Checks if request is successful
if r.status_code == 200:
	#Loads data into json from nasa api
	json_data = json.loads(r.text)

	ast_safe = []
	ast_hazardous = []

	#Checks if json document contains element count
	if 'element_count' in json_data:
		#gets astreroid count and parses  from string to integer
		ast_count = int(json_data['element_count'])
		print("Asteroid count today: " + str(ast_count))
	
		if ast_count > 0:
			#loops trough near earth objects at requested date
			for val in json_data['near_earth_objects'][request_date]:
				#checks if a  specific asteroid is in json
				if 'name' and 'nasa_jpl_url' and 'estimated_diameter' and 'is_potentially_hazardous_asteroid' and 'close_approach_data' in val:
					tmp_ast_name = val['name']
					tmp_ast_nasa_jpl_url = val['nasa_jpl_url']
					#checks if asteroid diameter calculation is aviable in kilometers
					if 'kilometers' in val['estimated_diameter']:
						#checks if diameter max and min values are aviable in val
						if 'estimated_diameter_min' and 'estimated_diameter_max' in val['estimated_diameter']['kilometers']:
							tmp_ast_diam_min = round(val['estimated_diameter']['kilometers']['estimated_diameter_min'], 3)
							tmp_ast_diam_max = round(val['estimated_diameter']['kilometers']['estimated_diameter_max'], 3)
						#if values are not aviable,  sets variables to -2
						else:
							tmp_ast_diam_min = -2
							tmp_ast_diam_max = -2
					#set variables to -1 if diameter is not aviable in kilometers
					else:
						tmp_ast_diam_min = -1
						tmp_ast_diam_max = -1

					tmp_ast_hazardous = val['is_potentially_hazardous_asteroid']
					
					#chekcs if any asteroids are approaching earth
					if len(val['close_approach_data']) > 0:
						#checks if any asteroids are approaching earth at a specific date, has relative velocity, has close miss distance
						if 'epoch_date_close_approach' and 'relative_velocity' and 'miss_distance' in val['close_approach_data'][0]:
							tmp_ast_close_appr_ts = int(val['close_approach_data'][0]['epoch_date_close_approach']/1000)
							tmp_ast_close_appr_dt_utc = datetime.utcfromtimestamp(tmp_ast_close_appr_ts).strftime('%Y-%m-%d %H:%M:%S')
							tmp_ast_close_appr_dt = datetime.fromtimestamp(tmp_ast_close_appr_ts).strftime('%Y-%m-%d %H:%M:%S')
							#chekcs if ateroid approaching speed is aviable in kilometers per hour
							if 'kilometers_per_hour' in val['close_approach_data'][0]['relative_velocity']:
								tmp_ast_speed = int(float(val['close_approach_data'][0]['relative_velocity']['kilometers_per_hour']))
							else:
								tmp_ast_speed = -1
							#checks if miss distance is aviable in kilometers
							if 'kilometers' in val['close_approach_data'][0]['miss_distance']:
								tmp_ast_miss_dist = round(float(val['close_approach_data'][0]['miss_distance']['kilometers']), 3)
							else:
								tmp_ast_miss_dist = -1
						#if any asteroids are not close to earth, sets variables to fixed date
						else:
							tmp_ast_close_appr_ts = -1
							tmp_ast_close_appr_dt_utc = "1969-12-31 23:59:59"
							tmp_ast_close_appr_dt = "1969-12-31 23:59:59"
					#if no asteroids are approaching earth, prints information accordingly
					else:
						print("No close approach data in message")
						tmp_ast_close_appr_ts = 0
						tmp_ast_close_appr_dt_utc = "1970-01-01 00:00:00"
						tmp_ast_close_appr_dt = "1970-01-01 00:00:00"
						tmp_ast_speed = -1
						tmp_ast_miss_dist = -1

					#prints information about asteroids
					print("------------------------------------------------------- >>")
					print("Asteroid name: " + str(tmp_ast_name) + " | INFO: " + str(tmp_ast_nasa_jpl_url) + " | Diameter: " + str(tmp_ast_diam_min) + " - " + str(tmp_ast_diam_max) + " km | Hazardous: " + str(tmp_ast_hazardous))
					print("Close approach TS: " + str(tmp_ast_close_appr_ts) + " | Date/time UTC TZ: " + str(tmp_ast_close_appr_dt_utc) + " | Local TZ: " + str(tmp_ast_close_appr_dt))
					print("Speed: " + str(tmp_ast_speed) + " km/h" + " | MISS distance: " + str(tmp_ast_miss_dist) + " km")
					
					# Adding asteroid data to the corresponding array
					if tmp_ast_hazardous == True:
						ast_hazardous.append([tmp_ast_name, tmp_ast_nasa_jpl_url, tmp_ast_diam_min, tmp_ast_diam_max, tmp_ast_close_appr_ts, tmp_ast_close_appr_dt_utc, tmp_ast_close_appr_dt, tmp_ast_speed, tmp_ast_miss_dist])
					else:
						ast_safe.append([tmp_ast_name, tmp_ast_nasa_jpl_url, tmp_ast_diam_min, tmp_ast_diam_max, tmp_ast_close_appr_ts, tmp_ast_close_appr_dt_utc, tmp_ast_close_appr_dt, tmp_ast_speed, tmp_ast_miss_dist])

		else:
			print("No asteroids are going to hit earth today")

	print("Hazardous asteorids: " + str(len(ast_hazardous)) + " | Safe asteroids: " + str(len(ast_safe)))

	#checks if there are any hazardous asteroids
	if len(ast_hazardous) > 0:
		
		#sorts hazardous asteroids by date
		ast_hazardous.sort(key = lambda x: x[4], reverse=False)

		#prints information about hazardous asteroids
		print("Today's possible apocalypse (asteroid impact on earth) times:")
		for asteroid in ast_hazardous:
			print(str(asteroid[6]) + " " + str(asteroid[0]) + " " + " | more info: " + str(asteroid[1]))

		ast_hazardous.sort(key = lambda x: x[8], reverse=False)
		print("Closest passing distance is for: " + str(ast_hazardous[0][0]) + " at: " + str(int(ast_hazardous[0][8])) + " km | more info: " + str(ast_hazardous[0][1]))
	else:
		print("No asteroids close passing earth today")

#if request is unsuccessful prints infromation accordingly
else:
	print("Unable to get response from API. Response code: " + str(r.status_code) + " | content: " + str(r.text))
