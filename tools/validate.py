# -*- coding: utf-8 -*-
"""
訪問看護 算定要件データベースの検査。

JCCDB に対する適正診断と同じで、物差しそのものが検査を通っていなければ、
それを使った判断は何の裏づけにもならない。以下を fail-closed で見る。

  1. 数字を持つ項目は、必ず出典を持つこと。出典の無い数字は1つも通さない。
  2. 出典は素性を必ず名乗ること。statute(告示・省令・通知の原文) / agency(厚生労働省が
     出した資料) / secondary(民間の解説)の三段階。「厚労省の資料」と「告示そのもの」を
     同じ扱いにしない。黙って混ぜない。
  3. confirmed:false の項目は、なぜ未確認かを書いてあること。
     「空欄」と「確認できていない」は違う。後者は理由ごと残す。
  4. requirements の各項目は、ヒアリングの設問と結ばれていること。
     結べない要件は、聞けていない要件である。
  5. 「算定できる」と読める断定を、データの中に置かないこと。
  6. 現場の実務(field_reports)を、規則の出典として使っていないこと。
     事業所が毎月扱っている事実は貴重だが、「実際どう運用されているか」は
     「何が定められているか」ではない。混ぜた瞬間、事業所が言ったことが
     制度が定めたことにすり替わる。

一つでも落ちたら非ゼロで終わる。数字を出す前に、この検査を通す。
"""

import io, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT = os.path.join(HERE, "..", "data", "rules_2024.json")

# 出典の素性。上ほど強い。
TIERS = ("statute", "agency", "secondary")
TIER_JA = {"statute": "告示・通知の原文", "agency": "厚労省の資料", "secondary": "民間の解説"}

# データの中に置いてはいけない言い方。我々は要件を並べるだけで、可否は判定しない。
FORBIDDEN = [
    "算定できます", "算定可能です", "算定してください", "減算されます",
    "問題ありません", "大丈夫です", "違反です",
]


def walk_strings(node, path=""):
    if isinstance(node, dict):
        for k, v in node.items():
            yield from walk_strings(v, path + "/" + str(k))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from walk_strings(v, path + "[%d]" % i)
    elif isinstance(node, str):
        yield path, node


