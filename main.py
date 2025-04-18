import asyncio
import aiohttp
from itertools import cycle
import json
import discord
import pytz
from discord.ext import commands
from discord.commands import Option
from discord.ui import InputText, Modal, Button, View
from datetime import datetime
from db import get_configs

client = commands.Bot(command_prefix=".", help_command=None, intents=discord.Intents().all())
client.load_extension('ponto')

config = get_configs()

async def att_status():
    status = cycle(["🛠️ Desenvolvido por @mtz._", f"⚔ {config['server_name']}"])
    while True:
        new_status = next(status)
        await client.change_presence(activity=discord.Game(name=new_status))
        await asyncio.sleep(40)
        if new_status == f"⚔ {config['server_name']}":  # Quando estiver no último status ↓
            users = client.get_guild(1267945413139238922).member_count
            await client.change_presence(activity=discord.Game(name=f'👮️ Gerenciando {users} policiais!'))
            await asyncio.sleep(50)

@client.event
async def on_ready():
    print('Bot está online!')
    await att_status()

@client.event
async def on_member_join(member: discord.Member):
    if member.guild.id == 1267945413139238922:
        with open('config.json', 'r') as f:
            data = json.load(f)
        channel = client.get_channel(int(data["welcome_channel"]))
        embed = discord.Embed(title='Novo Membro!', description=f'Bem vindo ao servidor do {config['server_name']} {member.mention}!\n\n'
                            '• <:aviso:1269036173381206132> Se registre em <#1268404417359777843>!', color=discord.Colour.random())
        embed.set_footer(text=f'{config['server_name']} • 2024')
        await channel.send(embed=embed)
        cargo = member.guild.get_role(int(data["autorole"]))
        await member.add_roles(cargo)

@client.event
async def on_application_command_error(ctx: discord.ApplicationContext, error: discord.DiscordException):
    if isinstance(error, commands.NoPrivateMessage):
        return await ctx.respond('**<a:x_:1269034170395394118> ERRO!** Este comando não pode ser utilizado no privado.')

    if isinstance(error, commands.CommandOnCooldown):
        if error.retry_after >= 3600:
            tempo = f'{error.retry_after / 3600:.1f} horas'
        elif error.retry_after >= 60:
            tempo = f'{error.retry_after / 60:.1f} minutos'
        else:
            tempo = f'{round(error.retry_after)} segundos'
        return await ctx.respond(f'**<a:x_:1269034170395394118> ERRO!** Este comando está em cooldown! Tente novamente em `{tempo}`!', ephemeral=True)

    if isinstance(error, commands.MissingAnyRole):
        return await ctx.respond('**<a:x_:1269034170395394118> ERRO!** Você não tem permissão para executar este comando.\n'
                                 f'> Cargo Necessário: <@&{error.missing_roles[0]}>')

    if isinstance(error, commands.MissingPermissions):
        permissions = {
            "administrator": "Administrador",
            "manage_messages": "Gerenciar Mensagens"
        }
        return await ctx.respond('**<a:x_:1269034170395394118> ERRO!** Você não tem permissão para executar este comando.\n'
                                 f'> Permissão Necessária: `{" - ".join([permissions[perm] for perm in error.missing_permissions])}`')

    canallog = client.get_channel(config['log_channel_id'])
    if ctx.command is None:
        comando = "Nenhum/Invalído"
    else:
        comando = ctx.command
    embedlog = discord.Embed(title='ERRO!', description=f'Comando utilizado: `{comando}`\nServidor: `{ctx.guild.name} / {ctx.guild.id}`\nCanal do comando: `{ctx.channel} / {ctx.channel.id}`\nAutor do comando: {ctx.author.mention} `/ {ctx.author.id}`\n\n**ERRO:**\n```py\n{error}\n```', color=discord.Colour.red())
    embedlog.set_footer(text='Developed by mtz._')
    await canallog.send(embed=embedlog)

