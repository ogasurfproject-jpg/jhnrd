# -*- coding: utf-8 -*-
"""
README の数字を、検査器の出力(status.json)から書き起こす。

なぜ要る (2026-08-24):
  README に「版 seed.6 / 項目 8 / 現行の statute 1件」と書いてあった。
  実際は seed.19 / 33項目 / 現行の statute 7件。11版ぶん古かった。
  中身が進むほど、手で書いた説明は置いていかれる。
  そして「自分の説明が実態より古い」ことは、外から見れば、
  中身が信用できないことと区別がつかない。

  だから、数字は書かない。生成する。
  そして、ずれていたら CI で止める。

使い方:
  python3 tools/update_readme.py           ずれているかを見るだけ
  python3 tools/update_readme.py --write   書き直す
  python3 tools/update_readme.py --check   ずれていたら非ゼロで終わる(CI 用)
"""
import io, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
README = os.path.join(ROOT, "README.md")
README_EN = os.path.join(ROOT, "README_en.md")
STATUS = os.path.join(ROOT, "status.json")
RULES = os.path.join(ROOT, "data", "rules_2024.json")

BLOCKS = ("caution", "state", "gaps", "footer")

# 2026-08-24 追記: 英語版も同じ印で生成する。
#   訳文を手で置いておくと、日本語だけ直って英語が古いまま残る。
#   外から最初に読まれるのは英語の方なので、そちらが古い方が損害が大きい。


def build(st, db):
    src = st["sources"]
    cur = st.get("statute_current", 0)
    stale = st.get("sources_not_current", 0)
    total_src = sum(src.values())
    out = {}

    if cur == 0:
        out["caution"] = ("**現時点で、現行の告示・省令・通知の原文（`statute`）に基づく出典は 1 件もありません。**\n\n"
                          "この版の数字は、実務の判断に使う前に、原文との突合が要ります。")
    else:
        out["caution"] = (
            "**いま、現行の告示・省令・通知の原文（`statute`）に基づく出典は %d 件です。**"
            "（`statute` は全 %d 件。うち %d 件は改正前・改定前の版で、**現行の根拠には使えません。**"
            "版を知るためだけに残しています。）\n\n"
            "残りは厚生労働省の資料（`agency` %d 件）と、民間の解説（`secondary` %d 件）です。\n\n"
            "**未確認の要件が %d 件あります。** 我々が原文で確かめられていないものは、"
            "そう書いてあります。空欄にはしていません。"
            % (cur, src.get("statute", 0), stale, src.get("agency", 0),
               src.get("secondary", 0), st.get("unconfirmed_requirements", 0)))

    conf = ("全 %d 件 / うち未解決 **%d 件**"
            % (st.get("conflicts_total", st.get("open_conflicts", 0)), st.get("open_conflicts", 0)))
    out["state"] = "\n".join([
        "| | |", "|---|---|",
        "| 版 | `%s` |" % st["version"],
        "| 項目数 | **%d** |" % st["items"],
        "| 出典 `statute`（告示・省令・通知の原文） | %d 件 |" % src.get("statute", 0),
        "| うち **現行版** | **%d 件** |" % cur,
        "| 出典 `agency`（厚生労働省の資料） | %d 件 |" % src.get("agency", 0),
        "| 出典 `secondary`（民間の解説） | %d 件 |" % src.get("secondary", 0),
        "| 出典 合計 | %d 件（うち現行でないもの %d 件） |" % (total_src, stale),
        "| 未確認の要件 | **%d 件** |" % st.get("unconfirmed_requirements", 0),
        "| 食い違い | %s |" % conf,
        "| 現場からの報告 | %d 件（規則の出典ではありません） |" % st.get("field_reports", 0),
        "| 最後に検査した日 | %s |" % st.get("checked_at", "—"),
        "",
        "%d 項目です。訪問看護の算定要件を網羅した数字ではありません。**名前が中身を先行しています。**"
        " そのことを隠さないために、項目数を先頭に置いています。" % st["items"],
    ])

    gaps = [g for g in (db.get("known_gaps") or []) if not g.get("resolved")]
    lines = ["`data/rules_2024.json` の `known_gaps` に、埋まっていないものを書いてあります。"
             "いま **%d 件**（解決済みのものは、解決したと分かる形で残してあります）。" % len(gaps), ""]
    for i, g in enumerate(gaps, 1):
        lines.append("%d. %s" % (i, g.get("gap", "")))
    out["gaps"] = "\n".join(lines)

    out["footer"] = ("同じ作法で作られた建設費のデータベースが "
                     "[JCCDB](https://shield.the-horizons-innovation.com/) にあります。"
                     "JHNRD は、訪問看護における同じ位置に立つことを目指しています。**まだ %d 項目です。**"
                     % st["items"])
    return out


