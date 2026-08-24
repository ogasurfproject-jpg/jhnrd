# -*- coding: utf-8 -*-
"""
機械が読む名刺(datapackage.json / .zenodo.json)を、検査器の出力から書き起こす。

なぜ要る (2026-08-24):
  README の数字が11版ぶん古かったのと、同じことが機械可読の記述でも起きる。
  むしろこちらの方が危ない。人間は README を読み直すが、
  カタログや DOI の登録情報は、一度登録すると誰も読み直さないからである。
  古い項目数が Zenodo に刻まれ、そこから引用される方が、README のずれより長く残る。

  だから、ここも書かない。生成する。そして、ずれていたら CI で止める。

使い方:
  python3 tools/make_metadata.py           ずれているかを見るだけ
  python3 tools/make_metadata.py --write   書き直す
  python3 tools/make_metadata.py --check   ずれていたら非ゼロで終わる(CI 用)
"""
import io, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
STATUS = os.path.join(ROOT, "status.json")
RULES = os.path.join(ROOT, "data", "rules_2024.json")
DATAPACKAGE = os.path.join(ROOT, "datapackage.json")
ZENODO = os.path.join(ROOT, ".zenodo.json")
SERVER = os.path.join(ROOT, "server.json")

# 公開MCPの居場所。ここを変えたら server.json も一緒に動く。
MCP_URL = "https://jhnrd-mcp.oga-surf-project.workers.dev/mcp"

REPO = "https://github.com/ogasurfproject-jpg/jhnrd"
ORCID = "0009-0000-9180-903X"
AFFIL = "The HORIZONs Inc. (法人番号 7021001075279)"

KEYWORDS = ["訪問看護", "介護報酬", "診療報酬", "算定要件", "出典", "provenance",
            "home-visit nursing", "long-term care insurance", "health insurance",
            "reimbursement", "Japan", "open data"]

# 素性を名乗るデータベースが、自分の素性を名乗らないという例外は作れない。
# 有償サービスを売っていることは、機械可読の名刺にも書く。
COI_JA = ("利益相反: The HORIZONs株式会社は、このデータベースを裏付けに使った有償のサービスを"
          "訪問看護事業所に販売している。収入源は顧客からの対価のみで、行政・業界団体・"
          "ベンダからの資金提供、掲載料、広告は受けていない。"
          "詳細は GOVERNANCE.md を参照のこと。")
COI_EN = ("Conflict of interest: The HORIZONs Inc. sells a paid service to home-visit nursing "
          "providers that is backed by this database. Revenue comes only from those customers; "
          "no government, trade-association or vendor funding, no listing fees, no advertising. "
          "See GOVERNANCE.md.")


def numbers(st):
    src = st["sources"]
    return {
        "version": st["version"],
        "items": st["items"],
        "sources_total": sum(src.values()),
        "sources_statute": src.get("statute", 0),
        "sources_statute_current": st.get("statute_current", 0),
        "sources_agency": src.get("agency", 0),
        "sources_secondary": src.get("secondary", 0),
        "sources_not_current": st.get("sources_not_current", 0),
        "unconfirmed_requirements": st.get("unconfirmed_requirements", 0),
        "conflicts_total": st.get("conflicts_total", 0),
        "open_conflicts": st.get("open_conflicts", 0),
        "field_reports": st.get("field_reports", 0),
        "checked_at": st.get("checked_at", ""),
    }


def desc_ja(n):
    return ("訪問看護の減算・加算・指示書の期限について、要件と、その要件がどの資料に基づくかを"
            "一つずつ記録したデータセット。数字そのものは公開情報であり、ここが持っているのは"
            "「その数字がどこから来たのか」という記録である。"
            "出典は statute(告示・省令・通知の原文) / agency(厚生労働省の資料) / "
            "secondary(民間の解説) の三段階で素性を名乗り、現行版かどうかを別に持つ。"
            "確認できていない要件は空欄にせず confirmed:false と理由を残す。"
            "出典どうしが食い違ったときは、片方を選ばず両方を残す。"
            "取りに行って取れなかった記録(attempts)も公開する。算定の可否は判定しない。"
            "この版は %(items)d 項目・出典 %(sources_total)d 件"
            "(うち現行の statute %(sources_statute_current)d 件)・"
            "未確認の要件 %(unconfirmed_requirements)d 件・"
            "未解決の食い違い %(open_conflicts)d 件。"
            "%(items)d 項目は訪問看護の算定要件を網羅した数ではない。" % n)


