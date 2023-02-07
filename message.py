# -*- coding: utf-8 -*-

import discord
import youtube_dl
from discord import FFmpegOpusAudio
from discord.ext import commands
from discord.utils import get
import requests
import json
from asyncio import sleep
import logging

class tools():
    def get_audio_url_yt(url): # get audio info by url from youtube
        YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'False'}
        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:info = ydl.extract_info(url, download=False)
        return info['formats'][0]['url'], info['title'], info['duration'], info['thumbnails'][1]['url']
    def set_msg(name, duration): # set message for send in chat
        return(f"Now playing: {name}\nDuration is: {duration}")
    def set_time(sec): # get format duration from audio time
        if sec >= 60:
            h = sec//60
            f = sec - 60 * h
            if f//10 < 1:
                f = str("0") + str(f)
            return str(h) + ":" + str(f)
        else:
            return "0:" + str(sec)
    def download_png(url): # download image for send with set_msg()
        html = requests.get(url)
        with open('2.png', 'wb')as fp:fp.write(html.content)
    def read_json(filename): # read config
        with open(filename, 'rb')as fp: return json.load(fp)
    def write_json(filename, write_obj): # write config
        with open(filename, 'w')as fp: json.dump(write_obj,fp)
    def start_logging(ctx, url1, type1):
        logging.info(f'author is: {ctx.author}')
        logging.info(f'url1: {url1}')
        logging.info(f'Get audio: get_audio_url_{type1}')


class vk_tools():
    def get_audio_by_id(t, url1): # get audio info by id from vk
        req = requests.session()
        json1 = tools.read_json('config.json')
        headers = {'User-Agent': json1['user_agent']}
        params = {'access_token': json1['vk_token'],'owner_id': url1,'album_id': None,'audio_ids': None,'need_user': 0,'offset': t,'count': 1,'v': '5.81'}
        a = req.get(url='https://api.vk.com/method/audio.get',headers=headers,params=params)
        return a.json()
    def get_audio_by_search(url1): # get audio info by search from vk
        req = requests.session()
        json1 = tools.read_json('config.json')
        headers = {'User-Agent': json1['user_agent']}
        params = {'access_token': json1['vk_token'],'q': url1,'auto_complete': 0,'lyrics': 0,'performer_only': 0,'sort': 2,'search_own': 0,'offset': 0,'count': 5,'v': '5.81'}
        a = req.get(url='https://api.vk.com/method/audio.search',headers=headers,params=params)
        return a.json()
    def get_dur(j): # get duration of music from vk
        return j['response']['items'][0]['duration']
    def get_title(j): # get title of music from vk
        return j['response']['items'][0]['title']
    def get_url(j): # get url of music from vk
        return j['response']['items'][0]['url']
    def get_count(url1): # get count of music in account from vk
        j = vk_tools.get_audio_by_id(0, url1)
        return j['response']['count']
    def format_tool(t, f): # format tools for logging
        return t, f
    def check_user(ctx):
        a = tools.read_json('q.json')
        for i in a.keys():
            for j in a[i].keys():
                if j == str(ctx.author):
                    return True
        return False
