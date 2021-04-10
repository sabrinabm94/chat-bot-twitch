"""
Required to use
https://dev.twitch.tv/console/apps
https://twitchapps.com/tmi/

Install modules
pip install irc
pip install requests

Commands
python chatbot.py username client id token channel
"""

import sys
import irc.bot
import requests

bot_username = 'x'
channel_name = 'x'
grant_type = 'client_credentials'

app_client_id = 'x'
auth_token = 'x'
#auth_token = 'oauth:x'

class TwitchBot(irc.bot.SingleServerIRCBot):
    def __init__(self, bot_username, channel, app_client_id, auth_token):
        self.bot_username = bot_username
        self.channel_name = channel_name
        self.app_client_id = app_client_id
        self.auth_token = auth_token

        #Authentication
        url =  'https://api.twitch.tv/helix/search/channels?query=' + self.channel_name
        headers = {'client-id': self.app_client_id, 'Authorization': 'Bearer ' + self.auth_token}
        r = requests.get(url, headers=headers).json()
        self.channel_id = r['data'][0]['id']

        #Chat connection
        server = 'irc.chat.twitch.tv'
        port = 6667
        print(' Connecting to ' + server + ' on port ' + str(port) + '...')
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port, 'oauth:'+ auth_token)], bot_username, bot_username)
        

    def on_welcome(self, c, e):
        print('Joining ' + self.channel_name)

        # You must request specific capabilities before you can use them
        c.cap('REQ', ':twitch.tv/membership')
        c.cap('REQ', ':twitch.tv/tags')
        c.cap('REQ', ':twitch.tv/commands')
        c.join(self.channel_name)

    def on_pubmsg(self, c, e):

        # If a chat message starts with an exclamation point, try to run it as a command
        if e.arguments[0][:1] == '!':
            cmd = e.arguments[0].split(' ')[0][1:]
            print('Received command: ' + cmd)
            self.do_command(e, cmd)
        return

    def do_command(self, e, cmd):
        c = self.connection

        #Get game status
        if cmd == "game":
            url = 'https://api.twitch.tv/kraken/channels/' + self.channel_id
            headers = {'Client-ID': self.client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
            r = requests.get(url, headers=headers).json()
            c.privmsg(self.channel_name, r['display_name'] + ' is currently playing ' + r['game'])

        #Get stream status
        elif cmd == "title":
            url = 'https://api.twitch.tv/kraken/channels/' + self.channel_id
            headers = {'Client-ID': self.client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
            r = requests.get(url, headers=headers).json()
            c.privmsg(self.channel_name, r['display_name'] + ' channel title is currently ' + r['status'])

        #Get basic information
        elif cmd == "raffle":
            message = "This is an example bot, replace this text with your raffle text."
            c.privmsg(self.channel_name, message)
        elif cmd == "schedule":
            message = "This is an example bot, replace this text with your schedule text."            
            c.privmsg(self.channel_name, message)

        #Error handler
        else:
            c.privmsg(self.channel_name, "Did not understand command: " + cmd)

def main():
    '''
    if username and client_id and token and channel:
        bot = TwitchBot(username, client_id, token, channel)
        bot.start()
    else: 
        print("Inválidas as informações de acesso")
        sys.exit(1)
    '''

    bot = TwitchBot(bot_username, app_client_id, auth_token, channel_name)
    bot.start()

if __name__ == "__main__":
    main()