@client.slash_command(description='Gera o relatório de prisão automaticamente', contexts={discord.InteractionContextType.guild})
async def prisao(ctx: discord.ApplicationContext,
                policias: Option(str, 'Digite o Nome ou ID dos policiais envolvidos', required=True),
                acusado: Option(str, 'Digite o Nome e ID do cidadão a ser preso', required=True, min_length=5),
                motivo: Option(str, 'Digite o motivo da prisão', required=True),
                pena: Option(str, 'Insira a pena e a multa aplicada', required=True),
                foto: Option(discord.Attachment, 'Coloque uma foto do acusado', required=False)):

    em = discord.Embed(colour=discord.Colour.brand_red(), description=f'**- <:policia:1269035235463397397> Policiais presentes:** **`{policias}`**\n'
        f'**- 🔒 Cidadão detido:** **`{acusado}`**\n'
        f'**- 📜 Motivo da Prisão:** **`{motivo}`**\n**- ⚖️ Pena e Multa aplicada:** **`{pena}`**')


    em.set_author(name=f'Relatório de prisão criado por: {ctx.author.name}', icon_url=ctx.author.display_avatar)
    if foto:
        em.set_image(url=foto.url)
    em.set_footer(text=f'{datetime.now(pytz.timezone("America/Sao_Paulo")).strftime("%d/%m/%Y - %H:%M")} | {config["server_name"]}')
    canal_prisao = ctx.guild.get_channel(1268404437366607946)
    msg = await canal_prisao.send(embed=em)
    await ctx.respond(f'**✅ Sucesso!** Relatório de prisão criado! {msg.jump_url}', ephemeral=True)

@client.slash_command(description='[ADM] Adiciona cargo a um usuário', contexts={discord.InteractionContextType.guild})
@commands.has_guild_permissions(administrator=True)
async def addrole(ctx: discord.ApplicationContext, cargo: Option(discord.Role, "Digite o cargo desejado", required=True),
                  user: Option(discord.Member, "Mencione um usuário", required=True)):
    await user.add_roles(cargo)
    await ctx.respond(f'Sucesso! Você atribuiu o cargo {cargo.mention} ao {user.mention}!')

@client.slash_command(description='Envia uma mensagem EMBED!', contexts={discord.InteractionContextType.guild})
@commands.has_guild_permissions(administrator=True)
async def embed(ctx: discord.ApplicationContext):
    embed = discord.Embed(title='Gerenciador de Embed', description='**Para enviar uma mensagem com o mesmo visual que esta (padrão embed), clique no botão abaixo, e preencha apenas os campos que você deseja.**', color=discord.Colour.red())
    embed.set_footer(text=f'{config["server_name"]} • 2024', icon_url=client.user.display_avatar)
    create_embed = Button(label='Criar Embed', style=discord.ButtonStyle.blurple, emoji='🛠')
    async def button_callback(inter: discord.Interaction):
        await inter.response.send_modal(embed_modal(ctx))

    view = View()
    view.add_item(create_embed)
    create_embed.callback = button_callback
    await ctx.respond(embed=embed, ephemeral=True, view=view)

class embed_modal(Modal):
    def __init__(self, ctx) -> None:
        self.ctx = ctx
        super().__init__(title='Gerador de Embed', timeout=720)
        self.add_item(InputText(label='Título da Embed', style=discord.InputTextStyle.short, required=True, max_length=250))
        self.add_item(InputText(label='Descrição da Embed', style=discord.InputTextStyle.long, required=True, max_length=4000))
        self.add_item(InputText(label='Imagem (thumbnail)', placeholder='Links suportados: https:// e http://', style=discord.InputTextStyle.short, required=False))
        self.add_item(InputText(label='Imagem grande', placeholder='Links suportados: https:// e http://', style=discord.InputTextStyle.short, required=False))
        self.add_item(InputText(label='Cor da Embed', style=discord.InputTextStyle.short, required=True))

    async def callback(self, inter: discord.Interaction):
        embed = discord.Embed(title=self.children[0].value, description=self.children[1].value)
        try:
            color = getattr(discord.Colour, self.children[4].value.lower())
        except AttributeError:
            color = discord.Colour.random

        if self.children[2].value.startswith('http:') or self.children[2].value.startswith('https:'):
            embed.set_thumbnail(url=self.children[2].value)
        if self.children[3].value.startswith('http:') or self.children[3].value.startswith('https:'):
            embed.set_image(url=self.children[3].value)

        embed.color = color()
        embed.set_footer(text=f'{config["server_name"]} • 2024', icon_url=client.user.display_avatar)
        await inter.channel.send(embed=embed)
        await inter.response.send_message(f'<a:check:1269034091882221710> Embed criada com sucesso em {inter.channel.mention}!', ephemeral=True)

