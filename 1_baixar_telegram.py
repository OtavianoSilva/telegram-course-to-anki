"""
Script 1: Conecta ao Telegram e baixa todos os vídeos de um canal/grupo/chat específico.

Requer TELEGRAM_API_ID e TELEGRAM_API_HASH, obtidos gratuitamente em:
https://my.telegram.org -> "API development tools"

Na primeira execução, o Telethon vai pedir seu número de telefone e o código
que o Telegram enviar (só acontece uma vez, depois fica salvo em sessao_curso.session).
"""
import os
import asyncio
import json
from telethon import TelegramClient
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("TELEGRAM_API_ID"))
API_HASH = os.getenv("TELEGRAM_API_HASH")
CHAT = os.getenv("TELEGRAM_CHAT")  # username (@canal), link (t.me/...) ou ID numérico do chat/canal/grupo

PASTA_VIDEOS = "videos_curso"
ARQUIVO_METADADOS = "aulas_metadados.json"

os.makedirs(PASTA_VIDEOS, exist_ok=True)


def get_filename(message):
    if message.file and message.file.name:
        return message.file.name
    return f"aula_{message.id}.mp4"


def eh_video(message):
    if message.video:
        return True
    if message.document and message.document.mime_type and "video" in message.document.mime_type:
        return True
    return False


async def main():
    client = TelegramClient("sessao_curso", API_ID, API_HASH)
    await client.start()

    print(f"Conectado. Buscando mensagens em: {CHAT}")
    entity = await client.get_entity(CHAT)

    # Carrega metadados já existentes (permite retomar sem baixar tudo de novo)
    aulas = []
    if os.path.exists(ARQUIVO_METADADOS):
        with open(ARQUIVO_METADADOS, "r", encoding="utf-8") as f:
            aulas = json.load(f)
    ids_existentes = {a["id"] for a in aulas}

    # reverse=True -> percorre do mais antigo pro mais novo (ordem cronológica do curso)
    async for message in client.iter_messages(entity, reverse=True):
        if not eh_video(message):
            continue
        if message.id in ids_existentes:
            continue

        nome_arquivo = get_filename(message)
        caminho = os.path.join(PASTA_VIDEOS, f"{message.id}_{nome_arquivo}")

        print(f"Baixando: {nome_arquivo} (msg id {message.id})")
        try:
            await client.download_media(message, file=caminho)
        except Exception as e:
            print(f"  Falhou ao baixar msg {message.id}: {e}")
            continue

        aulas.append({
            "id": message.id,
            "titulo": (message.text or nome_arquivo).strip(),
            "arquivo": caminho,
            "data": str(message.date),
        })

        # salva incrementalmente, pra não perder progresso se cair a conexão
        with open(ARQUIVO_METADADOS, "w", encoding="utf-8") as f:
            json.dump(aulas, f, ensure_ascii=False, indent=2)

    print(f"\nConcluído! {len(aulas)} aulas no total. Metadados em {ARQUIVO_METADADOS}")


if __name__ == "__main__":
    asyncio.run(main())
