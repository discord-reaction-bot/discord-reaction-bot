import os
import random
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import config_manager as cm

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


def generar_texto_info():
    return (
        "**🤖 Comandos disponibles:**\n\n"
        "🔒 *Los siguientes requieren permisos de administrador:*\n"
        "`/ruser @usuario emoji` — Añade o actualiza un usuario vigilado con su reacción (máx. 20 usuarios.).\n"
        "`/rmulti-user @usuario1 @usuario2 ... emoji` — Asigna el mismo emoji a varios usuarios a la vez.\n"
        "`/redit @usuario emoji` — Cambia la reacción de un usuario ya configurado.\n"
        "`/rmulti @usuario emojis` — Asigna hasta 5 emojis (separados por espacio); el bot elige uno al azar cada vez.\n"
        "`/rchance @usuario emoji porcentaje` — Define la probabilidad (1-100%) de que el bot reaccione a ese usuario.\n"
        "`/rremove @usuario` — Elimina un usuario de la lista de vigilados.\n"
        "`/rpause` — Pausa o reanuda las reacciones automáticas.\n"
        "`/rlist` — Muestra la lista actual de usuarios vigilados, sus emojis y probabilidad.\n\n"
        "🌐 *Disponible para todos:*\n"
        "`/rinfo` — Muestra este mensaje.\n\n"
        "**¿Qué hace el bot?** Reacciona automáticamente con un emoji (o uno al azar entre varios) "
        "a los mensajes de los usuarios vigilados, según la probabilidad configurada, mientras no esté en pausa."
    )

@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user} (ID: {bot.user.id})")
    try:
        synced = await bot.tree.sync()
        print(f"✅ {len(synced)} comandos slash sincronizados.")
    except Exception as e:
        print(f"❌ Error sincronizando comandos: {e}")


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # --- Mensajes directos (DM) ---
    if message.guild is None:
        if not cm.is_dm_notified(message.author.id):
            cm.mark_dm_notified(message.author.id)
            texto = generar_texto_info()
            try:
                await message.author.send(
                    "⚠️ Solo funciono en servidores, no puedo hacer nada por aquí.\n\n" + texto
                )
            except discord.Forbidden:
                print(f"⚠️ No se pudo enviar DM a {message.author} (tiene los DMs cerrados).")
        return

    # --- Mención pura (solo <@ID_DEL_BOT>, sin nada más en el mensaje) ---
    if bot.user and message.content.strip() in (f"<@{bot.user.id}>", f"<@!{bot.user.id}>"):
        try:
            await message.channel.send("¡Hola! Para saber mis comandos usa `/rinfo` 👋")
        except discord.Forbidden:
            print(f"⚠️ Sin permisos para hablar en el canal {message.channel}.")

    # --- Reacciones automáticas ---
    try:
        config = cm.load_config(message.guild.id)
    except Exception as e:
        print(f"❌ Error leyendo config.json: {e}")
        await bot.process_commands(message)
        return

    if config.get("paused", False):
        await bot.process_commands(message)
        return

    watched = config.get("watched_users", {})
    user_id = str(message.author.id)

    if user_id in watched:
        user_data = watched[user_id]
        emojis = user_data.get("emojis", ["👍"])
        chance = user_data.get("chance", 100)

        roll = random.randint(1, 100)
        if roll <= chance:
            emoji = random.choice(emojis)
            try:
                await message.add_reaction(emoji)
            except discord.Forbidden:
                print(f"⚠️ Sin permisos para reaccionar en el canal {message.channel}.")
            except discord.HTTPException:
                print(f"⚠️ Emoji inválido o error al reaccionar en el mensaje de {message.author}.")
            except Exception as e:
                print(f"❌ Error inesperado al reaccionar: {e}")

    await bot.process_commands(message)


@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        msg = "⚠️ No tienes permisos para usar este comando."
    elif isinstance(error, app_commands.CommandOnCooldown):
        msg = "⚠️ Espera un momento antes de volver a usar este comando."
    else:
        msg = "⚠️ Ocurrió un error inesperado al ejecutar el comando."
        print(f"❌ Error no controlado: {error}")

    if interaction.response.is_done():
        await interaction.followup.send(msg, ephemeral=True)
    else:
        await interaction.response.send_message(msg, ephemeral=True)


