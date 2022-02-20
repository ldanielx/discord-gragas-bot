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

    YDL_OPTIONS = {
        "format": "bestaudio/best",
        "restrictfilenames": True,
        "noplaylist": True,
        "nocheckcertificate": True,
        "ignoreerrors": False,
        "logtostderr": False,
        "quiet": True,
        "no_warnings": True,
        "default_search": "auto",
        "source_address": "0.0.0.0",  # bind to ipv4 since ipv6 addresses cause issues sometimes
    }
    FFMPEG_OPTIONS = {
        "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
        "options": "-vn",
    }

    def __init__(self, bot):
        self.bot = bot
        self.song_queue = {}
        self.message = {}
        self.stop = False

    @staticmethod
    def parse_duration(duration):
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
        elif len(self.song_queue[ctx.guild]) == 0 and not self.stop:
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
    async def _play(self, ctx, *, music: str = ""):
        voice = get(self.bot.voice_clients, guild=ctx.guild)

        if self.author_is_connected(ctx):
            channel = ctx.author.voice.channel

            if music:
                song = Music.search(ctx.author.mention, music)

                if voice and voice.is_connected():
                    await voice.move_to(channel)
                else:
                    bonk_sound = Music.search(
                        ctx.author.mention, "Bonk Sound Effect #2"
                    )
                    self.song_queue[ctx.guild] = [bonk_sound]
                    voice = await channel.connect()

                await ctx.guild.me.edit(deafen=True)

                if not voice.is_playing():
                    self.song_queue[ctx.guild].append(song)
                    self.message[ctx.guild] = await ctx.send(embed=song["embed"])

                    voice.play(
                        FFmpegPCMAudio(
                            self.song_queue[ctx.guild][0]["source"],
                            **Music.FFMPEG_OPTIONS,
                        ),
                        after=lambda e: self.play_next(ctx),
                    )

                    voice.is_playing()
                else:
                    await ctx.send(
                        f"▶️ {song['title']} 🎵 adicionado a fila", delete_after=5.0
                    )
                    self.song_queue[ctx.guild].append(song)
                    await self.edit_message(ctx)
            else:
                voice.resume()

    @commands.command(name="pause", description="Pause the current music")
    async def _pause(self, ctx):
        voice = get(self.bot.voice_clients, guild=ctx.guild)

        if voice.is_connected() and self.author_is_connected(ctx):
            await ctx.message.delete()
            if voice.is_playing():
                await ctx.send("⏸️ Música pausada", delete_after=5.0)
                voice.pause()

    @commands.command(name="resume", description="Resume the current music")
    async def _resume(self, ctx):
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        if voice.is_connected() and self.author_is_connected(ctx):
            await ctx.message.delete()
            if not voice.is_playing():
                await ctx.send("⏯️ Música retomada", delete_after=5.0)
                voice.resume()

    @commands.command(name="skip", description="Skip the current music", aliases=["sk"])
    async def _skip(self, ctx):
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        if voice.is_playing() and self.author_is_connected(ctx):
            await ctx.message.delete()
            await ctx.send("⏭️ Música pulada", delete_after=5.0)
            voice.stop()

    @commands.command(
        name="stop",
        description="Stop the current music and clear the queue",
    )
    async def _stop(self, ctx):
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        if voice.is_playing() and self.author_is_connected(ctx):
            voice.stop()
            self.stop = True

            self.song_queue[ctx.guild] = []
            await ctx.send("⏭️ Fila parada.", delete_after=5.0)

    @commands.command(
        name="remove", description="Música removida da fila", aliases=["rm"]
    )
    async def _remove(self, ctx, *, num: int):
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        if voice.is_playing() and self.author_is_connected(ctx):
            del self.song_queue[ctx.guild][num]
            await ctx.message.delete()
            await self.edit_message(ctx)

    @commands.command(
        name="disconnect", description="Disconnect bot from channel", aliases=["dc"]
    )
    async def _disconnect(self, ctx):
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        if self.author_is_connected(ctx):
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

    def author_is_connected(self, ctx):
        if ctx.author.voice:
            return True
        else:
            run_coroutine_threadsafe(
                ctx.send(
                    "Você não está conectado a um canal de voz meu mano",
                    delete_after=10.0,
                ),
                self.bot.loop,
            ),
            return False


def setup(bot):
    bot.add_cog(Music(bot))