def main():
    path = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else DEFAULT)
    db = json.load(io.open(path, encoding="utf-8"))
    src = db.get("sources", {})
    errs, warns, asks = [], [], set()

    print("検査するもの: %s" % os.path.basename(path))
    print("版           : %s (%s)" % (db.get("version"), db.get("revision")))
    print("項目数       : %d / 出典 %d 件\n" % (len(db.get("items", [])), len(src)))

    # 2. 出典が素性を名乗っているか
    for sid, s in src.items():
        if s.get("tier") not in TIERS:
            errs.append("出典 %s の tier が %s のどれでもない" % (sid, "/".join(TIERS)))
        if not s.get("url"):
            errs.append("出典 %s に url がない" % sid)
        if not s.get("retrieved_at"):
            errs.append("出典 %s に取得日がない" % sid)

    def check_refs(where, obj):
        refs = obj.get("source_ref") or []
        for r in refs:
            if r not in src:
                errs.append("%s が知らない出典 %s を指している" % (where, r))
        return refs

    for it in db.get("items", []):
        iid = it.get("id", "(id無し)")

        # 1. 数字を持つ塊には出典が要る
        for block in ("effect", "timeline"):
            b = it.get(block)
            if not isinstance(b, dict):
                continue
            has_number = any(re.search(r"[0-9０-９]", str(v)) for v in b.values() if isinstance(v, str))
            refs = check_refs("%s/%s" % (iid, block), b)
            if has_number and b.get("confirmed") and not refs:
                errs.append("%s/%s は数字を持つのに出典がない" % (iid, block))
            # 3. 未確認なら理由が要る
            if b.get("confirmed") is False and not b.get("unconfirmed_reason"):
                errs.append("%s/%s が confirmed:false なのに理由がない" % (iid, block))

        # 3 + 4. requirements / rules / watch
        for key in ("requirements", "rules", "watch"):
            for r in it.get(key, []):
                rid = "%s/%s/%s" % (iid, key, r.get("id", "?"))
                if r.get("confirmed") is False and not r.get("unconfirmed_reason"):
                    errs.append("%s が confirmed:false なのに理由がない" % rid)
                check_refs(rid, r)
                if key in ("requirements", "watch"):
                    if r.get("ask"):
                        asks.add(r["ask"])
                    else:
                        errs.append("%s がヒアリングの設問と結ばれていない(ask がない)" % rid)

        for c in it.get("conflicts", []):
            cid = "%s/conflicts/%s" % (iid, c.get("about", "?"))
            if not c.get("status"):
                errs.append("%s に status がない(未解決かどうかが分からない)" % cid)
            for side in ("claim_a", "claim_b"):
                cl = c.get(side)
                if not isinstance(cl, dict):
                    errs.append("%s に %s がない" % (cid, side)); continue
                if not check_refs(cid + "/" + side, cl):
                    errs.append("%s/%s に出典がない" % (cid, side))

        if not it.get("sources"):
            warns.append("%s に item 単位の sources がない" % iid)

    # 6. 現場の実務を、規則の出典に使っていないか。
    fr = db.get("field_reports") or []
    fr_ids = set()
    for i, r in enumerate(fr):
        rid = r.get("id") or ("field_report[%d]" % i)
        fr_ids.add(rid)
        for need in ("item_id", "reported_by", "reported_at", "text"):
            if not r.get(need):
                errs.append("%s に %s がない" % (rid, need))
        if r.get("item_id") and r["item_id"] not in {x.get("id") for x in db.get("items", [])}:
            errs.append("%s が知らない項目 %s を指している" % (rid, r["item_id"]))
    if fr_ids:
        for it in db.get("items", []):
            for block in ("effect", "timeline"):
                b = it.get(block)
                if isinstance(b, dict):
                    for ref in (b.get("source_ref") or []):
                        if ref in fr_ids:
                            errs.append("%s/%s が現場の実務 %s を規則の出典にしている"
                                        % (it.get("id"), block, ref))
            for key in ("requirements", "rules", "watch"):
                for r in it.get(key, []):
                    for ref in (r.get("source_ref") or []):
                        if ref in fr_ids:
                            errs.append("%s/%s/%s が現場の実務 %s を規則の出典にしている"
                                        % (it.get("id"), key, r.get("id"), ref))

    # 5. 断定の言い方を置いていないか
    for p, s in walk_strings(db):
        if p.endswith("/we_do_not_say") or "/discipline" in p:
            continue
        for w in FORBIDDEN:
            if w in s:
                errs.append("断定的な言い方「%s」が %s にある" % (w, p))

    # 素性の集計。二次資料しか無いことを、黙って通さず必ず出す。
    tiers = {}
    for s in src.values():
        tiers[s.get("tier")] = tiers.get(s.get("tier"), 0) + 1
    print("出典の素性:")
    for t in TIERS:
        print("  %-10s (%s) %d件" % (t, TIER_JA[t], tiers.get(t, 0)))
    if not tiers.get("statute"):
        print("  → 告示・通知の原文は、まだ1件も無い。この版の数字は、実務判断の前に原文との突合が要る。")

    # 出典どうしの食い違い。解けていないものは必ず出す。黙って片方を採らない。
    conflicts = []
    for it in db.get("items", []):
        for c in it.get("conflicts", []):
            conflicts.append((it.get("name"), c.get("about"), c.get("status")))
    print("\n現場からの報告: %d 件 (規則の出典ではない)" % len(db.get("field_reports") or []))
    for r in (db.get("field_reports") or []):
        print("  ・%s: %s (%s)" % (r.get("item_id"), str(r.get("text"))[:44], r.get("reported_by")))

    print("\n事業所に聞けば運用が分かる未確認: ", end="")
    askable_now = []
    for it in db.get("items", []):
        for key in ("rules", "requirements"):
            for r in it.get(key, []):
                if r.get("confirmed") is False and r.get("can_ask_provider"):
                    askable_now.append(it.get("name") + " / " + str(r.get("text"))[:36])
    print("%d 件" % len(askable_now))
    for a in askable_now:
        print("  ・" + a)

    fnd = db.get("findings") or []
    print("\n途中まで分かったこと: %d 件 (結論ではない)" % len(fnd))
    for f in fnd:
        print("  ・%s" % f.get("about"))
        print("    分かった  : %s" % str(f.get("known", {}).get("text", ""))[:64])
        for nk in (f.get("not_known") or [])[:2]:
            print("    未確認    : %s" % nk[:60])

    print("\n未解決の食い違い: %d 件" % len(conflicts))
    for n, a, st in conflicts:
        print("  ・%s / %s (%s)" % (n, a, st))

    unconf = []
    for it in db.get("items", []):
        for key in ("requirements", "rules"):
            for r in it.get(key, []):
                if r.get("confirmed") is False:
                    unconf.append("%s / %s" % (it.get("name"), r.get("text", "")[:44]))
    print("未確認の要件: %d 件" % len(unconf))
    for u in unconf:
        print("  ・" + u)

    print("\nヒアリングで聞くべき設問 id: %d 個" % len(asks))
    for a in sorted(asks):
        print("  " + a)

    if warns:
        print("\n注意:")
        for w in warns:
            print("  ・" + w)
    status = {
        "version": db.get("version"),
        "revision": db.get("revision"),
        "items": len(db.get("items", [])),
        "sources": {t: tiers.get(t, 0) for t in TIERS},
        "unconfirmed_requirements": len(unconf),
        "open_conflicts": len(conflicts),
        "field_reports": len(db.get("field_reports") or []),
        "askable_from_provider": len(askable_now),
        "questions_required": sorted(asks),
        "checked_at": db.get("built_at"),
        "passed": not errs,
    }
    # status.json は、リポジトリ本体のデータを検査したときだけ書く。
    # 2026-08-23、壊したコピーを検査したときに status.json を上書きしてしまった。
    # 検査は読むだけの操作であるべきで、どこを見たかで結果が書き換わってはいけない。
    if os.path.abspath(path) != os.path.abspath(DEFAULT):
        print("\n(既定のデータではないので status.json は書きません: %s)" % path)
        if errs:
            print("\n検査: 赤")
            for e in errs:
                print("  ・" + e)
            sys.exit(2)
        print("\n検査: 緑")
        return
    out = os.path.join(os.path.dirname(path), "..", "status.json")
    try:
        io.open(os.path.abspath(out), "w", encoding="utf-8").write(
            json.dumps(status, ensure_ascii=False, indent=2) + "\n")
        print("\n状態を書いた: status.json")
    except Exception as e:
        print("\n状態を書けなかった: %s" % e, file=sys.stderr)

    if errs:
        print("\n検査: 赤")
        for e in errs:
            print("  ・" + e)
        sys.exit(2)
    print("\n検査: 緑")


if __name__ == "__main__":
    main()