def _validar_emoji(emoji: str, guild: discord.Guild):
    """Devuelve (válido: bool, mensaje_error: str|None)."""
    if emoji.startswith("<:") or emoji.startswith("<a:"):
        try:
            emoji_id = int(emoji.split(":")[-1].replace(">", ""))
        except (ValueError, IndexError):
            return False, "⚠️ No reconozco ese emoji personalizado. Asegúrate de escribirlo tal cual aparece al autocompletarlo con `:`."

        found = discord.utils.get(guild.emojis, id=emoji_id)
        if not found:
            return False, "⚠️ Ese emoji personalizado no pertenece a este servidor."

    return True, None


@bot.tree.command(name="ruser", description="Añade o actualiza un usuario vigilado con su reacción.")
@app_commands.default_permissions(administrator=True)
@app_commands.describe(usuario="El usuario que quieres añadir o actualizar.", reaccion="El emoji que se usará para ese usuario.")
async def ruser(interaction: discord.Interaction, usuario: discord.Member, reaccion: str):
    valido, error = _validar_emoji(reaccion, interaction.guild)
    if not valido:
        await interaction.response.send_message(error, ephemeral=True)
        return

    success, message = cm.add_watched_user(interaction.guild_id, usuario.id, reaccion)
    if success:
        await interaction.response.send_message(
            f"✅ {usuario.mention} → {reaccion}", ephemeral=True
        )
    else:
        await interaction.response.send_message(f"⚠️ {message}", ephemeral=True)


@bot.tree.command(name="rremove", description="Elimina un usuario de la lista vigilada.")
@app_commands.default_permissions(administrator=True)
@app_commands.describe(usuario="El usuario que quieres eliminar de la lista.")
async def rremove(interaction: discord.Interaction, usuario: discord.Member):
    success, message = cm.remove_watched_user(interaction.guild_id, usuario.id)
    if success:
        await interaction.response.send_message(
            f"✅ {usuario.mention} eliminado de la lista de usuarios vigilados.", ephemeral=True
        )
    else:
        await interaction.response.send_message(f"⚠️ {message}", ephemeral=True)


@bot.tree.command(name="redit", description="Cambia la reacción de un usuario ya configurado.")
@app_commands.default_permissions(administrator=True)
@app_commands.describe(usuario="El usuario a editar.", reaccion="El nuevo emoji para ese usuario.")
async def redit(interaction: discord.Interaction, usuario: discord.Member, reaccion: str):
    valido, error = _validar_emoji(reaccion, interaction.guild)
    if not valido:
        await interaction.response.send_message(error, ephemeral=True)
        return

    success, message = cm.edit_watched_user(interaction.guild_id, usuario.id, reaccion)
    if success:
        await interaction.response.send_message(
            f"✅ {usuario.mention} ahora reaccionará con {reaccion}", ephemeral=True
        )
    else:
        await interaction.response.send_message(f"⚠️ {message}", ephemeral=True)


@bot.tree.command(name="rchance", description="Define la probabilidad (1-100%) de que el bot reaccione a un usuario.")
@app_commands.default_permissions(administrator=True)
@app_commands.describe(
    usuario="El usuario a configurar.",
    emoji="Emoji a usar SOLO si el usuario aún no está configurado (se ignora si ya existe).",
    porcentaje="Probabilidad de reaccionar, del 1 al 100."
)
async def rchance(interaction: discord.Interaction, usuario: discord.Member, emoji: str, porcentaje: app_commands.Range[int, 1, 100]):
    valido, error = _validar_emoji(emoji, interaction.guild)
    if not valido:
        await interaction.response.send_message(error, ephemeral=True)
        return

    success, message = cm.set_chance(interaction.guild_id, usuario.id, emoji, porcentaje)
    prefix = "✅" if success else "⚠️"
    await interaction.response.send_message(f"{prefix} {message}", ephemeral=True)


@bot.tree.command(name="rmulti", description="Asigna hasta 5 emojis a un usuario; el bot elige uno al azar cada vez.")
@app_commands.default_permissions(administrator=True)
@app_commands.describe(
    usuario="El usuario a configurar.",
    reacciones="Emojis separados por espacio (mínimo 1, máximo 5). Ej: 🥺 🔥 😭"
)
async def rmulti(interaction: discord.Interaction, usuario: discord.Member, reacciones: str):
    emojis_list = reacciones.split()

    if len(emojis_list) < 1 or len(emojis_list) > 5:
        await interaction.response.send_message(
            "⚠️ Debes indicar entre 1 y 5 emojis, separados por espacio.", ephemeral=True
        )
        return

    for e in emojis_list:
        valido, error = _validar_emoji(e, interaction.guild)
        if not valido:
            await interaction.response.send_message(f"⚠️ Emoji inválido: {e}\n{error}", ephemeral=True)
            return

    success, message = cm.set_multi(interaction.guild_id, usuario.id, emojis_list)
    prefix = "✅" if success else "⚠️"
    await interaction.response.send_message(f"{prefix} {message}", ephemeral=True)

