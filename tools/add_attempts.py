# -*- coding: utf-8 -*-
"""
取りに行って、取れなかったものを記録する。

出典の一覧には「取れたもの」しか載らない。そのままだと、
まだ取れていない項目について、次に調べる人が同じ道を同じ順で辿り、
同じところで止まる。時間だけが消える。

取れなかったことは失敗ではなく、次の人にとっての情報である。
どの URL を、何を狙って開き、何が返ってきたかを残す。
"""

import io, json, os

P = os.path.abspath(os.environ.get("JHNRD_DATA",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "rules_2024.json")))

ATTEMPTS = [
    {
        "at": "2026-08-23",
        "looking_for": "厚生省令第37号 第4章(訪問看護)末尾の準用規定の条番号。第30条の2と第37条の2が準用されているかどうか。",
        "why_it_matters": "これが確認できるまで、取得済みの条文(訪問介護の章)を訪問看護の要件として断定できない。いま最も重い穴。",
        "tried": [
            {"url": "https://www.mhlw.go.jp/web/t_doc?dataId=82999404&dataType=0&pageNo=1",
             "got": "第30条の2(業務継続計画の策定等)と第37条の2(虐待の防止)の条文を取得できた。訪問介護の章まで。準用規定には届かず。"},
            {"url": "https://www.mhlw.go.jp/web/t_doc?dataId=82999404&dataType=0&pageNo=2",
             "got": "第60条〜第62条あたりで切れる。準用規定には届かず。"},
            {"url": "https://www.mhlw.go.jp/web/t_doc?dataId=82999404&dataType=0&pageNo=3",
             "got": "第60条第3項の途中で切れる。pageNo を増やしても先に進まない。この閲覧系のページ送りは、条文の順序どおりに増えていないと思われる。"},
            {"url": "https://laws.e-gov.go.jp/law/411M50000100037",
             "got": "取得できず(このセッションの取得制限)。"},
        ],
        "next_ideas": [
            "e-Gov 法令検索の条文ページを、検索結果経由で開く。",
            "国立社会保障・人口問題研究所が公開している省令の PDF (https://www.ipss.go.jp/publication/j/shiryou/no.13/data/shiryou/syakaifukushi/728.pdf) を当たる。ただし古い版の可能性があるので、改正の反映状況を先に確認すること。",
            "厚生労働省の閲覧系で、条文番号を直接指定できるパラメータがあるか調べる。",
        ],
    },
    {
        "at": "2026-08-23",
        "looking_for": "高齢者虐待防止措置未実施減算における研修の頻度(訪問看護は年1回以上か)。",
        "why_it_matters": "ヒアリングの設問文に『訪問看護は年1回以上が要件です』と書いていた。省令の条文は『定期的に』としか書いておらず、頻度は無い。設問文からは既に外した。頻度が本当に定められているなら、解釈通知の側にあるはず。",
        "tried": [
            {"url": "https://www.mhlw.go.jp/content/001227740.pdf",
             "got": "介護保険最新情報 Vol.1225 の送付状のみ取得。Q&A 本体に届かず。"},
        ],
        "next_ideas": [
            "介護保険最新情報 Vol.1263 (https://www.mhlw.go.jp/content/001255245.pdf) を当たる。",
            "留意事項通知(指定居宅サービスに要する費用の額の算定に関する基準の制定に伴う実施上の留意事項について)の令和6年改正版を探す。",
            "介護保険最新情報 Vol.1285 / Vol.1345 を当たる(カイポケの記事が挙げていた宛先)。",
        ],
    },
]


def main():
    db = json.load(io.open(P, encoding="utf-8"))
    db["attempts"] = ATTEMPTS
    db["attempts_note"] = ("取りに行って取れなかったものの記録。出典の一覧には取れたものしか載らないので、"
                           "ここが無いと、次に調べる人が同じ道を同じ順で辿って同じところで止まる。")
    io.open(P, "w", encoding="utf-8").write(json.dumps(db, ensure_ascii=False, indent=2) + "\n")
    print("取れなかった記録を %d 件 追加しました" % len(ATTEMPTS))


if __name__ == "__main__":
    main()
