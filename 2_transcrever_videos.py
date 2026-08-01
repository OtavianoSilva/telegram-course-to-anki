"""
Script 2: Extrai o áudio dos vídeos baixados e transcreve com Whisper (roda local, offline, sem custo de API).

Requer ffmpeg instalado no sistema (não é pacote Python):
  - Windows: https://ffmpeg.org/download.html (ou "winget install ffmpeg")
  - Mac: brew install ffmpeg
  - Linux: sudo apt install ffmpeg
"""
import os
import json
import subprocess
from faster_whisper import WhisperModel

ARQUIVO_METADADOS = "aulas_metadados.json"
PASTA_AUDIO = "audio_temp"
ARQUIVO_TRANSCRICOES = "aulas_transcricoes.json"

# Modelos disponíveis (do mais rápido/impreciso ao mais lento/preciso):
# tiny, base, small, medium, large-v3
# "small" é um bom equilíbrio pra começar; troque para "medium" se tiver GPU ou paciência
MODELO = "small"
DEVICE = "cpu"          # troque para "cuda" se tiver GPU NVIDIA
COMPUTE_TYPE = "int8"   # com GPU, use "float16"

os.makedirs(PASTA_AUDIO, exist_ok=True)


def extrair_audio(video_path, audio_path):
    if os.path.exists(audio_path):
        return
    subprocess.run(
        ["ffmpeg", "-y", "-i", video_path, "-vn", "-ac", "1", "-ar", "16000", audio_path],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )


def main():
    with open(ARQUIVO_METADADOS, "r", encoding="utf-8") as f:
        aulas = json.load(f)

    # retoma de onde parou, se o arquivo já existir
    if os.path.exists(ARQUIVO_TRANSCRICOES):
        with open(ARQUIVO_TRANSCRICOES, "r", encoding="utf-8") as f:
            aulas_salvas = {a["id"]: a for a in json.load(f)}
        for aula in aulas:
            if aula["id"] in aulas_salvas:
                aula["transcricao"] = aulas_salvas[aula["id"]].get("transcricao")

    print("Carregando modelo Whisper (pode demorar na primeira vez, baixa o modelo)...")
    model = WhisperModel(MODELO, device=DEVICE, compute_type=COMPUTE_TYPE)

    for aula in aulas:
        if aula.get("transcricao"):
            continue

        video_path = aula["arquivo"]
        audio_path = os.path.join(PASTA_AUDIO, f"{aula['id']}.wav")

        print(f"Processando: {aula['titulo']}")
        try:
            extrair_audio(video_path, audio_path)
            segments, _info = model.transcribe(audio_path, language="pt")
            aula["transcricao"] = " ".join(seg.text.strip() for seg in segments)
        except Exception as e:
            print(f"  Erro ao processar '{aula['titulo']}': {e}")
            aula["transcricao"] = ""

        with open(ARQUIVO_TRANSCRICOES, "w", encoding="utf-8") as f:
            json.dump(aulas, f, ensure_ascii=False, indent=2)

    print(f"\nConcluído! Transcrições salvas em {ARQUIVO_TRANSCRICOES}")


if __name__ == "__main__":
    main()
