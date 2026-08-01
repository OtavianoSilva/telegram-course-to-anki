# Curso do Telegram → Flashcards do Anki

Pipeline em 4 etapas que baixa as aulas em vídeo de um chat/canal do Telegram,
transcreve o conteúdo, gera flashcards com a IA e exporta tudo pra um `.apkg`
pronto pra importar no Anki.

```
1_baixar_telegram.py       -> baixa os vídeos + títulos das aulas
2_transcrever_videos.py    -> transcreve o áudio (Whisper local, offline)
2b_extrair_frames.py       -> (opcional) extrai frames pra pegar fórmulas/slides visuais
3_gerar_flashcards.py      -> gera flashcards com a API da Claude
4_exportar_anki.py         -> exporta pra flashcards_curso.apkg
```

## 1. Instalação

```bash
pip install -r requirements.txt
```

Também é preciso ter o **ffmpeg** instalado no sistema (não é pacote Python):

- Windows: `winget install ffmpeg` (ou baixe em ffmpeg.org)
- Mac: `brew install ffmpeg`
- Linux: `sudo apt install ffmpeg`

## 2. Configuração

1. Copie `.env.example` para `.env`.
2. Preencha `TELEGRAM_API_ID` e `TELEGRAM_API_HASH`, obtidos gratuitamente em
   https://my.telegram.org → "API development tools".
3. Preencha `TELEGRAM_CHAT` com o canal/grupo/chat onde estão os vídeos
   (username tipo `@meucurso`, link `https://t.me/meucurso`, ou o ID numérico).
4. Preencha `ANTHROPIC_API_KEY` com uma chave criada em
   https://console.anthropic.com/settings/keys

## 3. Rodando o pipeline

```bash
python 1_baixar_telegram.py
```
Na primeira execução vai pedir seu número de telefone e o código que o
Telegram te enviar — só acontece uma vez, depois fica salvo em
`sessao_curso.session`.

```bash
python 2_transcrever_videos.py
```
Roda o Whisper localmente (sem custo, mas usa CPU/GPU da sua máquina).
Para cursos longos, isso pode demorar — ele salva o progresso incrementalmente,
então pode parar e retomar a qualquer momento.

```bash
python 2b_extrair_frames.py
```
Opcional, mas recomendado se as aulas têm slides com fórmulas/gráficos que
não são só falados em voz alta.

```bash
python 3_gerar_flashcards.py
```
Chama a API da Claude uma vez por aula. Isso tem custo de API — dá uma olhada
nos preços do modelo em console.anthropic.com antes de rodar em um curso
grande. Ajuste a variável `MODELO` no script se quiser mais barato
(`claude-haiku-4-5-20251001`) ou mais caprichado (`claude-opus-4-8`).

```bash
python 4_exportar_anki.py
```
Gera `flashcards_curso.apkg`. Abra o Anki → **Arquivo → Importar** → selecione
esse arquivo. Cada aula vira um subbaralho dentro do baralho do curso.

## Observações

- **Uso pessoal**: isso foi desenhado pra estudo pessoal a partir de um curso
  que você já tem acesso. Não redistribua os vídeos, transcrições ou
  flashcards gerados.
- **Qualidade da transcrição**: o Whisper funciona bem com áudio em português
  claro; sotaques fortes, ruído de fundo ou termos técnicos muito específicos
  podem gerar erros pontuais — vale revisar os flashcards antes de estudar.
- **Fórmulas e conteúdo visual**: a transcrição de áudio não pega o que só
  aparece na tela. É por isso que o script `2b` existe — sem ele, fórmulas
  mostradas em slides mas não faladas em voz alta não viram flashcard.
- **Retomar do meio**: todos os scripts salvam progresso incrementalmente em
  arquivos JSON (`aulas_metadados.json`, `aulas_transcricoes.json`,
  `flashcards.json`), então você pode interromper e rodar de novo sem perder
  o que já foi processado.
- **Ajustando o prompt**: se os flashcards saírem muito genéricos, muito
  fáceis ou muito difíceis, edite o `PROMPT_SISTEMA` no
  `3_gerar_flashcards.py` — é o lugar mais fácil de ajustar o estilo.