@client.slash_command(description='Limpa mensagens do canal', contexts={discord.InteractionContextType.guild})
@commands.has_guild_permissions(manage_messages=True)
async def clear(ctx: discord.ApplicationContext,
                quantidade: Option(int, 'Insira a quantidade de mensagens a serem deletadas', required=True)):
    msgs = len(
        await ctx.channel.purge(limit=quantidade, bulk=True)
    )
    await ctx.respond(f'<a:check:1269034091882221710> Foram deletadas {msgs} mensagens!', delete_after=8.0)

@client.slash_command(description='Obtém quantidade de players atual no servidor', contexts={discord.InteractionContextType.guild})
@commands.cooldown(1, 10, commands.BucketType.user)
async def players(ctx: discord.ApplicationContext):
    msg = await ctx.respond('<a:loading:1269034073444319355> Carregando informações do servidor...')
    with open('config.json', 'r') as f:
        data = json.load(f)
    ip = data["server_ip"]
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'http://{ip}/players.json') as res:
                player_count = len(json.loads(await res.text()))
    except aiohttp.ClientError:
        return await ctx.respond('<a:x_:1269034170395394118> ERRO! Ocorreu um problema ao contactar o servidor. Verifique se o IP está setado corretamente.')

    await asyncio.sleep(1)
    await msg.edit_original_response(content=f'**{config["server_name"]} - Jogadores Online:** {player_count}!\n[Clique Aqui para conectar](http://{config["server_ip"]}/)\n-# Atualizado nos últimos 10 segundos.')

@client.slash_command(description='[ADM] Seta o ip do servidor', contexts={discord.InteractionContextType.guild})
@commands.has_guild_permissions(administrator=True)
async def setar_ip(ctx: discord.ApplicationContext, ip: Option(str, 'Insira o IP completo do servidor', required=True)):
    with open('config.json', 'r') as f:
        data = json.load(f)
    data["server_ip"] = ip
    with open('config.json', 'w') as f:
        json.dump(data, f, indent=4)
    await ctx.respond(f'<a:check:1269034091882221710> Sucesso! IP do servidor definido em: {ip}', delete_after=10.0)

@client.slash_command(description='[ADM] Seta o canal de entrada', contexts={discord.InteractionContextType.guild})
@commands.has_guild_permissions(administrator=True)
async def setar_entrada(ctx: discord.ApplicationContext,
                        canal: Option(discord.TextChannel, 'Insira o canal de entrada', required=True)):
    with open('config.json', 'r') as f:
        data = json.load(f)
    data["welcome_channel"] = int(canal.id)
    with open('config.json', 'w') as f:
        json.dump(data, f, indent=4)
    await ctx.respond(f'<a:check:1269034091882221710> Sucesso! Canal de entrada definido em: {canal.mention}', delete_after=10.0)

@client.slash_command(description='[ADM] Seta o cargo automático para quem entrar no discord', contexts={discord.InteractionContextType.guild})
@commands.has_guild_permissions(administrator=True)
async def setar_autorole(ctx: discord.ApplicationContext, cargo: Option(discord.Role, 'Selecione o cargo', required=True)):
    with open('config.json', 'r') as f:
        data = json.load(f)
    data["autorole"] = int(cargo.id)
    with open('config.json', 'w') as f:
        json.dump(data, f, indent=4)
    await ctx.respond(f'<a:check:1269034091882221710> Sucesso! Cargo inicial setado em {cargo.mention}', delete_after=10.0)

client.run(config['token'])