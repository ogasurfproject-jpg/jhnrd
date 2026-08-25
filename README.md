# JHNRD

**Japan Home-visit Nursing Reimbursement Database**

[![validate](https://github.com/ogasurfproject-jpg/jhnrd/actions/workflows/validate.yml/badge.svg)](https://github.com/ogasurfproject-jpg/jhnrd/actions/workflows/validate.yml)
[![live](https://github.com/ogasurfproject-jpg/jhnrd/actions/workflows/live.yml/badge.svg)](https://github.com/ogasurfproject-jpg/jhnrd/actions/workflows/live.yml)
[![version](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fogasurfproject-jpg%2Fjhnrd%2Fmain%2Fstatus.json&query=%24.version&label=version&color=343a40&cacheSeconds=3600)](https://github.com/ogasurfproject-jpg/jhnrd/blob/main/status.json)
[![items](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fogasurfproject-jpg%2Fjhnrd%2Fmain%2Fstatus.json&query=%24.items&label=items&color=0b7285&cacheSeconds=3600)](https://github.com/ogasurfproject-jpg/jhnrd/blob/main/status.json)
[![current statute sources](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fogasurfproject-jpg%2Fjhnrd%2Fmain%2Fstatus.json&query=%24.statute_current&label=current%20statute%20sources&color=5f3dc4&cacheSeconds=3600)](https://github.com/ogasurfproject-jpg/jhnrd/blob/main/status.json)
[![unconfirmed requirements](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fogasurfproject-jpg%2Fjhnrd%2Fmain%2Fstatus.json&query=%24.unconfirmed_requirements&label=unconfirmed%20requirements&color=e8590c&cacheSeconds=3600)](https://github.com/ogasurfproject-jpg/jhnrd/blob/main/status.json)
[![open conflicts](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fogasurfproject-jpg%2Fjhnrd%2Fmain%2Fstatus.json&query=%24.open_conflicts&label=open%20conflicts&color=c2255c&cacheSeconds=3600)](https://github.com/ogasurfproject-jpg/jhnrd/blob/main/status.json)
[![License: CC BY 4.0](https://img.shields.io/badge/license-CC%20BY%204.0-lightgrey.svg)](LICENSE)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22083722.svg)](https://doi.org/10.5281/zenodo.22083722)

A record of Japanese home-visit nursing reimbursement rules — additions, reductions, and the expiry of physician instructions — **in which every requirement carries the document it rests on.**

The numbers themselves are public. **What this dataset holds is where each number came from.**

**[日本語版はこちら → README.ja.md](README.ja.md)**

> **間違いを見つけた方へ。** この資料の誤りに気づけるのは、現場で算定している方です。
> 直し方は **[CONTRIBUTING.md](CONTRIBUTING.md)** に日本語で書いてあります。
> 出典を1つ添えて [Issue](https://github.com/ogasurfproject-jpg/jhnrd/issues/new/choose) を立ててください。
> 「この加算の要件が違う」の一行でも構いません。訂正は不具合として扱います。

---

## Do not make a billing decision on this alone

<!-- auto:caution:start -->
**8 sources currently rest on the statute text itself** (`statute` — the ministerial notice, ordinance or circular). `statute` is 11 in total; 5 of those are superseded revisions and **cannot be used as current authority.** They are kept only so that the revision history is legible.

The rest are ministry material that is not the statute text (`agency`, 8) and private commentary (`secondary`, 7).

**54 requirements are unconfirmed.** Anything we could not check against the statute text says so. It is not left blank.
<!-- auto:caution:end -->

What this dataset can say is: *"this reduction has requirements A, B and C, and C has not yet been confirmed against the statute text."* It never says *"you may bill this"* or *"this applies to you."*

The reason for that line is simple: **when a claim is returned, someone has to be accountable, and a dataset cannot be.**

---

## Where it stands

<!-- auto:state:start -->
| | |
|---|---|
| Version | `2024-kaitei.seed.22` |
| Items | **33** |
| Sources — `statute` (the notice/ordinance/circular itself) | 11 |
| of which **current** | **8** |
| Sources — `agency` (MHLW material, not the statute text) | 8 |
| Sources — `secondary` (private commentary) | 7 |
| Sources, total | 26 (5 not current) |
| Unconfirmed requirements | **54** |
| Conflicts | 4 total / **1** unresolved |
| Field reports | 0 (never a source of rules) |
| Last validated | 2026-08-25 |

33 items. **This is not a complete map of the rules.** The name runs ahead of the contents, and the item count is put first so that this is not hidden.
<!-- auto:state:end -->

---

## Japanese statutory terms are never translated away

Names that come from a statute — `看護体制強化加算 (Ⅰ)`, `特別管理加算`, `告示第95号` — are kept
verbatim in this repository, in the data and in this README, with an English gloss beside them
where one helps.

They are not replaced by an English name. No English name for them exists in any Japanese statute,
so inventing one would create a precision the source does not have. That is the same reason an
unconfirmed requirement is published as unconfirmed rather than tidied away.

## The disciplines

1. **No number without a source.** Every unit value and every requirement carries a `source`.
2. **Every source declares its own standing, in three tiers.** `statute` / `agency` / `secondary`. **Material published by the ministry is not treated as equal to the statute text.**
3. **An unconfirmed item is never left blank.** It carries `confirmed: false` and an `unconfirmed_reason`. Blank and unconfirmed are different things.
4. **When sources disagree, we do not pick one and go quiet.** Both readings go into `conflicts`, and the conflict stays marked unresolved. The moment one is chosen, the reason for choosing it disappears.
5. **Nothing that reads as "you may bill this" is allowed into the data.** The validator rejects it.
6. **Revisions cut a new version; the old one is not deleted.** Otherwise past decisions cannot be audited afterwards.
7. **Every requirement is bound one-to-one to an interview question.** A requirement with no question attached is a requirement nobody has actually asked about.

These are not aspirations. `tools/validate.py` checks them mechanically, and **CI fails on any breach.**

---

## Public MCP endpoint (no key, read-only)

**https://jhnrd-mcp.oga-surf-project.workers.dev**

The dataset is served over MCP (JSON-RPC 2.0 / Streamable HTTP at `POST /mcp`) and over plain HTTP
(`/status.json`, `/items`, `/items/<id>`, `/sources`, `/search?q=`, `/unconfirmed`,
`/conflicts`, `/gaps`, `/disclosure`, `/cite`). **No key. No write path.**

The content is CC BY 4.0 already — but a JSON file on its own means every consumer writes a parser, and every parser mixes in its author's reading. Serving it means that happens in one place.

The same line is drawn on the serving side:

- **It does not decide whether a claim may be billed.** That it never returns such a statement is checked mechanically by the test suite.
- **Every response carries the version, the "this does not decide billing" notice, and the conflict-of-interest disclosure.** All eleven tools are tested for it.
- **It holds no key and is wired to no storage.** The moment it is, it starts holding something of someone's.
- **The tools that expose the weaknesses come first**: `jhnrd_unconfirmed`, `jhnrd_gaps` (including searches that came back empty), `jhnrd_conflicts` (both readings kept).

The copy it serves is generated from the dataset and **never fetched at runtime** — a CDN edge once kept a stale revision alive and an internal server handed out old numbers. **CI fails if the copy drifts from the source.**

Once a day, both the version the live endpoint is actually serving and the manifest listed in the official MCP registry are compared against the repository (the `live` badge above) — because pushing and forgetting to deploy, and publishing a manifest whose metadata the registry silently dropped, have both already happened here.

That check **does not fail when the connection cannot be made** — being unreachable is not evidence of being stale — but it **does** fail when an HTTP status comes back and is not 200, because a status is an answer. The first version of this gate conflated the two and spent its life reporting green while receiving 403s. Its logic is exercised against seventeen mocked endpoints on every push, since a gate that runs once a day can stay broken for a day without anyone knowing.

```json
{ "mcpServers": { "jhnrd": { "type": "http", "url": "https://jhnrd-mcp.oga-surf-project.workers.dev/mcp" } } }
```

See [`mcp/README.md`](mcp/README.md); the registry manifest is [`server.json`](server.json).

---

## Conflict of interest

**The HORIZONs Inc., which maintains this dataset, sells a paid service to home-visit nursing providers that is backed by it.** Payment is taken as an initial build fee and a monthly fee.

So: **the people building this dataset are paid when it is believed to be useful.** That has to be stated first, or the numbers above cannot be used. A dataset whose central discipline is that every source declares its own standing cannot exempt itself from declaring its own.

Four things could bend, and each is bound in advance:

| Temptation | What is bound against it |
| --- | --- |
| Make it look complete | The item count is the headline, with "not a complete map" next to it |
| Make the risk look larger | The validator rejects any wording that reads as a billing decision |
| Delete an inconvenient conflict | Conflicts keep both readings; total and unresolved counts are published separately |
| Hide a correction | Corrections stack on top of the original wording, which is never deleted |

**Every number in this README is generated from `status.json`, and CI fails if it is edited by hand.** Inflating a figure is not something that can be done quietly.

- Revenue comes **only from those customers.** No government, trade-association or vendor funding. No listing fees. No advertising.
- **There is no separate or extended dataset for paying customers.** What is here is all of it.
- Practice notes gathered from providers are **never added without their consent** (currently 0), and are **never a source of rules** even when present.

Full text, and what the maintainer can and cannot decide: **[GOVERNANCE.md](GOVERNANCE.md)** (Japanese).

---

## Citing

**Always cite the version (the seed number). Different versions hold different content.** Because corrections are stacked rather than overwritten, a citation without a version cannot be reconciled afterwards.

```
The HORIZONs Inc. (2026). JHNRD — Japan Home-visit Nursing Reimbursement Database,
version 2024-kaitei.seed.19. Zenodo. https://doi.org/10.5281/zenodo.22083722 (CC BY 4.0)
```

**DOI: [`10.5281/zenodo.22083722`](https://doi.org/10.5281/zenodo.22083722)** — this is the concept DOI covering all versions; it always resolves to the newest. **To cite a specific release, use the per-version DOI on its Zenodo record.** Different versions hold different content.

Machine-readable descriptions — all generated from `status.json`, none written by hand:
[`CITATION.cff`](CITATION.cff) ・ [`datapackage.json`](datapackage.json) ・ [`.zenodo.json`](.zenodo.json) ・ [`CHANGELOG.md`](CHANGELOG.md)

Each version carries an annotated tag: `git tag -l 'seed.*'`, then `git show seed.19`.

---

## Corrections are treated as defects

If a statement here is wrong, or disagrees with the statute text, **please open an issue.** You do not need to run a provider to do so.

- A correction **never deletes the original wording.** Deleting it would make it impossible to check afterwards whether the correction itself was right.
- A correction grounded in `statute` outranks `agency`, which outranks `secondary`.
- Where we say "not confirmed" rather than staying silent, **that is exactly the place to push back.**

How to file: [CONTRIBUTING.md](CONTRIBUTING.md). Contact: `contact@the-horizons-innovation.com`

---

## What is still missing

<!-- auto:gaps:start -->
Unfilled gaps are recorded in `known_gaps` inside `data/rules_2024.json` — currently **7** (resolved ones are kept, marked as resolved).
<!-- auto:gaps:end -->

---

## Maintainer

The HORIZONs Inc. (Japan corporate number 7021001075279)
Toshikatsu Oga ([ORCID 0009-0000-9180-903X](https://orcid.org/0009-0000-9180-903X))

Maintained by a single company. **Not a peer-review body, not a public authority, not a trade association.** No relationship with the Ministry of Health, Labour and Welfare or any other government body, and **nothing here has been confirmed by any of them.**

<!-- auto:footer:start -->
A construction-cost database built to the same disciplines exists at [JCCDB](https://shield.the-horizons-innovation.com/). JHNRD aims to stand in the same place for home-visit nursing. **It is 33 items so far.**
<!-- auto:footer:end -->
