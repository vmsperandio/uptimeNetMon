# PingTest - Instruções Rápidas

## Instalação

```bash
pip install -r requirements.txt
```

## Executar

```bash
streamlit run app.py
```

## Criar Executável

```bash
pyinstaller build_exe.spec
```

Executável gerado em: `dist/PingTest/PingTest.exe`

## Uso Rápido

1. Digite os IPs no sidebar (um por linha)
2. Clique em "▶️ Iniciar" para começar o monitoramento
3. (Opcional) Clique em "🖱️ Ativar Keep-Alive" para evitar hibernação
4. Monitore as métricas em tempo real
5. Exporte relatórios com o botão "📥 Exportar Relatório"

## Importante

⚠️ No Windows, execute como Administrador para funcionamento correto dos pings ICMP.
