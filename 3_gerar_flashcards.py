"""
Script 3: Usa a API da Anthropic (Claude) para gerar flashcards a partir da transcrição
(e, opcionalmente, dos frames visuais) de cada aula.

Requer uma chave de API em ANTHROPIC_API_KEY (arquivo .env ou variável de ambiente).
Crie uma chave em: https://console.anthropic.com/settings/keys

Custo: isso faz 1 chamada de API por aula. Para um curso com muitas aulas longas,
verifique os preços do modelo escolhido no console da Anthropic antes de rodar tudo.
"""
import os
import json
import base64
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

ARQUIVO_TRANSCRICOES = "aulas_transcricoes.json"
ARQUIVO_FLASHCARDS = "flashcards.json"
PASTA_FRAMES = "frames_temp"          # gerado pelo script 2b (opcional)
MAX_FRAMES_POR_AULA = 6               # limite pra não estourar tamanho da requisição

# Modelos disponíveis: claude-haiku-4-5-20251001 (mais rápido/barato),
# claude-sonnet-5 (equilíbrio, recomendado), claude-opus-4-8 (mais caro/capaz)
MODELO = "claude-sonnet-5"

client = Anthropic()  # usa ANTHROPIC_API_KEY do ambiente automaticamente

PROMPT_SISTEMA = """Você é um assistente que cria flashcards de estudo (pergunta/resposta)
a partir da transcrição de uma aula em vídeo, e opcionalmente de imagens de slides da aula.

Regras:
- Crie entre 5 e 15 flashcards por aula, dependendo da densidade de conteúdo (não invente
  conteúdo que não apareceu na aula).
- Cada flashcard cobre UM conceito, definição, fórmula ou fato específico (não misture vários).
- Perguntas claras e objetivas, sem ambiguidade.
- Respostas curtas e diretas, ideais para revisão espaçada (estilo Anki).
- Se houver fórmulas matemáticas nas imagens ou na fala, inclua-as em texto simples ou LaTeX
  entre $ $, em flashcards próprios (frente = quando/o que é a fórmula, verso = a fórmula e
  o que cada termo significa).
- Não crie flashcards genéricos ("o que foi discutido na aula?").
- Responda APENAS com um JSON válido, nesse formato exato, sem markdown nem texto adicional:
[{"frente": "pergunta", "verso": "resposta"}, ...]
"""


def carregar_frames(aula_id):
    pasta = os.path.join(PASTA_FRAMES, str(aula_id))
    if not os.path.isdir(pasta):
        return None
    imagens = []
    for nome in sorted(os.listdir(pasta))[:MAX_FRAMES_POR_AULA]:
        with open(os.path.join(pasta, nome), "rb") as f:
            imagens.append(base64.b64encode(f.read()).decode("utf-8"))
    return imagens or None


def gerar_flashcards_aula(titulo, transcricao, frames_base64=None):
    conteudo = [{"type": "text", "text": f"Título da aula: {titulo}\n\nTranscrição:\n{transcricao}"}]

    if frames_base64:
        conteudo.append({
            "type": "text",
            "text": "\nImagens de slides/tela extraídas da aula (podem conter fórmulas, "
                    "gráficos e textos que não foram falados em voz alta):",
        })
        for img_b64 in frames_base64:
            conteudo.append({
                "type": "image",
                "source": {"type": "base64", "media_type": "image/jpeg", "data": img_b64},
            })

    resposta = client.messages.create(
        model=MODELO,
        max_tokens=4000,
        system=PROMPT_SISTEMA,
        messages=[{"role": "user", "content": conteudo}],
    )

    texto = resposta.content[0].text.strip()
    texto = texto.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(texto)
    except json.JSONDecodeError:
        print(f"  Aviso: não consegui interpretar o JSON da aula '{titulo}'. Pulando.")
        return []


def main():
    with open(ARQUIVO_TRANSCRICOES, "r", encoding="utf-8") as f:
        aulas = json.load(f)

    for aula in aulas:
        if aula.get("flashcards"):
            continue
        if not aula.get("transcricao"):
            print(f"Aula '{aula['titulo']}' sem transcrição, pulando.")
            continue

        print(f"Gerando flashcards: {aula['titulo']}")
        frames = carregar_frames(aula["id"])
        aula["flashcards"] = gerar_flashcards_aula(aula["titulo"], aula["transcricao"], frames)

        with open(ARQUIVO_FLASHCARDS, "w", encoding="utf-8") as f:
            json.dump(aulas, f, ensure_ascii=False, indent=2)

    total = sum(len(a.get("flashcards", [])) for a in aulas)
    print(f"\nConcluído! {total} flashcards gerados em {ARQUIVO_FLASHCARDS}")


if __name__ == "__main__":
    main()
