from ast import alias
import discord
from discord.ext import commands
import asyncio

#from youtube_dl import YoutubeDL

from yt_dlp import YoutubeDL

from pytube import YouTube

class music_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # all the music related stuff
        self.is_playing = False
        self.is_paused = False

        # 2d array containing [song, channel]
        self.music_queue = []
        self.YDL_OPTIONS = {'format': 'bestaudio/best',
                            'postprocessors': [{
                                'key': 'FFmpegExtractAudio',
                                'preferredcodec': 'mp3',
                                'preferredquality': '192',
                            }],
                            'noplaylist': 'True'}
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                               'options': '-vn'}

        self.vc = None

    # searching the item on youtube
    def search_yt(self, item):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info("ytsearch:{}".format(item), download=False)

            except Exception:
                return False

        print(info['entries'][0]['fulltitle'])
        print(info['title'])
        if 'youtube.com' not in info['title']:
            info['title'] = info['entries'][0]['original_url']

        #print(info['entries'][0]['original_url'])
        #print(info['entries'][0]['webpage_url'])
        ##print(info['original_url'])
        return {'source': info['title'], 'title': info['entries'][0]['fulltitle']}

    def play_next(self, ctx):
        if len(self.music_queue) > 0:
            self.is_playing = True

            # get the first url
            m_url = self.music_queue[0][0]

            yt = YouTube(m_url)
            audio_stream = yt.streams.filter(only_audio=True).first()
            audio_stream.download(filename="temp_audio.webm")

            # remove the first element as you are currently playing it
            self.music_queue.pop(0)

            #self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
            self.vc.stop()
            self.vc.play.play(discord.FFmpegPCMAudio(executable="ffmpeg", source="temp_audio.webm"), after=lambda e: self.play_next(ctx))
        else:
            self.is_playing = False

    # infinite loop checking
    async def play_music(self, ctx):
        print('3')
        if len(self.music_queue) > 0:
            self.is_playing = True

            m_url = self.music_queue[0][0]
            print(m_url['source'])

            yt = YouTube(m_url['source'])
            audio_stream = yt.streams.filter(only_audio=True).first()
            audio_stream.download(filename="temp_audio.webm")


            # try to connect to voice channel if you are not already connected

            # remove the first element as you are currently playing it
            self.music_queue.pop(0)
            server = ctx.message.guild
            voice_channel = server.voice_client
            #voice_channel.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
            self.vc.stop()
            self.vc.play(discord.FFmpegPCMAudio(executable="ffmpeg", source="temp_audio.webm"), after=lambda e: self.play_next(ctx))
            print('6')
        else:
            self.is_playing = False

        await asyncio.sleep(5)

    @commands.command(name="play", aliases=["p", "playing"], help="Plays a selected song from youtube")
    async def play(self, ctx, *args):
        query = " ".join(args)

        voice_channel = ctx.author.voice.channel

        await ctx.message.delete()
        # if voice_channel is None:
        # you need to be connected so that the bot knows where to go
        #   await ctx.send("Connect to a voice channel!")
        if self.is_paused:
            self.vc.resume()
        else:
            song = self.search_yt(query)
            if type(song) == type(True):
                await ctx.send("Chceš pěstí? 'URL'")
            else:
                # await ctx.send("Song added to the queue")
                self.music_queue.append([song, voice_channel])
                print('1')
                if self.vc == None or not self.vc.is_connected():
                    print('4')
                    self.vc = await voice_channel.connect()
                    print('4.4')
                    # in case we fail to connect
                    if self.vc == None:
                        await ctx.send("Nemůžu se připojit mrdko")
                        return
                else:
                    print('4.2')
                    await self.vc.move_to(self.music_queue[0][1])

                if self.is_playing == False:
                    print('2')
                    await self.play_music(ctx)

    @commands.command(name="pause", help="Pauses the current song being played")
    async def pause(self, ctx, *args):
        if self.is_playing:
            self.is_playing = False
            self.is_paused = True
            self.vc.pause()
        elif self.is_paused:
            self.is_paused = False
            self.is_playing = True
            self.vc.resume()

    @commands.command(name="resume", aliases=["r"], help="Resumes playing with the discord bot")
    async def resume(self, ctx, *args):
        if self.is_paused:
            self.is_paused = False
            self.is_playing = True
            self.vc.resume()

    @commands.command(name="skip", aliases=["s"], help="Skips the current song being played")
    async def skip(self, ctx):
        await ctx.message.delete()
        if self.vc != None and self.vc:
            self.vc.stop()
            # try to play next in the queue if it exists
            await self.play_music(ctx)

    @commands.command(name="queue", aliases=["q"], help="Displays the current songs in queue")
    async def queue(self, ctx):
        await ctx.message.delete()
        retval = ""
        for i in range(0, len(self.music_queue)):
            # display a max of 5 songs in the current queue
            if (i > 4): break
            retval += self.music_queue[i][0]['title'] + "\n"

        if retval != "":
            await ctx.send(retval)
        else:
            await ctx.send("Nic tu nemam ty svině")

    @commands.command(name="clear", aliases=["c", "bin"], help="Stops the music and clears the queue")
    async def clear(self, ctx):
        if self.vc != None and self.is_playing:
            self.vc.stop()
        self.music_queue = []
        await ctx.send("Vyčistil jsem")

    @commands.command(name="leave", aliases=["disconnect", "l", "d"], help="Kick the bot from VC")
    async def dc(self, ctx):
        self.is_playing = False
        self.is_paused = False
        await self.vc.disconnect()
