# JHNRD

**Japan Home-visit Nursing Reimbursement Database — 訪問看護 算定要件データベース**

[![validate](https://github.com/ogasurfproject-jpg/jhnrd/actions/workflows/validate.yml/badge.svg)](https://github.com/ogasurfproject-jpg/jhnrd/actions/workflows/validate.yml)
[![版](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fogasurfproject-jpg%2Fjhnrd%2Fmain%2Fstatus.json&query=%24.version&label=%E7%89%88&color=343a40&cacheSeconds=3600)](https://github.com/ogasurfproject-jpg/jhnrd/blob/main/status.json)
[![項目数](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fogasurfproject-jpg%2Fjhnrd%2Fmain%2Fstatus.json&query=%24.items&label=%E9%A0%85%E7%9B%AE%E6%95%B0&color=0b7285&cacheSeconds=3600)](https://github.com/ogasurfproject-jpg/jhnrd/blob/main/status.json)
[![現行statuteの出典](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fogasurfproject-jpg%2Fjhnrd%2Fmain%2Fstatus.json&query=%24.statute_current&label=%E7%8F%BE%E8%A1%8Cstatute%E3%81%AE%E5%87%BA%E5%85%B8&color=5f3dc4&cacheSeconds=3600)](https://github.com/ogasurfproject-jpg/jhnrd/blob/main/status.json)
[![未確認の要件](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fogasurfproject-jpg%2Fjhnrd%2Fmain%2Fstatus.json&query=%24.unconfirmed_requirements&label=%E6%9C%AA%E7%A2%BA%E8%AA%8D%E3%81%AE%E8%A6%81%E4%BB%B6&color=e8590c&cacheSeconds=3600)](https://github.com/ogasurfproject-jpg/jhnrd/blob/main/status.json)
[![未解決の食い違い](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fogasurfproject-jpg%2Fjhnrd%2Fmain%2Fstatus.json&query=%24.open_conflicts&label=%E6%9C%AA%E8%A7%A3%E6%B1%BA%E3%81%AE%E9%A3%9F%E3%81%84%E9%81%95%E3%81%84&color=c2255c&cacheSeconds=3600)](https://github.com/ogasurfproject-jpg/jhnrd/blob/main/status.json)
[![License: CC BY 4.0](https://img.shields.io/badge/license-CC%20BY%204.0-lightgrey.svg)](LICENSE)

<sub>*A record of Japanese home-visit nursing reimbursement rules in which every requirement carries the document it rests on. Sources declare their own standing in three tiers, unconfirmed requirements are published as unconfirmed, and conflicting readings are kept side by side. It does not decide whether a claim may be billed. → [English](README_en.md)*</sub>

**[利益相反の開示](#利益相反の開示) ・ [運営と意思決定](GOVERNANCE.md) ・ [直し方](CONTRIBUTING.md) ・ [版ごとの記録](CHANGELOG.md) ・ [引用する](#引用する)**

訪問看護の減算・加算・指示書の期限について、**要件と、その要件がどの資料に基づくかを、一つずつ記録したもの**です。

数字そのものは公開情報です。ここが持っているのは数字ではなく、**その数字がどこから来たのかという記録**です。

---

## 請求の判断に、これだけを使わないでください

<!-- auto:caution:start -->
**いま、現行の告示・省令・通知の原文（`statute`）に基づく出典は 7 件です。**（`statute` は全 10 件。うち 5 件は改正前・改定前の版で、**現行の根拠には使えません。**版を知るためだけに残しています。）

残りは厚生労働省の資料（`agency` 8 件）と、民間の解説（`secondary` 7 件）です。

**未確認の要件が 48 件あります。** 我々が原文で確かめられていないものは、そう書いてあります。空欄にはしていません。
<!-- auto:caution:end -->

請求や届出の判断をする前に、必ず原文を確認してください。このデータベースが言えるのは「**この減算にはA・B・Cの要件があり、Cはまだ我々が原文で確認できていない**」までであって、「算定できます」でも「該当します」でもありません。

その線を引いている理由は単純です。**返戻になったとき、責任の所在が壊れるから**です。

---

## 利益相反の開示

**このデータベースを作っている The HORIZONs株式会社は、これを裏付けに使った有償のサービスを訪問看護事業所に販売しています。** 初期構築費と月額の形で対価を受け取っています。

つまり、**このデータベースが役に立つと思われることで、作っている側が収入を得ます。** 先に書いておかなければ、ここに並んでいる数字は使えません。出典の素性を三段階で名乗ることを規律にしている以上、**このデータベース自身の素性だけ名乗らない、という例外は作れないからです。**

歪みうる方向は 4 つあり（網羅して見せたくなる／危険を大きく見せたくなる／都合の悪い食い違いを消したくなる／直したことを隠したくなる）、それぞれに対して先に手を縛ってあります。**README に書いてある数字は `status.json` から機械生成しており、手で盛ると CI が落ちます。**

- 資金は**顧客からの対価のみ**。行政・業界団体・ベンダからの資金提供、掲載料、広告はありません。
- **有償の顧客だけが見られる別版・拡張版のデータはありません。** ここにあるものが全部です。
- 事業所から聞いた現場の運用は、**同意なしには入れません**（いま 0 件）。入っても**規則の出典にはしません**。

→ **全文と、何を決められて何を決められないかは [GOVERNANCE.md](GOVERNANCE.md)。**

---

## いまの状態

> この節の数字は `status.json` から生成しています。手で書き換えないでください。`python3 tools/update_readme.py --write` で書き直り、ずれていれば CI が止めます。

`status.json` が、検査器の出力そのままです。下の表は、そこから写したものです。**ずれていたら `status.json` が正です。**

<!-- auto:state:start -->
| | |
|---|---|
| 版 | `2024-kaitei.seed.19` |
| 項目数 | **33** |
| 出典 `statute`（告示・省令・通知の原文） | 10 件 |
| うち **現行版** | **7 件** |
| 出典 `agency`（厚生労働省の資料） | 8 件 |
| 出典 `secondary`（民間の解説） | 7 件 |
| 出典 合計 | 25 件（うち現行でないもの 5 件） |
| 未確認の要件 | **48 件** |
| 食い違い | 全 3 件 / うち未解決 **0 件** |
| 現場からの報告 | 0 件（規則の出典ではありません） |
| 最後に検査した日 | 2026-08-24 |

33 項目です。訪問看護の算定要件を網羅した数字ではありません。**名前が中身を先行しています。** そのことを隠さないために、項目数を先頭に置いています。
<!-- auto:state:end -->

---

## 規律

1. **出典の無い数字は1つも入れない。** 単位数も要件も、必ず `source` を持つ。
2. **出典の素性を三段階で名乗る。** `statute`（告示・省令・通知の原文）／`agency`（厚生労働省が出した資料）／`secondary`（民間の解説）。**「厚労省の資料」と「告示そのもの」を同じ扱いにしない。**
3. **確認できていない項目は、空欄にしない。** `confirmed: false` と `unconfirmed_reason` を書いて残す。空欄と未確認は違う。
4. **出典どうしが食い違ったら、片方を選んで黙らない。** `conflicts` に両方を書き、未解決であることを残す。選んだ瞬間に、選んだ理由が消える。
5. **「算定できます」と読める断定を、データの中に置かない。** 検査器が拒否する。
6. **改定で版を切る。旧版は消さない。** 過去の判断を後から検証できなくなるため。
7. **要件は、ヒアリングの設問と1対1で結ぶ。** 結べない要件は、聞けていない要件である。

これらは努力目標ではありません。`tools/validate.py` が機械的に検査し、**一つでも破れば CI が落ちてマージできません。**

---

## 検査する

```bash
python3 tools/validate.py
```

出るもの:

- 出典の素性の内訳（`statute` が 0 件なら、その旨を必ず表示する）
- 未確認の要件の一覧と、なぜ未確認かの理由
- 未解決の食い違いの一覧
- このデータベースが要求するヒアリング設問の id
- 検査の合否（赤なら非ゼロで終了）

---

## 中身

```
data/rules_2024.json      要件と出典の本体
tools/validate.py         検査器（fail-closed）。赤なら非ゼロで終了する
status.json               検査器が吐いた、いまの状態。README も名刺もここから生成する
tools/update_readme.py    README の数字を status.json から引き直す（--check を CI が見る）
tools/make_metadata.py    datapackage.json / .zenodo.json を生成（--check を CI が見る）
tools/make_changelog.py   CHANGELOG.md を annotated tag から生成
```

`data/rules_2024.json` の構造:

```jsonc
{
  "items": [
    {
      "id": "genzan-bcp",
      "kind": "減算",
      "name": "業務継続計画未策定減算",
      "effect": { "value": "…", "confirmed": true, "source_ref": ["mhlw-001195261"] },
      "requirements": [
        { "id": "bcp-plan", "text": "…", "ask": "q_nv_bcp_plan" }
      ],
      "we_do_not_say": "この減算に該当します、とは言わない。"
    }
  ],
  "sources": {
    "mhlw-001195261": { "tier": "agency", "url": "…", "retrieved_at": "2026-08-23" }
  }
}
```

`ask` が、ヒアリングの設問 id です。ここが空の要件は、**聞けていない要件**として検査器が弾きます。

---

## 引用する

**版（seed 番号）を必ず添えてください。版が違えば中身が違います。**

訂正しても元の記述を消さない方針のため、**どの版を見たかが分からないと、後から突き合わせられません。**

```
The HORIZONs Inc. (2026). JHNRD — Japan Home-visit Nursing Reimbursement Database,
version 2024-kaitei.seed.19. https://github.com/ogasurfproject-jpg/jhnrd (CC BY 4.0)
```

機械可読の記述は次のとおりです。**いずれも `status.json` から生成しており、手で書いていません。**

| ファイル | 何か |
| --- | --- |
| [`CITATION.cff`](CITATION.cff) | 引用情報（GitHub の "Cite this repository" が読む） |
| [`datapackage.json`](datapackage.json) | Frictionless Data Package。項目数・出典の内訳・利益相反を機械可読で持つ |
| [`.zenodo.json`](.zenodo.json) | Zenodo 登録用。DOI を取るときの中身 |
| [`CHANGELOG.md`](CHANGELOG.md) | 版ごとに何をどう直したか（annotated tag から生成） |

各版には annotated tag が打ってあります。

```bash
git tag -l 'seed.*'      # 版の一覧
git show seed.19         # その版に何が書いてあったか
```

---

## 間違いを見つけたら

**訂正は不具合として扱います。**

このデータベースの記述が間違っている、あるいは原文と食い違っている、と思われた場合は Issue を立ててください。事業所を運営されている必要はありません。

- 訂正すると、**元の記述は消しません。** 消すと、訂正が正しかったかどうかを後から確かめられなくなるためです。
- 訂正の根拠が `statute`（原文）であれば、`agency` や `secondary` に優先します。素性の強い出典が来たら、弱い出典に基づく記述は差し替えます。
- 我々が確認できなかった項目については、そう書いてあります。**「書いていない」ではなく「確認できていない」と書いてある箇所は、そのまま指摘してください。**

**指摘の出し方は [CONTRIBUTING.md](CONTRIBUTING.md) に、訂正がどう処理されるかは [GOVERNANCE.md](GOVERNANCE.md) 4 に書いてあります。**
Issue の様式は 2 つ用意してあります（[訂正](../../issues/new?template=correction.yml) ／ [抜け](../../issues/new?template=gap.yml)）。

連絡先: `contact@the-horizons-innovation.com`

---

## これから埋めるもの

<!-- auto:gaps:start -->
`data/rules_2024.json` の `known_gaps` に、埋まっていないものを書いてあります。いま **7 件**（解決済みのものは、解決したと分かる形で残してあります）。

1. 加算は2項目しか入っていない。取りこぼしを探すには全く足りない。
2. このデータベースは令和6年度改定(2024)を見て作った。令和8年度改定が医療・介護の両方で令和8年6月に施行されている。既にある8項目は、まだ令和8年6月施行版で確かめ直していない。
3. 医療保険の訪問看護指示期間の日数につき減算(1日につき −97単位)が、この版に項目として入っていない。
4. 看護・介護職員連携強化加算(1月につき +250単位)が入っていない。
5. 訪問看護費の『ハ 定期巡回・随時対応型訪問介護看護事業所と連携する場合』(1月につき 2,961単位)が入っていない。
6. サービス提供体制強化加算のうち『ハを算定する場合』(1月につき +50単位 /+25単位)が入っていない。
7. 介護職員等処遇改善加算の率(所定単位×18/1000)が項目として入っていない。
<!-- auto:gaps:end -->

---

## 運営

The HORIZONs株式会社（法人番号 7021001075279）
監修 大賀俊勝（[ORCID 0009-0000-9180-903X](https://orcid.org/0009-0000-9180-903X)）

一社が単独で維持しています。**査読機関でも、公的機関でも、業界団体でもありません。** 厚生労働省をはじめとする行政機関とは関係がなく、**ここに載っている内容について行政の確認は受けていません。**

**[利益相反の開示](#利益相反の開示)** ／ 意思決定と訂正の扱い: **[GOVERNANCE.md](GOVERNANCE.md)**

<!-- auto:footer:start -->
同じ作法で作られた建設費のデータベースが [JCCDB](https://shield.the-horizons-innovation.com/) にあります。JHNRD は、訪問看護における同じ位置に立つことを目指しています。**まだ 33 項目です。**
<!-- auto:footer:end -->
