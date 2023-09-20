import datetime
import json
import discord
from discord.commands import Option
from discord.ext import commands
from discord.ui import View, InputText, Modal
from pytz import timezone


class BatePonto(commands.Cog):
    def __init__(self, client):
        self.client = client
    @commands.Cog.listener()
    async def on_ready(self):
        print('✅ Bate-Ponto carregado com sucesso!')
        self.client.add_view(view=batePonto())

    @commands.slash_command(description='Visualiza as pessoas que mais tem horas semanais', guild_only=True)
    async def ranking(self, ctx: discord.ApplicationContext, limit: Option(int, "Insira um limite para o ranking. (Padrão: 15)", default=15, name='limite')):
        with open('db.json', 'r') as f:
            data = json.load(f)

        bateponto = data["bateponto"]
        ranking = sorted(bateponto.items(), key=lambda i: i[1]["tempo_semanal"], reverse=True)
        ranking = ranking[:limit]
        embed = discord.Embed(title='Ranking - Horas Semanais', description='**Exibindo em ordem decrescente os oficiais com maior tempo de patrulha dessa semana.**\n\n')
        for num, i in enumerate(ranking, start=1):
            hr = int(i[1]["tempo_semanal"] // 3600)
            mins = int((i[1]["tempo_semanal"] % 3600) // 60)
            embed.description += f'> • {num}º: <@{i[0]}>: `{hr}h` - `{mins}m`\n'
        await ctx.respond(embed=embed)

    @commands.slash_command(description='[ADM] Gerencia o sistema do bate-ponto', guild_only=True)
    @commands.has_any_role(1148214580405874779)
    async def painel(self, ctx: discord.ApplicationContext):
        embed = discord.Embed(title='Bate-Ponto - STAFF', color=discord.Colour.gold(), description=f'**Gerenciamento do sistema de bate-ponto**\n\n'
                              '**•** `🔄 Reset Semanal`: Reseta as horas de todas as pessoas (nova semana)\n\n'
                              '**•** `➖ Reset Usuário`: Reseta as horas de um usuário especifíco\n\n'
                              '**•** `⚙ Modificar Usuário`: Modifica as horas semanais de alguém')
        embed.set_footer(text='CHOQUE • 2023', icon_url=self.client.user.display_avatar)
        await ctx.respond(embed=embed, view=painelBatePonto(ctx))

    @commands.slash_command(description='Consulta suas horas semanais', guild_only=True)
    async def consultar_horas(self, ctx, _user: Option(discord.Member, 'Selecione o usuário', required=False, name='usuário')):
        user = ctx.author if _user is None else _user
        total_secs = await bateponto_data_user(user.id)
        hr = int(total_secs["tempo_semanal"] // 3600)
        mins = int((total_secs["tempo_semanal"] % 3600) // 60)
        segundos = int(total_secs["tempo_semanal"] % 60)

        embed = discord.Embed(color=discord.Colour.gold(), 
                            description=f'**Exibindo tempo de bate-ponto semanal para o usuário: {user.mention}**\n\n'
                            f'**• Total de Horas: `{hr}`**\n**• Total de Minutos: `{mins}`**\n**• Total de Segundos: `{segundos}`**'
                            '\n\n**OBS:** Caso o usuário esteja com o bate-ponto aberto, o tempo acima pode não estar atualizado.')
        embed.set_author(name=f'Consultor de Horas semanais')
        embed.set_footer(text='CHOQUE • 2023', icon_url=self.client.user.display_avatar)
        await ctx.respond(embed=embed)

    @commands.slash_command()
    async def backup(self, ctx: commands.Context):
        if ctx.author.id == 402475992448237578:
            await ctx.reply(content='Backup atual:', file=discord.File('db.json'))
        else:
            await ctx.reply('❌ ERRO! Comando disponível apenas para desenvolvedores.')

    @commands.command()
    @commands.has_any_role(1148214580405874779)
    async def bateponto(self, ctx):
        embed = discord.Embed(title='Bate Ponto CHOQUE', color=discord.Colour.green(),
                              description='Sistema de bate-ponto da CHOQUE!\n\n'
                              '**→** Clique em `▶️ Começar` quando iniciar sua patrulha!\n\n'
                              '**→** Para consultar seu relatório de horas clique em `🔍Consultar Horas`!\n\n'
                              '**• OBS: Ao terminar sua patrulha, lembre-se de clicar em `⏹ Finalizar` em seu bate-ponto.**')
        embed.set_footer(text='CHOQUE • 2023', icon_url=self.client.user.display_avatar)
        await ctx.channel.send(embed=embed, view=batePonto())

class batePonto(View):
    def __init__(self):
        super().__init__(timeout=None)
        self._bateponto = {}   # Estrutura: {user_id: [unix_horario, message.id]}
    @discord.ui.button(label='Começar', emoji='▶️', style=discord.ButtonStyle.success, custom_id="button_start")
    async def start_callback(self, button, inter: discord.Interaction):
        if inter.user.id in self._bateponto:
            return await inter.response.send_message('⚠ Você já iniciou o seu bate-ponto!', ephemeral=True)
        await inter.response.defer()

        horario = int(datetime.datetime.now(timezone('America/Sao_Paulo')).timestamp())

        embed = discord.Embed(description=f'**→ 👮‍♂️ Oficial:** {inter.user.mention}\n\n'
                              f'**→ ⏰ Iniciado em:** <t:{horario}> (<t:{horario}:R>)\n\n'
                              '**❗ Quando encerrar sua patrulha, encerre o bate-ponto no botão abaixo**',
                              color=discord.Colour.green())
        embed.set_author(name=f'Bate-Ponto de {inter.user}', icon_url=inter.user.display_avatar)
        embed.set_footer(text='CHOQUE • 2023')
        msg = await inter.channel.send(embed=embed, view=finalizarPonto(self._bateponto))

        await bateponto_data_user(inter.user.id) # Criar o usuário no banco de dados, se não existir
        self._bateponto[inter.user.id] = [horario, msg.id]

    @discord.ui.button(label='Consultar Horas', emoji='🔍', style=discord.ButtonStyle.blurple, custom_id="button_consult")
    async def consult_callback(self, button, inter: discord.Interaction):
        total_secs = await bateponto_data_user(inter.user.id)
        hr = int(total_secs["tempo_semanal"] // 3600)
        mins = int((total_secs["tempo_semanal"] % 3600) // 60)
        segundos = int(total_secs["tempo_semanal"] % 60)

        embed = discord.Embed(color=discord.Colour.gold(), 
                            description=f'**Exibindo o seu tempo de bate-ponto semanal:**\n\n'
                            f'**• Total de Horas: `{hr}`**\n**• Total de Minutos: `{mins}`**\n**• Total de Segundos: `{segundos}`**'
                            '\n\n**OBS:** Caso você esteja com o bate-ponto aberto, o tempo acima pode não estar atualizado.')
        embed.set_author(name=f'Consultor de Horas semanais')
        embed.set_footer(text='CHOQUE • 2023')
        await inter.response.send_message(embed=embed, ephemeral=True)
        
class finalizarPonto(View):
    def __init__(self, controle_bateponto):
        super().__init__(timeout=None)
        self._bateponto = controle_bateponto

    @discord.ui.button(label='Finalizar', emoji='⏹', style=discord.ButtonStyle.danger)   # TODO: quem tiver cargo especifico, conseguir finalizar de qualquer pessoa
    async def end_callback(self, button, inter: discord.Interaction):
        cargo_adm = inter.guild.get_role(1148214580405874779)
        if cargo_adm in inter.user.roles:
            for k, v in self._bateponto.items():
                if v[1] == inter.message.id:
                    user_id = k
                    if inter.user.id != user_id and inter.message.id == self._bateponto[user_id][1]:
                        try:
                            self._bateponto.pop(user_id)
                            user = self.client.get_user(int(user_id))
                            await user.send(f'**⚠ AVISO:** Seu bate-ponto foi finalizado por: {inter.user.mention}!\nTome cuidado em deixar o bate-ponto aberto ao sair de patrulha. Em caso de dúvidas, procure o responsável por ter finalizado o seu ponto.\n\n**`OBS`:** Suas horas não serão contabilizadas. ')
                        except KeyError:
                            pass
                        await inter.message.delete()
                        return await inter.response.send_message(f'**Bate-ponto finalizado!** As horas não foram contabilizadas.', ephemeral=True)
                    break

        if inter.user.id not in self._bateponto:
            return
        if inter.message.id != self._bateponto[inter.user.id][1]:
            return
        
        msg = await inter.channel.fetch_message(self._bateponto[inter.user.id][1])
        await msg.delete()

        horario_inicio = self._bateponto[inter.user.id][0]
        horario_atual = int(datetime.datetime.now(timezone('America/Sao_Paulo')).timestamp())
        segundos_totais = horario_atual - horario_inicio
        horas, minutos = int(segundos_totais // 3600), int((segundos_totais % 3600) // 60)
        self._bateponto.pop(inter.user.id)

        with open('db.json', 'r+') as f:
            data = json.load(f)
            data["bateponto"][str(inter.user.id)]["tempo_semanal"] += segundos_totais
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()

        await inter.response.send_message(f'**✅ Bate-ponto fechado!**\nTempo total de PTR: `{horas}` horas e `{minutos}` minutos', ephemeral=True)

class batePontoModal(Modal):
    def __init__(self, ctx, change_hours: bool = False) -> None:
        super().__init__(title='Gerenciador Bate-Ponto', timeout=600)
        self.ctx = ctx
        self.change_hours = change_hours
        self.add_item(InputText(label='ID do discord do usuário:', style=discord.InputTextStyle.short, required=True))
        if self.change_hours:
            self.add_item(InputText(label='Insira as novas horas semanais:', placeholder='Insira o novo valor em horas', style=discord.InputTextStyle.short, required=True))
    async def callback(self, inter: discord.Interaction):
        if self.ctx.author != inter.user:
            return
        if self.change_hours:
            if not (self.children[0].value).isdigit() or not (self.children[1].value).isdigit():
                return await inter.response.send_message('**❌ ERRO!** Insira apenas números!')
        else:
            if not (self.children[0].value).isdigit():
                return await inter.response.send_message('**❌ ERRO!** Insira apenas números!')
        

        with open('db.json', 'r+') as f:
            data = json.load(f)
            if self.children[0].value not in data["bateponto"]:
                return await inter.response.send_message('**❌ ERRO!** Esse usuário ainda não está cadastrado no bate-ponto.')
            try:
                data["bateponto"][self.children[0].value]["tempo_semanal"] = 0 if not self.change_hours else (int(self.children[1].value) * 60 * 60)
            except KeyError:
                return await inter.response.send_message('**❌ ERRO!** Você digitou um ID inválido')
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()
            member = inter.guild.get_member(int(self.children[0].value))
            await inter.response.send_message(f'**✅ Sucesso!** Agora o usuário {member.mention} possui {self.children[1].value} horas trabalhadas!')

            
class painelBatePonto(View):
    def __init__(self, ctx) -> None:
        super().__init__(timeout=None)
        self.ctx = ctx
    @discord.ui.button(label='Reset Semanal', emoji='🔄', style=discord.ButtonStyle.blurple)
    async def reset_sem_callback(self, button, inter: discord.Interaction):
        if inter.user.id != self.ctx.author.id:
            return
        await inter.response.defer()

        with open('db.json', 'r+') as f:
            data = json.load(f)
            for i in data["bateponto"].values():
                i["tempo_semanal"] = 0
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()
        
        await inter.followup.send(f'✅ Sucesso! Você resetou a carga horária semanal de {len(data["bateponto"])} oficiais!')
    
    @discord.ui.button(label='Reset Usuário', emoji='➖', style=discord.ButtonStyle.blurple)
    async def reset_user_callback(self, button, inter: discord.Interaction):
        if inter.user.id != self.ctx.author.id:
            return
    
        await inter.response.send_modal(batePontoModal(self.ctx))    

    @discord.ui.button(label='Modificar Usuário', emoji='⚙', style=discord.ButtonStyle.blurple)
    async def modify_user_callback(self, button, inter: discord.Interaction):
        if inter.user.id != self.ctx.author.id:
            return
        
        await inter.response.send_modal(batePontoModal(self.ctx, change_hours=True))


async def bateponto_data_user(user_id):
    with open('db.json', 'r') as f:
        data = json.load(f)

    user_id = str(user_id)

    if user_id in data["bateponto"]:
        return data["bateponto"][user_id]
    
    data["bateponto"].setdefault(
        user_id,
        {"tempo_semanal": 0}
    )
    with open('db.json', 'w') as f:
        json.dump(data, f, indent=4)

    return data["bateponto"][user_id]


def setup(client):
    client.add_cog(BatePonto(client))