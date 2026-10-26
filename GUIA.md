# Guia editorial — Instagram @allcleantech

Este guia orienta a produção semanal dos posts. Ele vale para quem gera o conteúdo (o Claude, na tarefa agendada) e para quem valida (Daniel).

## Rotina

- **Quinta-feira, à tarde:** a tarefa agendada prepara os 5 posts da semana seguinte (segunda a sexta, às 10h, horário de Brasília) e deixa todos como **rascunho** no Metricool.
- **Daniel valida** no Metricool: abre cada rascunho, ajusta se quiser e muda de rascunho para agendado. Nada é publicado sem essa aprovação.
- **Mídias novas:** fotos e vídeos vão para a pasta `entrada/`. Depois de usados, são movidos para `usado/`.
- Se a `entrada/` estiver vazia, os posts saem como carrossel só com arte (sem foto).

## Pilares de conteúdo (rodízio da semana)

| Dia | Pilar | Ângulo |
|---|---|---|
| Segunda | Causa raiz | Umidade, oxidação e falhas elétricas; riscos escondidos da lavagem com água |
| Terça | Automação e mão de obra | Fim da escala 6x1, falta de mão de obra, limpeza automática de esteiras |
| Quarta | Água e ETE | Menos água, menos efluente para tratar, sustentabilidade |
| Quinta | Segurança de alimentos | Higienização, boas práticas de fabricação, auditorias |
| Sexta | Produto em ação | Vídeos e fotos reais do sistema funcionando; novidades |

Alternar formatos: Reel quando houver vídeo bom na `entrada/`; carrossel quando o tema pede explicação.

## Regras que não mudam

1. **Privacidade dos clientes:** nunca mostrar rostos, nomes, logos ou produtos de clientes. Nunca mostrar a máquina com **IHM** nem telas de painel. Sem áudio original (pode ter vozes): Reels saem sem som.
2. **Fatos verificados:** toda informação factual precisa de **três fontes independentes**. As fontes aparecem na legenda ou no rodapé da tela.
3. **Sem números inventados:** porcentagens de economia de água, tempo ou custo só entram com dados reais fornecidos pela AllCleantech.
4. **Sem afirmar o que o vídeo não mostra:** se a imagem mostra piso molhado, não usar com mensagem de "mínimo de água" (recortar ou trocar a cena).
5. **Logo:** sempre na tela final (`marca/logo-allcleantech.png`).
6. **Tom:** direto, técnico, voltado a gestores de indústria (manutenção, produção, qualidade). Português do Brasil.

## Identidade visual

- Fundo verde-escuro `#061609`; destaque verde `#22A447` (selos) e `#5BEA85` (palavras em destaque).
- Títulos em Archivo extra-negrito; textos em Inter.
- Carrossel 1080×1350; Reel 1080×1920 com barra de progresso no topo.
- Gerador: `python3 ferramentas/render.py roteiro.json` (exemplos de roteiro no topo do arquivo).

## Fatos já verificados (usar com as fontes)

- **Fim da escala 6x1:** PEC aprovada pelo Senado em outubro de 2026 (75 a 1) e promulgada em 16/10/2026. Jornada cai de 44h para 42h cerca de 60 dias após a promulgação (dezembro de 2026), com duas folgas semanais e sem redução de salário; depois cai para 40h. Fontes: Forbes Brasil, meutudo, Trabalhista.blog, Portal de Prefeitura.
- **Umidade e falhas elétricas:** a umidade oxida conexões, aumenta a resistência e gera calor, podendo levar a arco e incêndio. Fontes: Technical Safety BC, Schneider Electric, O Setor Elétrico, NAFE.
- **Lavagem em plantas de alimentos:** a entrada de líquido é causa frequente de falhas elétricas em áreas de lavagem. Fontes: Wesco/ABB, CHINT, Parker.

## Hashtags base

#AllCleantech #LimpezaAVapor #IndústriaDeAlimentos #Automação #ManutençãoIndustrial #Sustentabilidade (mais 3 a 5 específicas do tema).
