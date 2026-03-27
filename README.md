# 🌐 Monitoramento de Uptime de Rede

Aplicativo Python + Streamlit para monitoramento de disponibilidade de equipamentos de rede via ping.

## 📋 Recursos

- ✅ **Monitoramento Multi-IP**: Monitore múltiplos equipamentos simultaneamente
- 📊 **Estatísticas em Tempo Real**: Visualize uptime percentual e histórico de cada equipamento
- 📈 **Gráficos de Disponibilidade**: Histórico visual das últimas 24 horas
- ⚠️ **Alertas de Falha**: Notificações visuais e sonoras quando equipamentos ficam offline
- 🖱️ **Keep-Alive**: Movimento automático do mouse para evitar hibernação do notebook
- 💾 **Persistência de Dados**: Salve e carregue sessões de monitoramento
- 📄 **Relatórios TXT**: Exporte relatórios completos com estatísticas e timeline de eventos
- 🕒 **Histórico de 7 Dias**: Mantém dados históricos dos últimos 7 dias

## ⚙️ Requisitos

### Sistema Operacional
- Windows 10/11 (recomendado)
- Linux (com adaptações)
- macOS (com adaptações)

### Python
- Python 3.8 ou superior

### Privilégios Administrativos (Windows)

⚠️ **IMPORTANTE**: No Windows, o comando `ping` via ICMP pode requerer privilégios administrativos dependendo da configuração de segurança do sistema.

**Recomendações:**

1. **Execute como Administrador** (método mais simples):
   - Clique com botão direito no terminal (PowerShell ou CMD)
   - Selecione "Executar como Administrador"
   - Execute o aplicativo normalmente

2. **Configure permissões de firewall**:
   - Abra "Windows Defender Firewall com Segurança Avançada"
   - Verifique regras de entrada/saída para ICMP Echo Request
   - Habilite se necessário

3. **Alternativa sem privilégios**:
   - O aplicativo tenta usar `subprocess` com o comando nativo `ping` do sistema
   - Em alguns casos, funciona sem privilégios elevados
   - Se não funcionar, execute como administrador

## 🚀 Instalação

### 1. Clone ou baixe o repositório

```bash
git clone <url-do-repositorio>
cd PingTest
```

### 2. Instale as dependências

```bash
pip install -r requirements.txt
```

**Dependências incluídas:**
- `streamlit`: Framework web para interface
- `pyautogui`: Controle de mouse para keep-alive
- `pandas`: Manipulação de dados para gráficos
- `pyinstaller`: Criação de executável (opcional)

## 🎮 Como Usar

### Executar o aplicativo

```bash
streamlit run app.py
```

O aplicativo abrirá automaticamente no navegador padrão em `http://localhost:8501`

### Interface

#### Sidebar (Configurações)

1. **📥 Carregar Estado Salvo**: Restaura sessão anterior salva
2. **🌐 Endereços IP**: Digite os IPs a monitorar (um por linha)
   - Exemplo:
     ```
     8.8.8.8
     1.1.1.1
     192.168.1.1
     ```
3. **⏱️ Intervalos**:
   - **Intervalo entre pings**: Tempo de espera entre cada ping (1-60s)
   - **Intervalo de movimento do mouse**: Frequência do keep-alive (10-300s)
   - **Intervalo de atualização da interface**: Frequência de refresh da tela (1-30s)

4. **🎮 Controles**:
   - **▶️ Iniciar**: Começa o monitoramento
   - **⏹️ Parar**: Para o monitoramento
   - **🖱️ Ativar/Desativar Keep-Alive**: Liga/desliga movimento do mouse
   - **💾 Salvar Estado**: Salva sessão atual
   - **🗑️ Limpar Histórico**: Remove dados históricos

#### Painel Principal

1. **Status**: Mostra estado do monitoramento e keep-alive
2. **📊 Métricas por Equipamento**: Cards com estatísticas de cada IP
   - Status atual (🟢 Online / 🔴 Offline)
   - Uptime percentual
   - Total de pings e sucessos/falhas
