import asyncio
from itertools import cycle
import json
import discord
from discord.ext import commands
from discord.commands import Option
from discord.ui import InputText, Modal, Button, View

client = commands.Bot(command_prefix=".", help_command=None, intents=discord.Intents().all())

client.load_extension('ponto')

with open('config.json', 'r') as f:
    config = json.load(f)
    TOKEN = config['token']

async def att_status():
    status = cycle(["🛠️ Desenvolvido por @mtz._", "⚔ BMR GAT"])
    while True:
        new_status = next(status) 
        await client.change_presence(activity=discord.Game(name=new_status))
        await asyncio.sleep(40)
        if new_status == "⚔ BMR GAT":  #Quando estiver no último status ↓
            users = client.get_guild(1148068124751560815).member_count
            await client.change_presence(activity=discord.Game(name=f'👮️ Gerenciando {users} policiais!'))
            await asyncio.sleep(50)

@client.event
async def on_ready():
    print('Bot está online!')
    await att_status()

@client.event
async def on_member_join(member: discord.Member):
    with open('config.json', 'r') as f:
        data = json.load(f)
    channel = client.get_channel(int(data["welcome_channel"]))
    embed = discord.Embed(title='Novo Membro!', description=f'Bem vindo ao servidor da GAT {member.mention}!\n\n'
                          '• ⚠ Se registre em <#1148213667641446431>!', color=discord.Colour.random())
    embed.set_footer(text='GAT • 2023')
    cargo = member.guild.get_role(int(data["autorole"]))
    await member.add_roles(cargo)
    await channel.send(embed=embed)

@client.event
async def on_application_command_error(ctx: discord.ApplicationContext, error: discord.DiscordException):
    if isinstance(error, commands.NoPrivateMessage):
        return await ctx.respond(f'**❌ ERRO!** Este comando não pode ser utilizado no privado.')
    if isinstance(error, commands.CommandOnCooldown):
        if error.retry_after >= 3600: 
            tempo = f'{error.retry_after / 3600:.1f} horas'
        elif error.retry_after >= 60:
            tempo = f'{error.retry_after / 60:.1f} minutos'
        else:
            tempo = f'{error.retry_after} segundos'
        return await ctx.respond(f'**❌ ERRO!** Este comando está em cooldown! Tente novamente em {tempo}!')
    if isinstance(error, commands.MissingAnyRole):
        return await ctx.respond('**❌ ERRO!** Você não tem permissão para executar este comando.\n'
                                 f'Cargo Necessário: <@&{error.missing_roles[0]}>')
    if isinstance(error, commands.MissingPermissions):
        permissions = {
            "administrator": "Administrador",
            "manage_messages": "Gerenciar Mensagens"
            }
        return await ctx.respond('**❌ ERRO!** Você não tem permissão para executar este comando.\n'
                                 f'Permissão Necessária: `{" - ".join([permissions[perm] for perm in error.missing_permissions])}`')

@client.slash_command(description='[ADM] Adiciona cargo a um usuário', guild_only=True)
@commands.has_guild_permissions(administrator=True)
async def addrole(ctx: discord.ApplicationContext, cargo: Option(discord.Role, "Digite o cargo desejado", required=True),
                  user: Option(discord.Member, "Mencione um usuário", required=True)):
    await user.add_roles(cargo)
    await ctx.respond(f'Sucesso! Você atribuiu o cargo {cargo.mention} ao {user.mention}!')

@client.slash_command(description='Envia uma mensagem EMBED!', guild_only=True)
@commands.has_guild_permissions(administrator=True)
async def embed(ctx: discord.ApplicationContext):
    embed = discord.Embed(title='Gerenciador de Embed', description='**Para enviar uma mensagem com o mesmo visual que esta (padrão embed), clique no botão abaixo, e preencha apenas os campos que você deseja.**', color=discord.Colour.red())
    embed.set_footer(text='GAT • 2023', icon_url=client.user.display_avatar)
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
        self.add_item(InputText(label='Cor da Embed', placeholder='Lista de opções: (shorturl.at/fsLZ8)', style=discord.InputTextStyle.short, required=True))
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
        embed.set_footer(text='GAT • 2023', icon_url=client.user.display_avatar)
        await inter.channel.send(embed=embed)
        await inter.response.send_message(f'✅ Embed criada com sucesso em {inter.channel.mention}!', ephemeral=True)

@client.slash_command(description='Limpa mensagens do canal', guild_only=True)
@commands.has_guild_permissions(manage_messages=True)
async def clear(ctx: discord.ApplicationContext, 
                quantidade: Option(int, 'Insira a quantidade de mensagens a serem deletadas', required=True)):
    msgs = len(
        await ctx.channel.purge(limit=quantidade)
        )
    await ctx.respond(f'Foram deletadas {msgs} mensagens!', delete_after=8.0)

@client.slash_command(description='[ADM] Seta o canal de entrada', guild_only=True)
@commands.has_guild_permissions(administrator=True)
async def setar_entrada(ctx: discord.ApplicationContext, 
                        canal: Option(discord.TextChannel, 'Insira o canal de entrada', required=True)):
    with open('config.json', 'r') as f:
        data = json.load(f)
    data["welcome_channel"] = int(canal.id)
    with open('config.json', 'w') as f:
        json.dump(data, f, indent=4)
    await ctx.respond(f'Sucesso! Canal de entrada definido em: {canal.mention}', delete_after=10.0)

@client.slash_command(description='[ADM] Seta o cargo automático para quem entrar no discord', guild_only=True)
@commands.has_guild_permissions(administrator=True)
async def setar_autorole(ctx: discord.ApplicationContext, cargo: Option(discord.Role, 'Selecione o cargo', required=True)):
    with open('config.json', 'r') as f:
        data = json.load(f)
    data["autorole"] = int(cargo.id)
    with open('config.json', 'w') as f:
        json.dump(data, f, indent=4)
    await ctx.respond(f'Sucesso! Cargo inicial setado em {cargo.mention}', delete_after=10.0)

client.run(TOKEN)