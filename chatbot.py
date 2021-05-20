"""
Required to use
https://dev.twitch.tv/console/apps
https://twitchapps.com/tmi/
https://dev.twitch.tv/console/extensions

Install modules
python 3.10+
pip install irc
pip install requests

Commands
python chatbot.py bot_username client_id access_token channel_name

python chatbot.py sivygames ckl9ldbxaagizxfxdtgalaihot3qjj oauth:wbhdr3s2p7yx4iqr768gf0zezseees #channel
"""

import irc.bot
import requests
import json

server = 'irc.chat.twitch.tv'
port = 6667
bot_username = 'sivygames'
access_token = 'oauth:wbhdr3s2p7yx4iqr768gf0zezseees'
channel_name = 'sivygames'
app_client_id = 'ckl9ldbxaagizxfxdtgalaihot3qjj'
app_client_secret = '5wb8e4qyxbqy9rz9sba8vqqalcoztt'

class TwitchBot(irc.bot.SingleServerIRCBot):
    def __init__(self, server, port, bot_username, access_token, channel_name):
        self.server = server
        self.port = port
        self.bot_username = bot_username
        self.access_token = access_token
        self.channel_name = channel_name
        self.app_client_id = app_client_id
        self.app_client_secret = app_client_secret

        self.chat_connection(server, port, bot_username, access_token, channel_name)
    
    def chat_connection(self, server, port, bot_username, access_token, channel_name):
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port, access_token)], bot_username, bot_username)
        print('Connected to ' + server + ' on port ' + str(port) + '...')

    def string_to_list(self, strings):
        return strings[0].split()

    def get_channel_id(self, app_client_id, app_client_secret):
        body = {
        'client_id': app_client_id,
        'client_secret': app_client_secret,
        "grant_type": 'client_credentials'
        }

        authentication = requests.post('https://id.twitch.tv/oauth2/token', body)
        keys = authentication.json()
        headers = {
            'Client-ID': app_client_id,
            'Authorization': 'Bearer ' + keys['access_token']
        }
        get_stream_info = requests.get('https://api.twitch.tv/helix/search/channels?query=' + channel_name, headers=headers)
        stream_info = get_stream_info.json()

        for channel in stream_info["data"]:
            if channel['broadcaster_login'] == self.channel_name:
                return channel['id']

    def on_welcome(self, connection, event):
        print(bot_username + ' joining in ' + self.channel_name)

        #You must request specific capabilities before you can use them
        connection.cap('REQ', ':twitch.tv/membership')
        connection.cap('REQ', ':twitch.tv/tags')
        connection.cap('REQ', ':twitch.tv/commands')
        connection.join(self.channel_name)

        print(bot_username + ' joined in ' + self.channel_name)
        connection.privmsg(event.target, bot_username + ' joined in ' + self.channel_name)

        self.chatMonitoration(connection, event)

    def chatMonitoration(self, connection, event):
        print(bot_username + ' is monitoring the chat')
        connection.privmsg(event.target, bot_username + ' is monitoring the chat')

        chatText = self.string_to_list(event.arguments)

        #If a chat message starts with an exclamation point, try to run it as a command
        print("searching for commands in text chat: ", chatText)
        command_indicator = '!'
        for text in chatText:
            if command_indicator in text:
                if text[0] == command_indicator:
                    self.do_command(event, text, app_client_id, app_client_secret)

    def do_command(self, event, command, app_client_id, app_client_secret):
        channel_id = self.get_channel_id(app_client_id, app_client_secret)
        
        print("command: ", command)
        match command:
            case "!game":
                url = 'https://api.twitch.tv/helix/channels/' + channel_id
                headers = {'Client-ID': self.client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
                r = requests.get(url, headers=headers).json()
                self.connection.privmsg(self.channel_name, r['display_name'] + ' is currently playing ' + r['game'])

            case "!title":
                url = 'https://api.twitch.tv/helix/channels/' + channel_id
                headers = {'Client-ID': self.client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
                r = requests.get(url, headers=headers).json()
                self.connection.privmsg(self.channel_name, r['display_name'] + ' channel title is currently ' + r['status'])

            case "!raffle":
                message = "This is an example bot, replace this text with your raffle text."
                self.connection.privmsg(self.channel_name, message)

            case "!schedule":
                message = "This is an example bot, replace this text with your schedule text."
                self.connection.privmsg(self.channel_name, message)

            case _:
                print(command + " is a invalid command, try again")

def main():
    """
    if bot_username and channel_name and access_token and app_client_id and app_client_secret:
        bot = TwitchBot(bot_username, channel_name, access_token, app_client_id, app_client_secret)
        bot.start()
    else: 
        print("Access information is invalid")
        sys.exit(1)
    """

    bot = TwitchBot(server, port, bot_username, access_token, channel_name)
    bot.start()

if __name__ == "__main__":
    main()
