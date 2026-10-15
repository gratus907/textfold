> **This fork (branch `shared-byok`) keeps one TextFold library for a team.** Fold on your own computer with your own
> Claude Code, Codex or API key, then publish what was written to the team's server. Your sign-in never leaves your
> computer; your notes and questions stay there too.
>
> ```sh
> pip install "git+https://github.com/gratus907/textfold@shared-byok"
> textfold <link or file> --model sonnet --to http://<the team's server>:3017 --as "<your name>"   # fold, then publish
> textfold serve                       # or read and fold at http://localhost:3017, as usual, then:
> textfold publish <link, id, or http://localhost:3017/p/<id>> --to http://<the team's server>:3017 --as "<your name>"
> ```
>
> `--model`: `sonnet` or `opus` (Claude Code), `codex/codex/<model>` (Codex). A PDF or a picture needs the PDF engine
> once (`textfold engine install`, about 3.4 GB); Word, PowerPoint, Excel, EPUB, HTML and Markdown files do not.
>
> Set `TEXTFOLD_TEAM=http://<the team's server>:3017` to leave out `--to`. The team's server runs
> `TEXTFOLD_HOST=<its address> textfold serve`. There, everyone reads every text, and anyone without a fold of their
> own can fold with their own API key (kept in their browser) or the team's model. The server rebuilds what is
> published with its own code and does not trust the upload as sent (`textfold/publish.py`).

<div align="center">

<img src="https://raw.githubusercontent.com/chenxiachan/textfold/main/docs/assets/logo.svg" width="72" alt="TextFold">

# TextFold

**Fold any text, from a one-screen map to every word**

<sub>Formerly PaperFold</sub>

<img alt="Python 3.9+" src="https://img.shields.io/badge/python-3.9%2B-6B5CE7?style=flat-square">
<img alt="Runs on your computer" src="https://img.shields.io/badge/runs-on_your_computer-E08A3C?style=flat-square">
<a href="https://github.com/chenxiachan/textfold/blob/main/LICENSE"><img alt="Apache License 2.0" src="https://img.shields.io/badge/license-Apache_2.0-6B5CE7?style=flat-square"></a>

