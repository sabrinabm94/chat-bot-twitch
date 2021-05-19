"""
Required to use
https://dev.twitch.tv/console/apps
https://twitchapps.com/tmi/

Install modules
pip install irc
pip install requests

Commands
python chatbot.py username client id token channel

python chatbot.py Sivy client_credentials ckl9ldbxaagizxfxdtgalaihot3qjj 03ndx73zuf2qy434ybtwlaxsqpjwym sivygames
"""

import irc.bot
import requests

bot_username = 'Sivy'
channel_name = 'sivygames'
access_token = 'oauth:digqx4bc7jwj9qe9zlimvbsmbjntj4'
app_client_id = 'ckl9ldbxaagizxfxdtgalaihot3qjj'
app_client_secret = '03ndx73zuf2qy434ybtwlaxsqpjwym'

class TwitchBot(irc.bot.SingleServerIRCBot):
    def __init__(self, bot_username, channel_name, access_token, app_client_id, app_client_secret):
        self.bot_username = bot_username
        self.channel_name = channel_name
        self.access_token = access_token
        self.app_client_id = app_client_id
        self.app_client_secret = app_client_secret
        self.channel_id = ''
        server = 'irc.chat.twitch.tv'
        port = 6667

        #Authentication
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
        
        #get channel id
        for channel in stream_info["data"]:
            if channel['broadcaster_login'] == self.channel_name:
                self.channel_id = channel['id']
                print("id: ", self.channel_id)
                break

        #bot connection in chat
        print('Connecting to ' + server + ' on port ' + str(port) + '...')
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port, access_token)], bot_username, bot_username)
        

    def on_welcome(self, c, e):
        print('Joining ' + self.channel_name)
        #You must request specific capabilities before you can use them
        c.cap('REQ', ':twitch.tv/membership')
        c.cap('REQ', ':twitch.tv/tags')
        c.cap('REQ', ':twitch.tv/commands')
        c.join(self.channel_name)
        print('Joined ' + self.channel_name)

        c.privmsg(self.channel_name, "Connected!")
        self.chatMonitoration(c, e)

    def chatMonitoration(self, c, e):
        print('chat monitoration started!')
        chatText = e.arguments

        #If a chat message starts with an exclamation point, try to run it as a command
        command_indicator = '!' 
        for text in chatText:
            if command_indicator in text:
                self.do_command(e, text)

    def do_command(self, e, command):
        c = self.connection
        print("command: ", command)

        #Get game status
        if command == "game":
            url = 'https://api.twitch.tv/kraken/channels/' + self.channel_id
            headers = {'Client-ID': self.client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
            r = requests.get(url, headers=headers).json()
            c.privmsg(self.channel_name, r['display_name'] + ' is currently playing ' + r['game'])

        #Get stream status
        elif command == "title":
            url = 'https://api.twitch.tv/kraken/channels/' + self.channel_id
            headers = {'Client-ID': self.client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
            r = requests.get(url, headers=headers).json()
            c.privmsg(self.channel_name, r['display_name'] + ' channel title is currently ' + r['status'])

       #Provide basic information to viewers
        elif command == "raffle":
            message = "This is an example bot, replace this text with your raffle text."
            c.privmsg(self.channel_name, message)

        elif command == "schedule":
            message = "This is an example bot, replace this text with your schedule text."
            c.privmsg(self.channel_name, message)

        #The command was not recognized
        else:
            c.privmsg(self.channel_name, "Did not understand command: " + command)

def main():
    """
    if bot_username and channel_name and access_token and app_client_id and app_client_secret:
        bot = TwitchBot(bot_username, channel_name, access_token, app_client_id, app_client_secret)
        bot.start()
    else: 
        print("Access information is invalid")
        sys.exit(1)
    """

    bot = TwitchBot(bot_username, channel_name, access_token, app_client_id, app_client_secret)
    bot.start()

if __name__ == "__main__":
    main()
