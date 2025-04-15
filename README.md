# 🤖 Bot de Gerenciamento para RP (FiveM/MTA) no Discord

Eu desenvolvi este bot em 2023 exclusivamente para o servidor de roleplay chamado **Brazza**, com o objetivo de facilitar o trabalho da Staff do servidor, e melhorar a experiência dos usuários, especialmente no controle de promoções/rebaixamentos dentro da polícia.<br>
> **⚠️ O servidor Brazza não está mais em atividade, e não tenho qualquer vínculo com marcas que levem esse nome. Fui autorizado a tornar este projeto público para que outros possam utilizá-lo e adaptá-lo.**

Apesar de ter sido feito para um servidor específico, fiz uma atualização e tornei o bot mais personalizável através do arquivo `config.json`.


## 📋 Funcionalidades
- ⏰ Registro de entrada e saída de patrulha
- 📊 Contabilização automática de horas trabalhadas
- 🏆 Ranking de horas
- 📝 Histórico detalhado de pontos
- 🚔 Geração automática de relatórios de prisão (com suporte a foto)
- ⚙️ Painel de controle para staff
- ➕ Adição/Remoção manual de horas
- 🔄 Reset semanal de horas
- 🎭 Sistema de cargos automáticos
- 📢 Sistema de boas-vindas personalizado
- 📄 Logs detalhados de todas as ações relevantes
> **🧠 Recomenda-se utilizar o bot em apenas um servidor por vez, pois ele foi desenvolvido para funcionar em uma única instância. Em múltiplos servidores, podem ocorrer conflitos.**

## 🚀 Instalação
### Pré-requisitos
- Python 3.8 ou superior
- Um bot criado no [Portal de Desenvolvedores do Discord](https://discord.com/developers/applications)

### Passo a Passo
1. Clone o repositório:
```bash
git clone https://github.com/mtzdev/bate-ponto-bot.git
cd bate-ponto-bot
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure o arquivo `config.json`:
```bash
{
    "server_name": "Nome do Seu Servidor",
    "token": "Token do bot do Discord",
    "welcome_channel": ID_CANAL_BOAS_VINDAS,
    "autorole": ID_CARGO_AUTOMATICO,
    "owner_id": SEU_ID_DISCORD,
    "log_channel_id": ID_CANAL_LOGS,
    "staff_role_id": ID_CARGO_STAFF,
    "server_ip": "IP_DO_SERVIDOR:PORTA"
}
```

4. Execute o bot:
```bash
python main.py
```

## 📝 Principais Comandos
### Comandos Gerais
- `/consultar_horas` - Verifica suas horas semanais
- `/ranking` - Exibe o ranking de horas
- `/pontos` - Exibe o seu histórico de pontos
- `/prisao` - Gera um relatório de prisão
- `/players` - Verifica quantidade de jogadores online no servidor

### Comandos Staff
- `.bateponto` - Mensagem padrão do sistema de bate-ponto
- `/addtempo` - Adiciona horas para um policial
- `/deltempo` - Remove horas de um policial
- `/painel` - Abre o painel de gerenciamento do bate-ponto
- `/embed` - Cria uma mensagem embed personalizada
- `/setar_ip` - Seta o IP do servidor do FiveM
- `/setar_entrada` - Define o canal que será enviada a mensagem de boas-vindas
- `/setar_autorole` - Define o cargo que os usuários ganharam ao entrar no servidor

## 🔧 Suporte
Esse foi um projeto exclusivo para um servidor servidor, portanto **não será prestado suporte oficial**.<br>
No entanto, se tiver dúvidas específicas sobre o funcionamento, pode me chamar no Discord: **@mtz._**

## ⚠️ Observações
- Sinta-se livre para modificar e utilizar o bot como quiser.
- Bugs podem existir, já que ele foi feito para atender as demandas específicas de um antigo servidor.
- O bot foi utilizado ativamente durante 1 ano, contendo diversos comandos úteis, bem estruturados e testados na prática.
- Ideal para servidores de roleplay que querem um sistema eficiente de gerenciamento de bate-ponto com várias funcionalidades de fácil uso.