3. **📈 Gráficos**: Histórico visual de disponibilidade (24h)
4. **⚠️ Alertas Ativos**: Lista de equipamentos offline
5. **📄 Relatório**: Botão para exportar relatório TXT
6. **📋 Logs em Tempo Real**: Últimos 20 eventos

### Exportar Relatório

1. Clique no botão "📥 Exportar Relatório"
2. Clique em "⬇️ Download TXT"
3. O relatório será baixado com nome: `relatorio_uptime_YYYYMMDD_HHMMSS.txt`

**Conteúdo do relatório:**
- Período do teste
- Configurações utilizadas
- Resumo geral (IPs monitorados, disponibilidade média)
- Detalhes por equipamento (status, uptime, tempos)
- Timeline de eventos críticos (falhas e recuperações)

## 📁 Estrutura de Arquivos

```
PingTest/
├── app.py                    # Aplicativo principal Streamlit
├── ping_monitor.py           # Módulo de monitoramento de ping
├── alert_manager.py          # Gerenciador de alertas
├── state_manager.py          # Persistência de estado
├── keep_alive.py             # Keep-alive do sistema
├── report_generator.py       # Gerador de relatórios
├── requirements.txt          # Dependências Python
├── README.md                 # Este arquivo
├── build_exe.spec            # Configuração PyInstaller
└── monitoring_state.json     # Estado salvo (gerado automaticamente)
```

## 🔧 Configurações Avançadas

### Timeout de Ping

O timeout de ping é fixo em **2 segundos**. Para modificar:

Edite [ping_monitor.py](ping_monitor.py#L24):
```python
self.timeout = 2  # Altere para o valor desejado
```

### Retenção de Histórico

O histórico é mantido por **7 dias**. Para modificar:

Edite [app.py](app.py#L63):
```python
st.session_state.state_manager = StateManager(history_days=7)  # Altere aqui
```

### Som de Alerta

Alertas sonoros usam `winsound.Beep(1000, 500)` no Windows.

Para modificar frequência/duração, edite [alert_manager.py](alert_manager.py#L84):
```python
winsound.Beep(1000, 500)  # (frequência_Hz, duração_ms)
```

## 🏗️ Criar Executável

Para gerar um executável standalone:

```bash
pyinstaller build_exe.spec
```

O executável será gerado em `dist/PingTest.exe`

**Nota**: Executáveis Streamlit podem ser grandes (~200-300 MB) devido às dependências.

## ❓ Solução de Problemas

### Pings sempre falham
- ✅ Execute como Administrador
- ✅ Verifique firewall do Windows
- ✅ Teste ping manualmente no CMD: `ping 8.8.8.8`

### Keep-Alive não funciona
- ✅ Instale `pyautogui` corretamente: `pip install pyautogui`
- ✅ No Linux, pode precisar de `python3-tk`: `sudo apt install python3-tk`

### Interface não atualiza
- ✅ Verifique "Intervalo de atualização da interface"
- ✅ Certifique-se que o monitoramento está ativo (▶️)

### Erro ao salvar estado
- ✅ Verifique permissões de escrita na pasta
- ✅ Certifique-se que não há outro processo usando `monitoring_state.json`

## 📝 Changelog

### v1.0 (2026-03-26)
- ✅ Lançamento inicial
- ✅ Monitoramento multi-IP via ping
- ✅ Alertas visuais e sonoros
- ✅ Keep-alive com movimento de mouse
- ✅ Gráficos de disponibilidade
- ✅ Persistência de dados (7 dias)
- ✅ Exportação de relatórios TXT
- ✅ Interface web Streamlit

## 📄 Licença

Este projeto é de código aberto. Sinta-se livre para usar e modificar conforme necessário.

## 🤝 Contribuições

Contribuições são bem-vindas! Abra issues ou pull requests no repositório.

## 📧 Suporte

Para problemas ou dúvidas, abra uma issue no repositório do projeto.

---

**Desenvolvido com ❤️ usando Python + Streamlit**
