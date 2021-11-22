import requests
import json
import discord

# Steam API Call
def steam_api(steam_ID):
    # GET requests to the Steam API
    API_key = '#'
    profile_response = requests.get(f'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={API_key}&steamids={steam_ID}&format=json')
    games_response = requests.get(f'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={API_key}&steamid={steam_ID}&format=json&include_appinfo=true')

    # Setting json data
    profile_name = profile_response.json()['response']['players'][0]['personaname']
    profile_url = profile_response.json()['response']['players'][0]['profileurl']
    profile_image = profile_response.json()['response']['players'][0]['avatarfull']

    # Sorting through games repsonse, grab the top 3 most played games, and convert the minutes played to hours
    all_played = []
    for data in games_response.json()['response']['games']:
        all_played.append((data['name'], data['playtime_forever']))
        all_played = sorted(all_played, key=lambda item: item[1])

    total_time = 0
    for x in all_played:
        total_time += x[1]
    total_time = round(total_time / 1440)

    most_played = [all_played[-1], all_played[-2], all_played[-3], all_played[-4], all_played[-5]]
    for index, item in enumerate(most_played):
        itemlist = list(item)
        itemlist[1] = round(itemlist[1] / 60)
        item = tuple(itemlist)
        most_played[index] = item
    return([profile_name, profile_url, profile_image, most_played, total_time])

# Setting up Discord variables 
discord_token = '#'
client = discord.Client()
# Print Discord connection
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
# Listen for messages in Development channel
@client.event
async def on_message(message):
    user_name = str(message.author).split('#')[0]
    user_message = str(message.content)
    channel = str(message.channel.name)
    error_text = f'Sorry {user_name}! I do not understand your command :( Please follow this example using your Steam ID: !steam XXXXXXXXXXXXXXXXX'
    print(f'{user_name}: {user_message} ({channel})')
    user_message_list = user_message.lower().split()
    if message.author == client.user:
        return
    if message.channel.name == 'development':
        if user_message_list[0] == '!steam':
            if len(user_message_list) == 2:
                if len(user_message_list[1]) == 17:
                    steam_info = steam_api(user_message_list[1])
                    embed = discord.Embed(title=steam_info[0], url=steam_info[1], description="Most Played Games", color=0xFF5733)
                    embed.set_thumbnail(url=steam_info[2])
                    embed.add_field(name="1st", value=f"{steam_info[3][0][0]} | {steam_info[3][0][1]} hours", inline=False)
                    embed.add_field(name="2nd", value=f"{steam_info[3][1][0]} | {steam_info[3][1][1]} hours", inline=False)
                    embed.add_field(name="3rd", value=f"{steam_info[3][2][0]} | {steam_info[3][2][1]} hours", inline=False)
                    embed.add_field(name="4th", value=f"{steam_info[3][3][0]} | {steam_info[3][3][1]} hours", inline=False)
                    embed.add_field(name="5th", value=f"{steam_info[3][4][0]} | {steam_info[3][4][1]} hours", inline=False)
                    embed.add_field(name="Total Days Gaming", value=f"{steam_info[4]} days 🤓", inline=False)
                    await message.channel.send(embed=embed)
                    return
                else:
                    await message.channel.send(error_text)
                    return
            else:
                await message.channel.send(error_text)
                return
# Start Discord connection
client.run(discord_token)