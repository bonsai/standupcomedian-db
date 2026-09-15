# standupcomedian-db

スタンダップコメディアンの人物・プロフィールを扱うDB。

## Responsibility

- comedian / stage name / profile
- affiliation and activity
- source and provenance
- comedian-level metadata

人物そのものを管理し、出演イベントは `bonsai/stage-search` が管理する。

## Ecosystem

```text
standupcomedian-db
        │
        │ who
        ▼
   stage-search
        │
        │ when / where / event
        ▼
      STAGE
```

### Boundary

- `standupcomedian-db` — **誰がスタンダップコメディアンか**
- `stage-search` — **いつ・どこで出演するか**
- `date-mcp` — **デートとしてどう組み合わせるか**
- `dates` — **デートとは何かを理論化する**

## STAGE category

スタンダップコメディは STAGE の `comedy` 系イベントとして扱う。

```text
COMEDY
├── owarai
├── manzai
├── conte
├── standup
├── rakugo
└── kodan
```

## Data policy

人物DBとイベントDBを重複させない。人物の一次情報・出典を保持し、イベントとの関係はID等で接続する。
