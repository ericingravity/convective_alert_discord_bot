import discord, wxdata, time, asyncio, aiocron, random
import wxdata
from discord.ext import commands


token = "" # your token here
channel_id = 1 # channel id to send alerts to
bot = commands.Bot(command_prefix='!')


# Set bot's presence
@bot.event
async def on_ready():
    a = discord.Activity(name='The Weather Channel', type=discord.ActivityType.watching)
    await bot.change_presence(activity=a)


# Convective outlook commands
outlook_help = "Get the current convective outlook for a zip code. Optionally, specify day 2 or 3 to get their outlook.\n\nExamples:\n\t!outlook 90210 2\n\t!outlook 99501"
@bot.command(name='outlook', help=outlook_help)
async def ol(ctx, zip, day=1):
    if type(day) != int:
        day = 1

    if day > 3 or day < 1:
        day = 1

    async with ctx.typing():
        latlon = wxdata.get_lat_lon_by_zip(zip)
        lat = str(latlon['latitude'])
        lon = str(latlon['longitude'])
        ol = wxdata.get_convective_outlook(lat, lon, day)
        outlook_number = str(ol['number'])
        outlook_text = ol['text']
        if day != 1:
            msg = "Day " + str(day) + " convective outlook for [" + zip + "] is [" + outlook_number + ":" + outlook_text + "]."
        else:
            msg = "Current convective outlook for [" + zip + "] is [" + outlook_number + ":" + outlook_text + "]"

    await ctx.send("```" + msg + "```")


link_help = "Returns a link to SPC\'s convective outlook page."
@bot.command(name='link', help=link_help)
async def link(ctx):
    await ctx.send("https://www.spc.noaa.gov/products/outlook/")


blurb_help = "Blurb describing what the outlooks mean."
@bot.command(name='blurb', help=blurb_help)
async def blurb(ctx):
    await ctx.send("```0. The [0:Thunderstorm] risk means a 10% or higher probability of thunderstorms is forecast during the valid period\n\n1. A [1:Marginal] risk includes severe storms of either limited organization and longevity, or very low coverage and marginal intensity.\n\n2. A [2:Slight] risk implies organized severe thunderstorms are expected, but usually in low coverage with varying levels of intensity.\n\n3. A [3:Enhanced] risk depicts a greater concentration of organized severe thunderstorms with varying levels of intensity.\n\n4. A [4:Moderate] risk indicates potential for widespread severe weather with several tornadoes and/or numerous severe thunderstorms, some of which may be intense.\n\n5. A [5:High] risk suggests a severe weather outbreak is expected from either numerous intense and long-track tornadoes, or a long-lived derecho system with hurricane-force wind gusts producing widespread damage.```")


addalert_help = "Add yourself to the convective outlook watch list by zip code. Optionally, set an alert threshold. For example, 1=Marginal and higher only, 2=Slight and higher only, etc. Default is 1. Try !blurb for more information.\n\nExamples:\n\t!addalert 90210 2\n\t!addalert 99501"
@bot.command(name='addalert', help=addalert_help)
async def addalert(ctx, zip, threshold=1):
    userid = str(ctx.message.author.id)

    if not zip:
        return

    exists = wxdata.user_exists(userid)
    if exists:
        await ctx.send("<@!" + userid + ">  `You are already on the convective outlook watch list. !removealert and try again.`")
    else:
        wxdata.add_user(userid, zip, threshold)
        await ctx.send("<@!" + userid + ">  `Added you to the convective outlook watch list for ZIP code [" + zip + "] with a threshold of [" + str(threshold) + "].`")


removealert_help = "Remove yourself from the convective outlook watch list."
@bot.command(name='removealert', help=removealert_help)
async def  removealert(ctx):
    userid = str(ctx.message.author.id)
    exists = wxdata.user_exists(userid)
    if exists:
        wxdata.remove_user(userid)
        await ctx.send("<@!" + userid + ">  `Removed you from the convective outlook watch list.`")
    else:
        await ctx.send("<@!" + userid + ">  `You were not found on the convective outlook watch list.`")


# Background task to check outlooks.
# Once an hour on minute 10 from 8a-5p.
@aiocron.crontab('10 8-17 * * *')
async def background():
    channel_to_msg = bot.get_channel(channel_id)
    msg = wxdata.background_weather()
    if msg:
        for i in msg:
            time.sleep(1)
            await channel_to_msg.send(i)


# Background task to clear alerts for the day.
# Make sure this happens outside the range for
# checking alerts.
@aiocron.crontab('30 20 * * *')
async def background2():
    wxdata.clear_alerted()


# To give the bot something to do
# while it keeps an eye on the outlooks.
@aiocron.crontab('0 */2 * * *')
async def background3():
    watchlist = [
        "The Weather Channel",
        "Twister",
        "The Perfect Storm",
        "Cloudy with a Chance of Meatballs",
        "The Finest Hours",
        "The Day After Tomorrow",
        "Sharknado"
    ]
    random_watch = random.choice(watchlist)
    a = discord.Activity(name=random_watch, type=discord.ActivityType.watching)
    await bot.change_presence(activity=a)


bot.run(token)
