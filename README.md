# French drills

Small static drills for French, hosted on GitHub Pages. Mistakes come back until you get them right
twice, and progress is stored in your browser only. Every item has a "Report a problem" link that opens a
prefilled GitHub issue.

| Page | What it drills | Data |
| --- | --- | --- |
| `imparfait.html` | Imparfait or passé composé | Tatoeba, `scripts/build_data.py` |
| `prepositions.html` | À or de after a verb or expression | Tatoeba, `scripts/build_prepositions.py` |
| `si.html` | Si + imparfait → conditionnel présent | Tatoeba, `scripts/build_si.py` |
| `connecteurs.html` | Connectors in model TCF writing answers | written here, `scripts/build_connecteurs.py` |
| `edito.html` | Review drills for *Édito B2* grammar and vocabulary lessons | written here, `scripts/build_edito.py` |

`drill.js` is the shared engine for every page except the imparfait drill (`app.js`). Its item format is
documented at the top of the file.

## Running locally

```bash
python3 -m http.server 8765
```

Then open http://localhost:8765.

## Rebuilding the data

The Tatoeba-based scripts need these files downloaded and unpacked into one folder, passed as the first
argument (`python3 scripts/build_prepositions.py THAT_FOLDER`):

- https://downloads.tatoeba.org/exports/per_language/fra/fra_sentences_detailed.tsv.bz2
- https://downloads.tatoeba.org/exports/per_language/fra/fra-eng_links.tsv.bz2
- https://downloads.tatoeba.org/exports/per_language/eng/eng_sentences.tsv.bz2
- https://downloads.tatoeba.org/exports/user_languages.tar.bz2
- http://www.lexique.org/databases/Lexique383/Lexique383.tsv

They keep only sentences by self-declared native French speakers that have an English translation, and
skip anything they cannot convert cleanly. `build_connecteurs.py` and `build_edito.py` take no arguments.

## Adding an Édito lesson

Write a function in `scripts/build_edito.py` that returns the lesson's decks (see `u1_opinions`), add it to
`LESSONS`, and run the script. The lesson then appears in the lesson menu and in the mixed review set.

## Credits and licences

- Sentences and translations: [Tatoeba](https://tatoeba.org), CC BY 2.0 FR. Each sentence links to its
  Tatoeba page and names its author.
- Verb forms used to build the data: [Lexique 3.83](http://www.lexique.org), CC BY-SA 4.0.

## Colour schemes

`theme.js` adds a scheme picker (House, the default French-flag palette, or Classic) and a light / dark / auto
picker to the navigation bar. The palettes are CSS custom properties at the top of `style.css`.
