"""
Script 4: Exporta os flashcards gerados para um arquivo .apkg pronto para importar no Anki.

Cada aula vira um subbaralho dentro do baralho principal do curso
(ex: "Meu Curso::Aula 1 - Introdução"), então no Anki você pode estudar
por aula ou o curso inteiro de uma vez.
"""
import json
import genanki

ARQUIVO_FLASHCARDS = "flashcards.json"
NOME_CURSO = "Meu Curso"          # <-- ajuste para o nome do seu curso
ARQUIVO_SAIDA = "flashcards_curso.apkg"

# IDs fixos (não mude entre exportações, ou o Anki pode tratar como baralho/modelo novo)
MODEL_ID = 1607392319
DECK_ID_BASE = 2059400110

modelo = genanki.Model(
    MODEL_ID,
    "Modelo Simples Curso",
    fields=[{"name": "Frente"}, {"name": "Verso"}],
    templates=[
        {
            "name": "Cartão 1",
            "qfmt": "{{Frente}}",
            "afmt": '{{FrontSide}}<hr id="answer">{{Verso}}',
        },
    ],
)


def deck_id_para(nome):
    # gera um ID estável (determinístico) a partir do nome do baralho
    return DECK_ID_BASE + (abs(hash(nome)) % 1_000_000)


def main():
    with open(ARQUIVO_FLASHCARDS, "r", encoding="utf-8") as f:
        aulas = json.load(f)

    decks = {}
    total_cards = 0

    for aula in aulas:
        titulo_aula = (aula.get("titulo") or f"Aula {aula['id']}").strip()
        # Anki usa "::" para hierarquia de subbaralhos
        titulo_aula_limpo = titulo_aula.replace("::", "-")
        nome_subdeck = f"{NOME_CURSO}::{titulo_aula_limpo}"

        cards = aula.get("flashcards", [])
        if not cards:
            continue

        if nome_subdeck not in decks:
            decks[nome_subdeck] = genanki.Deck(deck_id_para(nome_subdeck), nome_subdeck)

        for card in cards:
            nota = genanki.Note(model=modelo, fields=[card["frente"], card["verso"]])
            decks[nome_subdeck].add_note(nota)
            total_cards += 1

    if not decks:
        print("Nenhum flashcard encontrado em", ARQUIVO_FLASHCARDS)
        return

    pacote = genanki.Package(list(decks.values()))
    pacote.write_to_file(ARQUIVO_SAIDA)

    print(f"Arquivo gerado: {ARQUIVO_SAIDA}")
    print(f"{total_cards} flashcards em {len(decks)} sub-baralhos.")
    print("No Anki: Arquivo > Importar... e selecione esse .apkg.")


if __name__ == "__main__":
    main()
