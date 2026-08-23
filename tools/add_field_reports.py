# -*- coding: utf-8 -*-
"""
現場の実務を記録する枠を、規則の出典とは別の場所に作る。

なぜ「素性の第4段階」にしないのか:
  statute / agency / secondary は「その規則について、どれだけ強い出典か」の一直線である。
  そこに practice(現場) を足すと、同じ直線の上に並ぶ。
  並んだ瞬間、「現場がそう言っている」が「そう定められている」の弱い版として扱われ、
  いずれ条文が取れない項目を現場の証言で埋めることになる。
  それは、事業所が言ったことを、制度が定めたことにすり替える動きである。

  訪問看護の事業所は、指示書の期限を毎月扱っている。その事実は貴重で、
  条文より正確に「実際どう回っているか」を知っている。
  しかし「実際どう回っているか」は「何が定められているか」ではない。
  運用が慣行として間違っていることもあるし、地域差もある。

  だから軸を分ける。field_reports は、規則の source_ref には決して入れない。
  検査器がそれを拒む。

何に使うのか:
  ・条文が取れるまでの間、現場では何日で運用されているかを記録しておく。
  ・条文が取れたとき、現場の運用と条文がずれていたら、それ自体が見つけるべきもの。
    ご提案 03「出す前に見る目」が探すのは、まさにそのずれである。
  ・誰が言ったかを必ず残す。事業所名と日付。匿名の「現場では」は書かない。
"""

import io, json, os, sys

P = os.path.abspath(os.environ.get("JHNRD_DATA",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "rules_2024.json")))


DISCIPLINE_ADD = (
    "現場の実務(field_reports)は、規則の出典ではない。事業所が毎月扱っている事実は貴重だが、"
    "「実際どう運用されているか」は「何が定められているか」ではない。"
    "field_reports の id を effect や rules の source_ref に入れてはならない。検査器が拒む。"
)

SCHEMA_NOTE = {
    "what": "事業所から聞き取った、現場での実際の運用。規則の出典ではない。",
    "never": "field_reports の id を、effect / rules / requirements の source_ref に入れない。",
    "why": ("入れた瞬間、事業所が言ったことが、制度が定めたことにすり替わる。"
            "運用が慣行として間違っていることもあり、地域差もある。"),
    "must_have": ["item_id で、どの規則についての話かを指す",
                  "reported_by に事業所名(誰の話か分からない『現場では』を書かない)",
                  "reported_at に聞き取った日",
                  "asked_via に、どの設問で聞いたか"],
    "on_conflict": ("条文が取れたとき、現場の運用と条文がずれていたら、そのずれ自体が"
                    "見つけるべきものである。どちらかを消さず、両方を残す。"),
}


def main():
    db = json.load(io.open(P, encoding="utf-8"))

    if DISCIPLINE_ADD not in db.get("discipline", []):
        db.setdefault("discipline", []).append(DISCIPLINE_ADD)

    db.setdefault("field_reports", [])
    db["field_reports_note"] = SCHEMA_NOTE

    # 現場に聞けば分かるもの / 条文でしか分からないもの を、はっきり分けて書いておく。
    # 「未確認」と一括りにすると、聞けば済むものと、原文に当たるしかないものが混ざる。
    for it in db["items"]:
        if it["id"] == "shiji-tsujo":
            for r in it["rules"]:
                if r["id"] == "ts-period":
                    r["can_ask_provider"] = True
                    r["ask_note"] = ("事業所は毎月この期限を扱っている。何か月で回しているかは聞ける。"
                                     "ただし聞けるのは運用であって、条文ではない。"
                                     "答えは field_reports に入れ、confirmed は false のままにする。")
        if it["id"] == "shiji-tokubetsu":
            for r in it["rules"]:
                if r["id"] == "tk-days":
                    r["can_ask_provider"] = True
                    r["ask_note"] = ("特別指示書の交付を実際に受けている事業所なら、"
                                     "何日で運用しているかを知っている。同じく field_reports へ。")
        if it["id"] == "genzan-bcp":
            for r in it["requirements"]:
                if r["id"] in ("bcp-stock",):
                    r["can_ask_provider"] = False
                    r["ask_note"] = "これは条文にあるかどうかの話。事業所に聞いても分からない。"
        if it["id"] == "genzan-gyakutai":
            for d in it.get("detail_unconfirmed", []):
                d["can_ask_provider"] = False
                d["ask_note"] = "頻度が定められているかどうかは、通知を見るしかない。"

    db["version"] = "2024-kaitei.seed.4"
    io.open(P, "w", encoding="utf-8").write(json.dumps(db, ensure_ascii=False, indent=2) + "\n")
    print("field_reports の枠を作りました。版 -> " + db["version"])
    print("  規則の出典とは別の軸。source_ref には入れられません(検査器が拒みます)。")
    ask = []
    for it in db["items"]:
        for key in ("rules", "requirements"):
            for r in it.get(key, []):
                if r.get("can_ask_provider"):
                    ask.append(it["name"] + " / " + r["text"][:40])
    print("\n事業所に聞けば運用が分かるもの: %d 件" % len(ask))
    for a in ask:
        print("  ・" + a)


if __name__ == "__main__":
    main()