def build_en(st, db):
    src = st["sources"]
    cur = st.get("statute_current", 0)
    stale = st.get("sources_not_current", 0)
    total_src = sum(src.values())
    out = {}

    if cur == 0:
        out["caution"] = ("**No source yet rests on the current statute text (`statute`).**\n\n"
                          "Nothing in this version should reach a billing decision without being "
                          "checked against the statute text first.")
    else:
        out["caution"] = (
            "**%d sources currently rest on the statute text itself** "
            "(`statute` — the ministerial notice, ordinance or circular). "
            "`statute` is %d in total; %d of those are superseded revisions and "
            "**cannot be used as current authority.** They are kept only so that the "
            "revision history is legible.\n\n"
            "The rest are ministry material that is not the statute text (`agency`, %d) "
            "and private commentary (`secondary`, %d).\n\n"
            "**%d requirements are unconfirmed.** Anything we could not check against the "
            "statute text says so. It is not left blank."
            % (cur, src.get("statute", 0), stale, src.get("agency", 0),
               src.get("secondary", 0), st.get("unconfirmed_requirements", 0)))

    out["state"] = "\n".join([
        "| | |", "|---|---|",
        "| Version | `%s` |" % st["version"],
        "| Items | **%d** |" % st["items"],
        "| Sources — `statute` (the notice/ordinance/circular itself) | %d |" % src.get("statute", 0),
        "| of which **current** | **%d** |" % cur,
        "| Sources — `agency` (MHLW material, not the statute text) | %d |" % src.get("agency", 0),
        "| Sources — `secondary` (private commentary) | %d |" % src.get("secondary", 0),
        "| Sources, total | %d (%d not current) |" % (total_src, stale),
        "| Unconfirmed requirements | **%d** |" % st.get("unconfirmed_requirements", 0),
        "| Conflicts | %d total / **%d** unresolved |"
        % (st.get("conflicts_total", 0), st.get("open_conflicts", 0)),
        "| Field reports | %d (never a source of rules) |" % st.get("field_reports", 0),
        "| Last validated | %s |" % st.get("checked_at", "—"),
        "",
        "%d items. **This is not a complete map of the rules.** The name runs ahead of the "
        "contents, and the item count is put first so that this is not hidden." % st["items"],
    ])

    gaps = [g for g in (db.get("known_gaps") or []) if not g.get("resolved")]
    out["gaps"] = ("Unfilled gaps are recorded in `known_gaps` inside `data/rules_2024.json` "
                   "— currently **%d** (resolved ones are kept, marked as resolved)." % len(gaps))

    out["footer"] = ("A construction-cost database built to the same disciplines exists at "
                     "[JCCDB](https://shield.the-horizons-innovation.com/). JHNRD aims to stand "
                     "in the same place for home-visit nursing. **It is %d items so far.**"
                     % st["items"])
    return out


def apply_blocks(text, blocks):
    for name in BLOCKS:
        pat = re.compile(r"(<!-- auto:%s:start -->\n)(.*?)(\n<!-- auto:%s:end -->)"
                         % (name, name), re.S)
        if not pat.search(text):
            sys.exit("README に <!-- auto:%s:start --> の印がありません。" % name)
        text = pat.sub(lambda m: m.group(1) + blocks[name] + m.group(3), text)
    return text


def main():
    st = json.load(io.open(STATUS, encoding="utf-8"))
    db = json.load(io.open(RULES, encoding="utf-8"))
    drift = []
    for path, builder in ((README, build), (README_EN, build_en)):
        cur = io.open(path, encoding="utf-8").read()
        new = apply_blocks(cur, builder(st, db))
        if new != cur:
            drift.append((path, new))

    if not drift:
        print("README.md / README_en.md は status.json と一致しています。")
        return 0
    if "--write" in sys.argv:
        for path, new in drift:
            io.open(path, "w", encoding="utf-8").write(new)
            print("書き直しました: %s" % os.path.basename(path))
        return 0
    for path, _ in drift:
        print("status.json とずれています: %s" % os.path.basename(path))
    print("  python3 tools/update_readme.py --write  で直せます。")
    return 1 if "--check" in sys.argv else 0


if __name__ == "__main__":
    sys.exit(main())