class queue():
    def get_all(ctx):
        id1 = str(ctx.message.guild.id)
        mes = ''
        t = 0
        json1 = tools.read_json('q.json')
        if json1[id1]['name'] == []:
            mes = 'None'
        else:
            for i in json1[id1]['name']:
                mes += f'\n{t}.{i}'
                t += 1
        return mes
    def clear():
        json1 = tools.read_json('q.json')
        for i in json1.keys():
            json1[i]['id_or_url'] = []
            json1[i]['type'] = []
            json1[i]['t'] = []
            json1[i]['name'] = []
            json1[i].update(num = 'None')
        tools.write_json('q.json', json1)
    def add_json(id_or_url, type1, t, ctx, name):
        json1 = tools.read_json('q.json')
        id1 = str(ctx.message.guild.id)
        if len(json1[id1]['id_or_url']) >= 5:
            queue.clear()
        json1[id1]['id_or_url'].append(id_or_url) # writing in queue
        json1[id1]['type'].append(type1)
        json1[id1]['t'].append(t)
        json1[id1]['name'].append(name)
        logging.info(f'json1 is: {str(json1)}')
        tools.write_json('q.json', json1)
    def delete_json(num, ctx):
        json1 = tools.read_json('q.json')
        id1 = str(ctx.message.guild.id)
        json1[id1]['id_or_url'].pop(num) # delete in queue
        json1[id1]['type'].pop(num)
        json1[id1]['t'].pop(num)
        logging.info(f'json1 is: {str(json1)}')
        tools.write_json('q.json')
    def check(num, ctx):
        json1 = tools.read_json('q.json')
        if len(json1[str(ctx.message.guild.id)]['id_or_url']) >= 1:
            try: num = int(num)
            except: None
            if num == 'None':
                pack = json1[str(ctx.message.guild.id)]
                id_or_url, type1, t = pack['id_or_url'][0], pack['type'][0], pack['t'][0]
                logging.info(f'q.json queue pack is : {pack}')
                return True, id_or_url, type1, t
            else:
                pack = json1[str(ctx.message.guild.id)]
                id_or_url, type1, t = pack['id_or_url'][num], pack['type'][num], pack['t'][num]
                logging.info(f'q.json queue pack is : {pack}')
                return True, id_or_url, type1, t
        return False, None, None, None
    def replace_json(old1, new1, json1):
        print() # //
    def set_queue_num(num2, ctx):
        json1 = tools.read_json('q.json')
        json1[str(ctx.message.guild.id)].update(num = num2)
        tools.write_json('q.json', json1)
        logging.info(f'Changed num is : {queue.check_queue_num(ctx)}')
    def check_queue_num(ctx):
        json1 = tools.read_json('q.json')
        return json1[str(ctx.message.guild.id)]['num']
    def check_rm(ctx):
        json1 = tools.read_json('q.json')
        id1 = str(ctx.message.guild.id)
        try:len(json1[id1])
        except:
            queue.add_server_q(id1)
            json1 = tools.read_json('q.json')
        logging.info(f'q.json is: {json1}')
        if len(json1[id1]['id_or_url']) >= 5:
            queue.clear()
    def add_server_q(id1):
        a = tools.read_json('q.json')
        a.update({id1: {'id_or_url': [], 'type': [], 't': [], 'num': 'None', 'name': []}})
        tools.write_json('q.json', a)

#start
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
json1 = tools.read_json('config.json') # open config file
logging.info('config.json is open')
queue.clear()
client = commands.Bot(command_prefix=json1["prefix"])

@client.event
async def on_ready():
    logging.info("Bot is ready") # check bot status
@client.command()
async def pause(ctx): # for pause music
    voice_client = ctx.message.guild.voice_client
    if voice_client and  voice_client.is_playing(): 
        try: await voice_client.pause() # pause
        except: logging.info('Audio is paused by ' + str(ctx.author))
    else: logging.info('Nothing is played')
@client.command()            
async def resume(ctx): # for resume music
    voice_client = ctx.message.guild.voice_client
    if not voice_client.is_playing():
        try: await voice_client.resume() # resume
        except: logging.info('Audio is resumed by ' + str(ctx.author))
    else: logging.info('Nothing is played')
@client.command(name='ypu') 
async def youtubeplay_url( ctx, url1: str):
    queue.check_rm(ctx)
    tools.start_logging(ctx, url1, type1='yt')
    #loging block
    voice = get(client.voice_clients, guild=ctx.guild)
    logging.info('None queue')
    i, s, d, k = tools.get_audio_url_yt(url1) #get audio source
    if await qucheck( ctx, voice, 'yp', url1, 'search', s):return 0
    logging.info(f"Now playing: {s}, Duration is: {d}")
    channel = ctx.message.author.voice.channel
    if voice and voice.is_connected():await voice.move_to(channel) #connect voice channel
    else:voice = await channel.connect()
    tools.download_png(k)
    msg = tools.set_msg(s, tools.set_time(d))
    await ctx.send(msg,file=discord.File('2.png')) #send info msg
    logging.info(f'Url is: {i}')
    voice.play(FFmpegOpusAudio(source = i)) #audio play
    while voice.is_playing() or voice.is_paused():await sleep(1)
    await start_queue(ctx)
@client.command()
async def vkll( ctx, url1: str, t):
    queue.check_rm(ctx)
    if t != 'search': type1 = 'id'
    else: type1 = 'search'
    tools.start_logging(ctx, url1, type1)
    #loging block
    voice = get(client.voice_clients, guild=ctx.guild)
    logging.info('None queue')
    if t == 'search':j = vk_tools.get_audio_by_search(url1.replace('_', ''))#get audio source
    else:j = vk_tools.get_audio_by_id(t, url1.replace('_', ''))
    logging.info('Pack is:' + str(j))
    title, dur = '', ''
    title, dur = vk_tools.format_tool(vk_tools.get_title(j), tools.set_time(vk_tools.get_dur(j))) #format info
    logging.info(f'Title is: {title},Duration is: {dur}')
    url = vk_tools.get_url(j) # get audio url
    if await qucheck( ctx, voice, type1, url1, t, title):return 0
    channel = ctx.message.author.voice.channel
    if voice and voice.is_connected():await voice.move_to(channel) #connect voice channel
    else:voice = await channel.connect()
    await ctx.send(tools.set_msg(title, dur)) #send info
    logging.info(f'Url is: {url}')
    voice.play(FFmpegOpusAudio(source=url)) #play audio
    while voice.is_playing() or voice.is_paused():await sleep(1)
    await start_queue(ctx)
