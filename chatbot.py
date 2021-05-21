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
python chatbot.py server, port, bot_username, access_token, channel_name, app_client_id, app_client_secret
python chatbot.py irc.chat.twitch.tv 6667 sivygames oauth:wbhdr3s2p7yx4iqr768gf0zezseees #sivygames ckl9ldbxaagizxfxdtgalaihot3qjj 5wb8e4qyxbqy9rz9sba8vqqalcoztt
"""

import irc.bot
import json
from threading import Timer
import requests
from irc.bot import SingleServerIRCBot

server = 'irc.chat.twitch.tv'
port = 6667
bot_username = 'sivygames'
access_token = 'oauth:wbhdr3s2p7yx4iqr768gf0zezseees'
channel_name = '#sivygames'
app_client_id = 'ckl9ldbxaagizxfxdtgalaihot3qjj'
app_client_secret = '5wb8e4qyxbqy9rz9sba8vqqalcoztt'

class TwitchBot(SingleServerIRCBot):
    def __init__(self, server, port, bot_username, access_token, channel_name, app_client_id, app_client_secret):
        self.server = server
        self.port = port
        self.bot_username = bot_username
        self.access_token = access_token
        self.channel_name = channel_name
        self.app_client_id = app_client_id
        self.app_client_secret = app_client_secret
        self.chat_connection(server, port, bot_username, access_token)

    def string_to_list(self, strings):
        return strings[0].split()

    def remove_one_character_in_string(self, string, character, position):
        return ''.join(string.split(character, position))

    def send_message_timer(self, event, message):
        self.connection.privmsg(event.target, message)

    def resets(self, event):
        print("resets running!")
        self.connection.privmsg(event.target, "/emoteonlyoff")
    
    def chat_connection(self, server, port, bot_username, access_token):
        SingleServerIRCBot.__init__(self, [(server, port, access_token)], bot_username, bot_username)
        print('Connected to ' + server + ' on port ' + str(port) + '...')

    def get_channel_info(self, app_client_id, app_client_secret, channel_name_pure):
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
        get_stream_info = requests.get('https://api.twitch.tv/helix/search/channels?query=' + channel_name_pure, headers=headers)

        return get_stream_info.json()

    #https://discuss.dev.twitch.tv/t/how-to-get-info-about-rewards-api/27891
    def get_reward_info(self, app_client_id, app_client_secret, channel_name_pure):
        channel_points_list = ['channel-points-channel-v1.' + self.channel_id]
        body = {
            'client_id': app_client_id,
            'client_secret': app_client_secret,
            "grant_type": 'client_credentials',
            'type': 'LISTEN',
            'topics': channel_points_list,
            'scope': 'channel:read:redemptions'
        }

        authentication = requests.post('wss://pubsub-edge.twitch.tv', body)
        keys = authentication.json()
        headers = {
            'Client-ID': app_client_id,
            'Authorization': 'Bearer ' + keys['access_token']
        }
        
        get_channel_point_info = requests.get('https://api.twitch.tv/helix/search/channels?query=' + channel_name_pure, headers=headers)
        redeemed_at = get_channel_point_info['redeemed_at']
        reward_title = get_channel_point_info['reward']['title']
        cost = get_channel_point_info['reward']['cost']
        username = get_channel_point_info['redemption']['user']['display_name']
        message = get_channel_point_info['reward']['prompt']


    def get_channel_id(self, channel_name_pure):
        channel_info = self.get_channel_info(app_client_id, app_client_secret, channel_name_pure)
        for channel in channel_info["data"]:
            if channel['broadcaster_login'] == channel_name_pure:
                return channel['id']

    def get_channel_game_name(self, channel_name_pure):
        channel_info = self.get_channel_info(app_client_id, app_client_secret, channel_name_pure)
        for channel in channel_info["data"]:
            if channel['broadcaster_login'] == channel_name_pure:
                return channel['game_name']

    def get_channel_stream_title(self, channel_name_pure):
        channel_info = self.get_channel_info(app_client_id, app_client_secret, channel_name_pure)
        for channel in channel_info["data"]:
            if channel['broadcaster_login'] == channel_name_pure:
                return channel['title']

    def custom_reward_verifier(self, event):
        text = event.arguments[0]
        username = event.source.nick

        print("text " + text)
        if "resgatou 1000 moedas Pokemon" in text:
            print("moedas pokemon " + text)
            self.connection.privmsg(event.target, "!gold add" + username + '1')
            return True
        
        if "resgatou Hora do anúncio" in text:
            print("anuncio " + text)
            self.connection.privmsg(event.target, "!commercial 30")
            return True
        
        if "resgatou Chat somente emotes" in text:
            print("chat somente emotes " + text)
            seconds = 120 #2min
            self.connection.privmsg(event.target, "/emoteonly")

            Timer(seconds, self.send_message_timer(event, "/emoteonlyoff")).start()
            return True

        if "resgatou Suspenda alguém por 2 minutos" in text:
            print("suspenda alguem " + text)
            user_target = '' #user-notice-line chat-line--inline
            seconds = 120 #2min
            self.connection.privmsg(event.target, "/timeout" + user_target + str(seconds))
            return True

        if "resgatou VIP no canal por 24 horas" in text:
            print("vip 24 horas " + text)
            seconds = 86400 #24hs
            self.connection.privmsg(event.target, "/vip " + username)

            Timer(seconds, self.send_message_timer(event, "/unvip " + username)).start()
            return True

        if "resgatou Moderador por 24 horas" in text:
            print("mod 24 horas " + text)
            seconds = 86400 #24hs
            self.connection.privmsg(event.target, "/mod " + username)

            Timer(seconds, self.send_message_timer(event, "/unmod " + username)).start()
            return True

                        
    def command_verifier(self, event):
        #If a chat message starts with an exclamation point, try to run it as a command 
        chatText = self.string_to_list(event.arguments)
        print("searching for commands in chat: ", chatText)   
        command_indicator = '!'
        for text in chatText:
            if command_indicator in text:
                if text[0] == command_indicator:
                    self.do_command(event, text)
                    return True

    def on_welcome(self, connection, event):
        print(bot_username + ' joining in chat')

        #You must request specific capabilities before you can use them
        connection.cap('REQ', ':twitch.tv/membership')
        connection.cap('REQ', ':twitch.tv/tags')
        connection.cap('REQ', ':twitch.tv/commands')
        connection.join(self.channel_name)

        print(bot_username + ' joined in chat')
        connection.privmsg(event.target, bot_username + ' joined in chat')

        self.resets(event)

    def on_pubmsg(self, connection, event):
        if self.custom_reward_verifier(event) == False:
            self.command_verifier(event)

    def do_command(self, event, command):
        channel_name_pure = self.remove_one_character_in_string(channel_name,'#', 1)
        
        print("command: ", command)
        match command:
            case "!game":
                self.connection.privmsg(event.target, channel_name_pure + ' is currently playing: ' + self.get_channel_game_name(channel_name_pure))

            case "!title":
                self.connection.privmsg(event.target, channel_name_pure + ' channel title is currently: ' + self.get_channel_stream_title(channel_name_pure))

            case "!raffle":
                self.connection.privmsg(event.target, " this is an example bot, replace this text with your raffle text.")

            case _:
                self.connection.privmsg(event.target, " the command " + command + " is a invalid, try again")

def main():
    """
    if bot_username and channel_name and access_token and app_client_id and app_client_secret:
        bot = TwitchBot(server, port, bot_username, access_token, channel_name, app_client_id, app_client_secret)
        bot.start()
    else: 
        print("Access information is invalid")
        sys.exit(1)
    """

    bot = TwitchBot(server, port, bot_username, access_token, channel_name, app_client_id, app_client_secret)
    bot.start()

if __name__ == "__main__":
    main()