import re  # Añade esta línea junto a tus otros imports al inicio del archivo (con random, os, discord, etc.)


@bot.tree.command(name="rmulti-user", description="Asigna el mismo emoji a varios usuarios a la vez.")
@app_commands.default_permissions(administrator=True)
@app_commands.describe(
    usuarios="Menciona varios usuarios separados por espacio, ej: @Hanky @Shiku @Krinsi",
    emoji="El emoji que se usará para todos los usuarios mencionados."
)
async def rmulti_user(interaction: discord.Interaction, usuarios: str, emoji: str):
    valido, error = _validar_emoji(emoji, interaction.guild)
    if not valido:
        await interaction.response.send_message(error, ephemeral=True)
        return

    # Extrae todos los IDs mencionados (soporta <@ID> y <@!ID>)
    ids_encontrados = re.findall(r"<@!?(\d+)>", usuarios)

    if not ids_encontrados:
        await interaction.response.send_message(
            "⚠️ No encontré ninguna mención válida. Usa @ y selecciona los usuarios del desplegable.",
            ephemeral=True
        )
        return

    # Elimina duplicados manteniendo el orden
    ids_unicos = list(dict.fromkeys(ids_encontrados))

    añadidos, actualizados, rechazados = cm.add_multi_users(interaction.guild_id, ids_unicos, emoji)

    partes = []
    if añadidos:
        menciones = ", ".join(f"<@{uid}>" for uid in añadidos)
        partes.append(f"✅ **Añadidos** con {emoji}: {menciones}")
    if actualizados:
        menciones = ", ".join(f"<@{uid}>" for uid in actualizados)
        partes.append(f"🔄 **Actualizados** a {emoji}: {menciones}")
    if rechazados:
        menciones = ", ".join(f"<@{uid}>" for uid in rechazados)
        partes.append(f"⚠️ **No entraron** (límite de {cm.MAX_USERS} alcanzado): {menciones}")

    await interaction.response.send_message("\n".join(partes), ephemeral=True)

@bot.tree.command(name="rpause", description="Pausa o reanuda las reacciones automáticas.")
@app_commands.default_permissions(administrator=True)
async def rpause(interaction: discord.Interaction):
    paused = cm.toggle_pause(interaction.guild_id)
    if paused:
        await interaction.response.send_message(
            "⏸️ Reacciones automáticas **pausadas**.", ephemeral=True
        )
    else:
        await interaction.response.send_message(
            "▶️ Reacciones automáticas **reanudadas**.", ephemeral=True
        )


@bot.tree.command(name="rlist", description="Muestra la lista de usuarios vigilados y su reacción.")
@app_commands.default_permissions(administrator=True)
async def rlist(interaction: discord.Interaction):
    config = cm.load_config(interaction.guild_id)
    watched = config.get("watched_users", {})

    if not watched:
        await interaction.response.send_message(
            "📋 No hay usuarios vigilados actualmente.", ephemeral=True
        )
        return

    await interaction.response.defer(ephemeral=True)

    lines = []
    for user_id, data in watched.items():
        emojis_str = ", ".join(data.get("emojis", ["👍"]))
        chance = data.get("chance", 100)
        try:
            await interaction.guild.fetch_member(int(user_id))
            lines.append(f"<@{user_id}> → {emojis_str} ({chance}%)")
        except discord.NotFound:
            lines.append(f"{user_id} (ya no está en el servidor) → {emojis_str} ({chance}%)")

    status = "⏸️ Pausado" if config.get("paused", False) else "▶️ Activo"

    message = (
        f"📋 **Usuarios vigilados ({len(watched)}/{cm.MAX_USERS}):**\n"
        + "\n".join(lines)
        + f"\n\n**Estado:** {status}"
    )

    await interaction.followup.send(message, ephemeral=True)


@bot.tree.command(name="rinfo", description="Muestra la lista de comandos disponibles y qué hace cada uno.")
async def rinfo(interaction: discord.Interaction):
    await interaction.response.send_message(generar_texto_info(), ephemeral=True)


bot.run(TOKEN)