@client.command()
async def vks( ctx, url1: str):
    await vkll(ctx, url1, 'search')
async def qucheck( ctx, voice, type1, url1, t, name):
    if voice and voice.is_playing():
        queue.add_json(url1, type1, t, ctx, name) # writing in queue
        logging.info(f'{name} in queue')
        await ctx.send(f'{ctx.message.author.mention}, {name} in queue.')
        return True
@client.command()
async def vk( ctx, url1):
    if not vk_tools.check_user(ctx):
        ctx.reply('Please set vk id. Use ">set" for it')
        return 0
    voice = get(client.voice_clients, guild=ctx.guild)
    t = 0
    for j in range(vk_tools.get_count(url1)): #get count of audio in account
        await pause(ctx)
        await vkll(ctx, url1, t)
        while voice and voice.is_playing() or voice and voice.is_paused():await sleep(1)
        t += 1
@client.command(name='set')
async def set_vk(ctx, url1):
    author1 = str(ctx.author)
    f = {author1:url1}
    a = tools.read_json('q.json')
    for i in a.values():
        try: 
            i[author1]
            a[str(ctx.message.guild.id)].update(f)
            await ctx.send('Your data has been overwrited')
        except:
            a[str(ctx.message.guild.id)].update(f)
            await ctx.send('Your data has been writed')
    tools.write_json('q.json', a)
@client.command()
async def ss( ctx, url1):
    a = tools.read_json('q.json')
    url = a[str(ctx.message.guild.id)][str(ctx.author)]
    await vkll( ctx, url, url1)
async def start_queue( ctx):
    num = queue.check_queue_num(ctx)
    is1, id_or_url, type1, t = queue.check(num, ctx)
    if is1 == False:return 0   
    else:
        if type1 == 'yp':
            if num == 'None':
                queue.set_queue_num(0, ctx)
            else:
                queue.set_queue_num(num + 1, ctx)
            await youtubeplay_url(ctx, id_or_url)
        if type1 == 'search':
            if num == 'None':
                queue.set_queue_num(0, ctx)
            else:
                queue.set_queue_num(num + 1, ctx)
            await vks( ctx, id_or_url)
        if type1 == 'id':
            if num == 'None':
                queue.set_queue_num(0, ctx)
            else:
                queue.set_queue_num(num + 1, ctx)
            await vkll( ctx, id_or_url, t)
@client.command(name='n')
async def next(ctx):
    if len(tools.read_json('q.json')[str(ctx.message.guild.id)]['id_or_url']) < 1:
        logging.info('no Next today')
        await ctx.send('no Next today')
        return 0
    else:
        logging.info('Next queue')
        d = 1
        num = queue.check_queue_num(ctx)
        if num == 'None':
            num = 0
            d = 0
        logging.info(f'num is : {num}')
        await pause(ctx)
        is1, id_or_url, type1, t = queue.check(num + d, ctx)
        if is1 == False:return 0   
        else:
            if type1 == 'yp':
                queue.set_queue_num(num + d, ctx)
                await youtubeplay_url(ctx, id_or_url)
            if type1 == 'search':
                queue.set_queue_num(num + d, ctx)
                await vks(ctx, id_or_url)
            if type1 == 'id':
                queue.set_queue_num(num + d, ctx)
                await vkll(ctx, id_or_url, t)


@client.command(name='p')
async def prev(ctx):
    if tools.read_json('q.json')[str(ctx.message.guild.id)]['num'] == 'None' or tools.read_json('q.json')[str(ctx.message.guild.id)]['num'] == 0:
        logging.info('no Prev today')
        await ctx.reply('no Prev today')
        return 0
    else:
        logging.info('Prev queue')
        d = 1
        num = queue.check_queue_num(ctx)
        logging.info(f'num is : {num}')
        await pause(ctx)
        is1, id_or_url, type1, t = queue.check(num - 1, ctx)
        if is1 == False:return 0   
        else:
            if type1 == 'yp':
                queue.set_queue_num(num + d, ctx)
                await youtubeplay_url(ctx, id_or_url)
            if type1 == 'search':
                queue.set_queue_num(num + d, ctx)
                await vks(ctx, id_or_url)
            if type1 == 'id':
                queue.set_queue_num(num + d, ctx)
                await vkll(ctx, id_or_url, t)

@client.command(name='q')
async def printq(ctx):
    await ctx.send(queue.get_all(ctx))

client.run(json1["token"]) # start bot