def desc_en(n):
    return ("A record of Japanese home-visit nursing reimbursement rules — additions, reductions "
            "and the expiry of physician instructions — in which every requirement carries the "
            "document it rests on. The numbers themselves are public; what this dataset holds is "
            "where each number came from. Every source declares its own standing in three tiers: "
            "statute (the text of the ministerial notice, ordinance or circular itself), agency "
            "(material published by the Ministry of Health, Labour and Welfare that is not the "
            "statute text), and secondary (private commentary). Whether a source is the currently "
            "effective revision is held separately. Requirements we could not confirm against the "
            "statute text are not left blank: they are marked confirmed:false with the reason. "
            "Where sources disagree, both readings are kept rather than one being chosen silently. "
            "Searches that came back empty are published too (attempts). The dataset does not "
            "decide whether a claim may be billed. "
            "This release holds %(items)d items, %(sources_total)d sources "
            "(%(sources_statute_current)d of them the current statute text), "
            "%(unconfirmed_requirements)d unconfirmed requirements and "
            "%(open_conflicts)d unresolved conflicts. "
            "%(items)d items is not a complete map of the rules." % n)


def build_datapackage(n):
    return {
        "$schema": "https://datapackage.org/profiles/1.0/datapackage.json",
        "name": "jhnrd",
        "title": "JHNRD — Japan Home-visit Nursing Reimbursement Database",
        "id": REPO,
        "version": n["version"],
        "description": desc_ja(n),
        "homepage": REPO,
        "created": n["checked_at"],
        "licenses": [{
            "name": "CC-BY-4.0",
            "path": "https://creativecommons.org/licenses/by/4.0/",
            "title": "Creative Commons Attribution 4.0 International",
        }],
        "contributors": [{
            "title": "Toshikatsu Oga",
            "givenName": "Toshikatsu",
            "familyName": "Oga",
            "roles": ["author", "maintainer"],
            "organization": AFFIL,
            "path": "https://orcid.org/" + ORCID,
        }],
        "keywords": KEYWORDS,
        "languages": ["ja"],
        "resources": [
            {
                "name": "rules",
                "path": "data/rules_2024.json",
                "title": "要件と出典の本体",
                "description": "items[] が要件、sources{} が出典。attempts / findings / "
                               "conflicts / known_gaps に、取れなかったもの・途中までのもの・"
                               "食い違い・埋まっていないものを残す。",
                "format": "json",
                "mediatype": "application/json",
                "encoding": "utf-8",
            },
            {
                "name": "status",
                "path": "status.json",
                "title": "検査器が吐いた、いまの状態",
                "description": "tools/validate.py の出力そのまま。README と datapackage.json の"
                               "数字はここから生成され、ずれていれば CI が止める。",
                "format": "json",
                "mediatype": "application/json",
                "encoding": "utf-8",
            },
        ],
        "x-jhnrd": {
            "note": "この節の数字は tools/make_metadata.py が status.json から生成する。手で書かない。",
            "counts": {k: v for k, v in n.items() if k != "version"},
            "tiers": {
                "statute": "告示・省令・通知の原文。最も強い。",
                "agency": "厚生労働省が出した資料。原文ではない。",
                "secondary": "民間の解説。単独では確定にしない。",
            },
            "we_do_not_say": "算定できます・該当します、とは言わない。検査器が拒否する。",
            "conflict_of_interest": COI_JA,
            "governance": REPO + "/blob/main/GOVERNANCE.md",
        },
    }


