import requests

client_id = 'ckl9ldbxaagizxfxdtgalaihot3qjj'
client_secret = '03ndx73zuf2qy434ybtwlaxsqpjwym'
streamer_name = 'sivygames'

body = {
    'client_id': client_id,
    'client_secret': client_secret,
    "grant_type": 'client_credentials'
}

authentication = requests.post('https://id.twitch.tv/oauth2/token', body)
keys = authentication.json()
headers = {
    'Client-ID': client_id,
    'Authorization': 'Bearer ' + keys['access_token']
}
print("Authentication api: ", keys)

get_stream_info = requests.get('https://api.twitch.tv/helix/streams?user_login=' + streamer_name, headers=headers)
stream_info = get_stream_info.json()
print("Stream info: ", stream_info)

if len(stream_info['data']) == 1:
    print(streamer_name + ' is live: ' + stream_info['data'][0]['title'] + ' playing ' + stream_info['data'][0]['game_name'])
else:
    print(streamer_name + ' is not live')