**English** · [简体中文](https://github.com/chenxiachan/textfold/blob/main/README.zh-CN.md)

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/chenxiachan/textfold/main/docs/assets/sources-dark.webp">
  <img src="https://raw.githubusercontent.com/chenxiachan/textfold/main/docs/assets/sources.webp" width="880" alt="What TextFold reads: arXiv, PubMed Central, bioRxiv, medRxiv, Wikipedia, GitHub READMEs, any web page, PDF, Word, PowerPoint, Excel, EPUB, HTML, pictures, Markdown, text, CSV and an agent's replies, folded from the full text down to a few words">
</picture>

**Paste a link:** any web page · arXiv · PubMed Central · bioRxiv · medRxiv · Wikipedia · GitHub<br>
**Drop a file:** PDF · Word · PowerPoint · Excel · EPUB · HTML · CSV · pictures · Markdown · text

**[Try the demo →](https://chenxiachan.github.io/paperfold-gallery/)** or **[install it ↓](#get-started)** · [What's new ↓](#whats-new)

<br>

<img src="https://raw.githubusercontent.com/chenxiachan/textfold/main/docs/assets/zoom.gif" width="880" alt="A paper folding from its full text into a map of its sections, and back">

</div>

## Read with less in your head

Choose the level of detail you need, and lower your cognitive load.

| | Level | Each paragraph becomes | In whose words |
|:-:|---|---|---|
| **1** | **Full** | the paragraph as written | the author's |
| **2** | **Brief** | its one to three key sentences, verbatim | the author's |
| **3** | **Key** | its point and the reason for it | AI, resting on the Brief sentences |
| **4** | **Takeaway** | one line on the spine of its section | AI |
| **5** | **Topic** | a few words; the text becomes a map of section cards | AI |

## Also for agent output

Your agent writes more than you have time to read. A [Claude Code mod](https://code.claude.com/docs/en/plugins/mods/overview) folds every reply the same way, one key per level. [More ↓](#in-claude-code)

<img src="https://raw.githubusercontent.com/chenxiachan/textfold/main/docs/assets/textfold.gif" width="880" alt="A reply in Claude Code folding from the full text to two sentences a paragraph, then one, and back, one key at a time">

## One fold, three places

- **Read.** Paste a link or drop a file; it opens as a map of its sections that you zoom into. [Get started ↓](#get-started)
- **Fold your agent's replies.** One key per level in Claude Code, with no second model. [In Claude Code ↓](#in-claude-code)
- **Plug it into your workflow.** `python3 -m textfold get` hands your agent or script a document one level at a time, and an open format lets any program read and write folded text. [For agents ↓](#for-agents-and-scripts)

## What you get

- **Words that travel.** As you zoom, every word that stays slides to its new place and the rest fade around it.
- **Zoom under your fingers.** Stop halfway, turn back, or open one paragraph alone.

- **Beside the original.** Open a paper's or a PDF's own pages next to the text, each paragraph shown where it stands on its page.
- **Ask AI about exactly what you read.** Select a passage, or ask about the whole text. The answer comes structured: the short answer first, then the evidence, each point citing the paragraph it rests on, one click away.
- **Notes that zoom with the text.** Highlight and write in the margin; what you marked stays as you zoom out, and is saved with the page.

- **Your language.** Twelve languages, translated sentence by sentence, with every formula as typeset.

<table>
<tr>
<td width="50%"><img src="https://raw.githubusercontent.com/chenxiachan/textfold/main/docs/assets/notes.png" alt="Highlights in the full text and a note in the margin"></td>
<td width="50%"><img src="https://raw.githubusercontent.com/chenxiachan/textfold/main/docs/assets/keep.png" alt="The highlighted passages kept at the Takeaway level"></td>
</tr>
<tr>
<td align="center"><sub>Highlight and write in the margin…</sub></td>
<td align="center"><sub>…and keep what you marked as you zoom out.</sub></td>
</tr>
</table>

## Get started

```bash
python3 -m pip install textfold
python3 -m textfold serve
```

Open `http://localhost:3017`. The first time, [connect a model](#connect-a-model); then paste a link or drop a file, and pick a language. You need Python 3.9 or newer (the one macOS ships with works).

| Paste or drop | What TextFold reads |
|---|---|
| A paper's link or DOI: arXiv, PubMed Central, bioRxiv, medRxiv | its text as the site structures it (an arXiv paper needs its HTML version, as most since late 2023 have; another DOI needs an open full text in Europe PMC) |
| Any other web page | its article, without the menus, the adverts, or the text it hides from its readers |
| A Wikipedia article, a GitHub repository | the article; the README, with its pictures |
| A PDF | the paper online when the PDF names one, with your file beside it; any other PDF, converted on your computer by the PDF engine (MinerU, about 3.4 GB, installed once from the landing) |
| A Word, PowerPoint or Excel file, a CSV, an EPUB, a saved web page | the document with its headings, tables, pictures and formulas: read by TextFold itself, or more completely by the PDF engine once it is installed |
| A picture | its text, read by the PDF engine |
| A Markdown or text file | the file as written |

What you read is kept in your system's folder for app data, shared with the desktop app.

<details>
<summary>Run it from the code instead</summary>

```bash
git clone https://github.com/chenxiachan/textfold.git
cd textfold
python3 -m pip install -r requirements.txt
python3 -m textfold serve
```

What you read is then kept in the clone.

</details>

## Connect a model

TextFold uses a model you already have, and there is no account to create. It looks for one when it starts; if it finds none, the first page offers the ways in.

| You have | What to do |
|---|---|
| Claude Code, Codex or Pi | Nothing. TextFold finds it and uses it. |
| A ChatGPT plan | Click **Use my ChatGPT plan**. A small bridge starts on your computer and signs in with your account (needs Node.js). |
| Nothing yet | Click **OpenRouter in one click**. Authorize once, and free models are ready. |
| An API key | **Settings › Add provider**: Anthropic, OpenAI, DeepSeek, Qwen, Zhipu GLM, Kimi, MiniMax, Google, Ollama, or any OpenAI-compatible endpoint. |

## In the reader

| Do | To |
|---|---|
| Pinch, or ⌘ / Ctrl + scroll | zoom around the pointer |
| `1` to `5` | jump to a level |
| Click a paragraph | open just that paragraph |
| Click a figure | see it enlarged |
| **Original**, at the top | read beside the paper's PDF |
| **Save**, at the top | keep the page as one file, or only your notes |
| Select text | highlight, write a note, or ask |
| **Ask the paper**, bottom right | ask about the whole text |
| `L` | next language |

## For agents and scripts

`python3 -m textfold get` gives a document one level at a time, coarsest first, so an agent reads the map before it spends its context on the whole text:

```bash
python3 -m textfold get https://arxiv.org/abs/2201.11903        # the map: every section's topic
python3 -m textfold get 2201.11903 --level key --section 3      # one section: its points, each with its reason
python3 -m textfold get report.pdf --json                       # the whole document, in the TextFold format
```

A document not folded yet is folded first, with the model you connected. Every line a model wrote is marked as such and anchored to the author's sentences it rests on: [docs/format.md](https://github.com/chenxiachan/textfold/blob/main/docs/format.md) describes the format, for any program that reads or writes folded text.

## Save a page

**Save**, at the top of the reader, keeps a page as one HTML file that opens anywhere without a server: its levels, the notes you choose and, if you like, its original PDF to read beside it. It can also keep only your notes, as a page, a PDF, Markdown for Obsidian or JSON. From the command line, the page without your notes:

```bash
python3 -m textfold export 2201.11903
```

TextFold is a tool, and its license covers its code. When you share a file, follow the terms of the original text, shown under its title.

## In Claude Code

TextFold puts the five levels on every reply in Claude Code. Press 5 for the answer in one sentence, 3 for the point of every paragraph, 1 for every word. Nothing is paraphrased, so at every level you read exactly what Claude said.

<details>
<summary><b>Install it, and see what each level gives you</b></summary>

<br>

It needs Claude Code 2.1.287 or later, in the terminal or in the Code tab of the Desktop app.

```bash
claude plugin marketplace add chenxiachan/textfold
claude plugin install textfold@textfold
```

| Key | Level | What you get |
|:-:|---|---|
| **1** | **Full** | every word Claude wrote |
| **2** | **Brief** | each point, with the reason behind it |
| **3** | **Points** | just the points, at a glance |
| **4** | **Outline** | the map of a long reply: its sections, and what each one says |
| **5** | **Gist** | the answer, in one sentence |

Type the digit while the prompt is empty, or pick a level in the row above the prompt. Short replies stay whole: one under about 80 words, or one a fold would barely shorten, always shows as written.

**Start folded.** A session starts at Full. To start at another level, run `/config` and set **Starting level**; in the session, the row above the prompt and the keys 1 to 5 still change it.

**Why you can trust a fold.** TextFold asks Claude to lead with the point: the answer first in every reply, the key sentence first in every paragraph. A fold keeps what Claude put first. There is no second model and no summary, so a fold costs nothing and takes no time.

More in [plugins/textfold](https://github.com/chenxiachan/textfold/blob/main/plugins/textfold/README.md).

</details>

## What's new

- **October 13, 2026: save a page as one file.** **Save**, at the top of the reader, keeps the page as one HTML file, with your notes and its original PDF if you like, or only your notes. [Save a page ↓](#save-a-page)
- **October 13, 2026: Word, PowerPoint, Excel, e-books and more.** Drop a Word, PowerPoint or Excel file, a CSV, an EPUB or a saved web page, and it opens at once, formulas included, with nothing more to install.
- **October 13, 2026: whole figures, and a guide.** A figure the PDF engine cut into pieces now comes out whole, cut from its page. A short guide opens on your first visit, and again from **How it works**.

<details>
<summary>Earlier</summary>

- **October 9, 2026: PaperFold is now TextFold.** The same reader, named for everything it folds: papers, web pages, PDFs, READMEs and your agent's replies. Links to the old repository lead here, and your settings move over by themselves.
- **October 9, 2026: any web page, and PDFs.** Paste any web page's link and read its article at five levels, without the text the page hides from its readers. Drop a PDF: when it names a paper that can be read online, that version opens with your PDF beside it; any other PDF is converted on your computer.
- **October 9, 2026: for agents.** `python3 -m textfold get <link> --level topic` prints a document's map, and `--section` unfolds the part that matters. [More ↓](#for-agents-and-scripts)
- **October 8, 2026: any GitHub README.** Paste a repository's link and read its README at five levels, with its logo, badges and GIFs as on GitHub.
- **October 8, 2026: read beside the original.** **Original**, at the top of a paper, opens its PDF at the left and shows each paragraph on its page as you read. A new paper opens as soon as it can be read, while its levels are written.
- **October 7, 2026: your agent's replies fold too.** [The Claude Code mod](#in-claude-code) puts the five levels on every reply. Press 5 for the answer in one sentence, 1 for every word.
- **October 6, 2026: more than arXiv.** PubMed Central, bioRxiv, medRxiv, Wikipedia in any language, and your own Markdown files.

</details>

<br>

<div align="center">

**If TextFold helps you read, ⭐ star it so others can find it.**

</div>

---

<div align="center">

<sub>Built on [trafilatura](https://github.com/adbar/trafilatura), which finds the article on a web page, [MinerU](https://github.com/opendatalab/MinerU), which converts PDFs, and [mammoth](https://github.com/mwilliamson/python-mammoth), which reads Word files; PDFs are shown with [PDF.js](https://github.com/mozilla/pdf.js) and formulas with [KaTeX](https://katex.org). Thanks to their authors.</sub>

[Apache 2.0](https://github.com/chenxiachan/textfold/blob/main/LICENSE) © 2026 Xia Chen · [Development](https://github.com/chenxiachan/textfold/blob/main/docs/DEVELOPMENT.md) · [Format](https://github.com/chenxiachan/textfold/blob/main/docs/format.md) · [Contributing](https://github.com/chenxiachan/textfold/blob/main/CONTRIBUTING.md) · [Security](https://github.com/chenxiachan/textfold/blob/main/SECURITY.md) · [Feedback](https://github.com/chenxiachan/textfold/issues)

</div>