def build_zenodo(n):
    return {
        "upload_type": "dataset",
        "title": "JHNRD — Japan Home-visit Nursing Reimbursement Database (%s)" % n["version"],
        "description": (desc_en(n) + "<br><br>" + COI_EN + "<br><br>" +
                        "（日本語）" + desc_ja(n) + "<br><br>" + COI_JA),
        "creators": [{
            "name": "Oga, Toshikatsu",
            "affiliation": AFFIL,
            "orcid": ORCID,
        }],
        "license": "cc-by-4.0",
        "access_right": "open",
        "language": "jpn",
        "version": n["version"],
        "keywords": KEYWORDS,
        "related_identifiers": [
            {"identifier": REPO, "relation": "isSupplementTo", "scheme": "url"},
        ],
        "notes": ("版が違えば中身が違う。引用するときは版(seed 番号)を添えること。"
                  "訂正しても元の記述を消さない方針のため、どの版を見たかが分からないと"
                  "後から突き合わせられない。 / Versions differ in content. Cite the seed number: "
                  "corrections are stacked on top of the original wording, never overwriting it."),
    }


def build_server(n):
    """公式の MCP レジストリに出す名刺。

    版番号が2つになることについて:
      レジストリの version は semver に従うことになっている。
      データの版は 2024-kaitei.seed.19 で、semver ではない。
      勝手に別の番号を振ると、どちらが本当か分からなくなるので、
      seed 番号から機械的に 0.<seed>.0 を作る。数字は1つしか無い。
      description は 100 文字まで、と schema が決めている。
    """
    seed = str(n["version"]).split("seed.")[-1]
    try:
        seed_no = int(seed)
    except ValueError:
        seed_no = 0
    desc = ("Japan home-visit nursing reimbursement rules, each with its source "
            "and that source's standing.")
    if len(desc) > 100:
        raise SystemExit("server.json の description が 100 文字を超えている: %d" % len(desc))
    return {
        "$schema": "https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json",
        "name": "io.github.ogasurfproject-jpg/jhnrd",
        "description": desc,
        "version": "0.%d.0" % seed_no,
        "websiteUrl": REPO,
        "repository": {"url": REPO, "source": "github"},
        "remotes": [{"type": "streamable-http", "url": MCP_URL}],
        "_meta": {
            "io.github.ogasurfproject-jpg/jhnrd": {
                "dataset_version": n["version"],
                "items": n["items"],
                "unconfirmed_requirements": n["unconfirmed_requirements"],
                "open_conflicts": n["open_conflicts"],
                "does_not_decide_billing":
                    "算定の可否は判定しない。『算定できます』『該当します』を返さない。",
                "conflict_of_interest": COI_EN,
                "license": "CC-BY-4.0",
            }
        },
    }


def dump(obj):
    return json.dumps(obj, ensure_ascii=False, indent=2) + "\n"


def main():
    st = json.load(io.open(STATUS, encoding="utf-8"))
    json.load(io.open(RULES, encoding="utf-8"))  # 壊れていたらここで落とす
    n = numbers(st)
    want = {DATAPACKAGE: dump(build_datapackage(n)),
            ZENODO: dump(build_zenodo(n)),
            SERVER: dump(build_server(n))}

    drift = []
    for path, text in want.items():
        cur = io.open(path, encoding="utf-8").read() if os.path.exists(path) else None
        if cur != text:
            drift.append(path)

    if not drift:
        print("datapackage.json / .zenodo.json / server.json は status.json と一致しています。")
        return 0
    if "--write" in sys.argv:
        for path in drift:
            io.open(path, "w", encoding="utf-8").write(want[path])
            print("書き直しました: %s" % os.path.relpath(path, ROOT))
        return 0
    for path in drift:
        print("ずれています: %s" % os.path.relpath(path, ROOT))
    print("  python3 tools/make_metadata.py --write  で直せます。")
    return 1 if "--check" in sys.argv else 0


if __name__ == "__main__":
    sys.exit(main())
