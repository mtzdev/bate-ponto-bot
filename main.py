import json
import discord
from discord.ext import commands
from discord.commands import Option

client = commands.Bot(command_prefix=".", help_command=None, intents=discord.Intents().all())

client.load_extension('ponto')

with open('config.json', 'r') as f:
    config = json.load(f)
    TOKEN = config['token']

@client.event
async def on_ready():
    print('Bot está online!')

@client.event
async def on_member_join(member: discord.Member):
    with open('config.json', 'r') as f:
        data = json.load(f)
    channel = client.get_channel(int(data["welcome_channel"]))
    embed = discord.Embed(title='Novo Membro!', description=f'Bem vindo ao servidor da CHOQUE {member.mention}!\n\n'
                          '• ⚠ Se registre em <#1148213667641446431>!')
    embed.set_footer(text='CHOQUE • 2023')
    cargo = member.guild.get_role(int(data["autorole"]))
    await member.add_roles(cargo)
    await channel.send(embed=embed)


@client.slash_command(description='Limpa mensagens do canal', guild_only=True)
async def clear(ctx: discord.ApplicationContext, 
                quantidade: Option(int, 'Insira a quantidade de mensagens a serem deletadas', required=True)):
    if not ctx.author.guild_permissions.manage_messages:
        return await ctx.respond(f'Você não tem permissão!\nPermissão necessária: `Gerenciar Mensagens`', delete_after=12.0)
    msgs = len(
        await ctx.channel.purge(limit=quantidade)
        )
    await ctx.respond(f'Foram deletadas {msgs} mensagens!', delete_after=8.0)

@client.slash_command(description='[ADM] Seta o canal de entrada', guild_only=True)
async def setar_entrada(ctx: discord.ApplicationContext, 
                        canal: Option(discord.TextChannel, 'Insira o canal de entrada', required=True)):
    if not ctx.author.guild_permissions.administrator:
        return await ctx.respond('Você não tem permissão!.\nPermissão necessária: `Administrador`', delete_after=12.0)
    with open('config.json', 'r') as f:
        data = json.load(f)
    data["welcome_channel"] = int(canal.id)
    with open('config.json', 'w') as f:
        json.dump(data, f, indent=4)
    await ctx.respond(f'Sucesso! Canal de entrada definido em: {canal.mention}', delete_after=10.0)

@client.slash_command(description='[ADM] Seta o cargo automático para quem entrar no discord', guild_only=True)
async def setar_autorole(ctx: discord.ApplicationContext, cargo: Option(discord.Role, 'Selecione o cargo', required=True)):
    if not ctx.author.guild_permissions.administrator:
        return await ctx.respond('Você não tem permissão!.\nPermissão necessária: `Administrador`', delete_after=12.0)
    with open('config.json', 'r') as f:
        data = json.load(f)
    data["autorole"] = int(cargo.id)
    with open('config.json', 'w') as f:
        json.dump(data, f, indent=4)
    await ctx.respond(f'Sucesso! Cargo inicial setado em {cargo.mention}', delete_after=10.0)

client.run(TOKEN)