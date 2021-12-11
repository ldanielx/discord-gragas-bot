from discord import Embed, FFmpegPCMAudio
from discord.ext import commands
from discord.utils import get
from youtube_dl import YoutubeDL
from asyncio import run_coroutine_threadsafe

import time
import requests
import random


class Music(commands.Cog, name="Music"):
    """
    Can be used by anyone and allows you to listen to music or videos.
    """

    YDL_OPTIONS = {"format": "bestaudio", "noplaylist": "True", "verbose": "True"}
    FFMPEG_OPTIONS = {
        "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
        "options": "-vn",
    }

    def __init__(self, bot):
        self.bot = bot
        self.song_queue = {}
        self.message = {}

    @staticmethod
    def parse_duration(duration):
        result = []
        m, s = divmod(duration, 60)
        h, m = divmod(m, 60)
        return f"{h:d}:{m:02d}:{s:02d}"

    @staticmethod
    def search(author, arg):
        with YoutubeDL(Music.YDL_OPTIONS) as ydl:
            try:
                requests.get(arg)
            except:
                info = ydl.extract_info(f"ytsearch:{arg}", download=False)["entries"][0]
            else:
                info = ydl.extract_info(arg, download=False)

        titles = [
            "🎵 Olha a saideira! 🍺",
            "🍺 Toma uma gelada! 🎵",
            "🎵 Happy hour to chegando! 🍺",
            "🍺 Ta na hora de encher o pote! 🎵",
        ]

        embed = (
            Embed(
                title=(random.choice(titles)),
                description=f"[{info['title']}]({info['webpage_url']})",
                color=0xDB3498,
            )
            .add_field(name="Duração", value=Music.parse_duration(info["duration"]))
            .add_field(name="Pedido por", value=author)
            .add_field(
                name="Autor", value=f"[{info['uploader']}]({info['channel_url']})"
            )
            .add_field(name="Fila", value=f"Não há musicas na fila")
            .set_thumbnail(url=info["thumbnail"])
        )

        return {
            "embed": embed,
            "source": info["formats"][0]["url"],
            "title": info["title"],
        }

    async def edit_message(self, ctx):
        embed = self.song_queue[ctx.guild][0]["embed"]
        content = (
            "\n".join(
                [
                    f"({self.song_queue[ctx.guild].index(i)}) {i['title']}"
                    for i in self.song_queue[ctx.guild][1:]
                ]
            )
            if len(self.song_queue[ctx.guild]) > 1
            else "Não há musicas na fila."
        )
        embed.set_field_at(index=3, name="Fila:", value=content, inline=False)
        await self.message[ctx.guild].edit(embed=embed)

    def play_next(self, ctx):
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        if len(self.song_queue[ctx.guild]) > 1:
            del self.song_queue[ctx.guild][0]
            run_coroutine_threadsafe(self.edit_message(ctx), self.bot.loop)

            voice.play(
                FFmpegPCMAudio(
                    self.song_queue[ctx.guild][0]["source"], **Music.FFMPEG_OPTIONS
                ),
                after=lambda e: self.play_next(ctx),
            )
            voice.is_playing()
        else:
            try:
                self.play_bark_sound_effect(ctx, voice)
                run_coroutine_threadsafe(
                    self.message[ctx.guild].delete(), self.bot.loop
                )
            except Exception as error:
                pass

    @commands.command(
        name="play",
        aliases=["p"],
        description="Listen to a video from an url or from a youtube search",
    )
    async def _play(self, ctx, *, video: str):
        channel = ctx.author.voice.channel
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        song = Music.search(ctx.author.mention, video)
        bonk_sound = Music.search(ctx.author.mention, "Bonk Sound Effect #2")

        if voice and voice.is_connected():
            await voice.move_to(channel)
        else:
            voice = await channel.connect()

        await ctx.guild.me.edit(deafen=True)

        if not voice.is_playing():
            self.song_queue[ctx.guild] = [bonk_sound]
            self.song_queue[ctx.guild].append(song)
            self.message[ctx.guild] = await ctx.send(embed=song["embed"])

            voice.play(
                FFmpegPCMAudio(
                    bonk_sound["source"],
                    **Music.FFMPEG_OPTIONS,
                ),
                after=lambda e: self.play_next(ctx),
            )

            voice.is_playing()
        else:
            self.song_queue[ctx.guild].append(song)
            await self.edit_message(ctx)

    @commands.command(name="pause", description="Pause the current music")
    async def _pause(self, ctx):
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        if voice.is_connected():
            await ctx.message.delete()
            if voice.is_playing():
                await ctx.send("⏸️ Música pausada", delete_after=5.0)
                voice.pause()
            else:
                await ctx.send("⏯️ Música retomada", delete_after=5.0)
                voice.resume()

    @commands.command(name="skip", description="Skip the current music", aliases=["sk"])
    async def _skip(self, ctx):
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        if voice.is_playing():
            await ctx.message.delete()
            await ctx.send("⏭️ Música pulada", delete_after=5.0)
            voice.stop()

    @commands.command(
        name="remove", description="Música removida da fila", aliases=["rm"]
    )
    async def _remove(self, ctx, *, num: int):
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        if voice.is_playing():
            del self.song_queue[ctx.guild][num]
            await ctx.message.delete()
            await self.edit_message(ctx)

    @commands.command(
        name="leave", description="Leave bot from channel", aliases=["lv"]
    )
    async def _leave(self, ctx):
        server = ctx.message.guild.voice_client
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        self.play_bark_sound_effect(ctx, voice)

    def play_bark_sound_effect(self, ctx, voice):
        if voice.is_playing():
            voice.stop()

        exit_sound = Music.search(
            ctx.author.mention,
            "https://www.youtube.com/watch?v=b-fX44-tJHI&ab_channel=CoolSoundFX",
        )

        voice.play(FFmpegPCMAudio(exit_sound["source"], **Music.FFMPEG_OPTIONS))

        while voice.is_playing():
            time.sleep(1)

        if not voice.is_playing():
            run_coroutine_threadsafe(voice.disconnect(), self.bot.loop),


def setup(bot):
    bot.add_cog(Music(bot))