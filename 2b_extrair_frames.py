"""
Script 2b (OPCIONAL, mas recomendado): Extrai frames dos vídeos em intervalos regulares.

Por quê? A transcrição de áudio (script 2) só pega o que foi FALADO.
Se a aula tem slides com fórmulas, gráficos ou textos que o professor não lê em voz alta,
isso se perde. Extraindo alguns frames por aula e passando pro Claude junto com a
transcrição (script 3), o conteúdo visual também vira flashcard.

Requer ffmpeg (mesmo do script 2).
"""
import os
import json
import subprocess

ARQUIVO_METADADOS = "aulas_metadados.json"
PASTA_FRAMES = "frames_temp"

# Extrai 1 frame a cada N segundos. Para aulas de ~20-40min, 45-60s costuma
# ser suficiente pra capturar as trocas de slide sem gerar frames demais.
INTERVALO_SEGUNDOS = 45


def main():
    with open(ARQUIVO_METADADOS, "r", encoding="utf-8") as f:
        aulas = json.load(f)

    for aula in aulas:
        pasta_aula = os.path.join(PASTA_FRAMES, str(aula["id"]))
        if os.path.isdir(pasta_aula) and os.listdir(pasta_aula):
            continue
        os.makedirs(pasta_aula, exist_ok=True)

        print(f"Extraindo frames: {aula['titulo']}")
        try:
            subprocess.run(
                [
                    "ffmpeg", "-y", "-i", aula["arquivo"],
                    "-vf", f"fps=1/{INTERVALO_SEGUNDOS}",
                    "-qscale:v", "3",
                    os.path.join(pasta_aula, "frame_%03d.jpg"),
                ],
                check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
        except subprocess.CalledProcessError as e:
            print(f"  Falhou em '{aula['titulo']}': {e}")

    print("Concluído! Frames extraídos em", PASTA_FRAMES)


if __name__ == "__main__":
    main()
