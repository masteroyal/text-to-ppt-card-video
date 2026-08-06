# Lieflat 主题 CSS 参考

> Text-to-PPT-Card-Video 的主题 CSS 参考，包含全部 12 套 lieflat 主题。
> 主题 CSS 与卡片布局参考 [lieflat-html-design](https://github.com/larashero3-dotcom/lieflat-html-design)（MIT），版权和许可信息以原仓库为准。
> `gen_draft.py` 通过 `scripts/themes.py` 按 manifest 的 `theme` 字段读取对应主题。

---

## 公共基础样式

下面是所有主题共用的基础样式。生成 HTML 时，`gen_draft.py` 会先写入这份基础布局，再叠加对应主题的 CSS。卡片的实际宽高由 manifest 的 `aspect_ratio` 决定，本节不写死固定尺寸。

```css
/* === RESET & BASE === */
*{box-sizing:border-box;margin:0;padding:0}
html,body{min-height:100%}

/* === DECK LAYOUT (horizontal scroll) === */
.deck{display:flex;overflow-x:auto;scroll-snap-type:x mandatory;scroll-behavior:smooth;height:100vh;width:100vw}
.deck::-webkit-scrollbar{display:none}
.deck{-ms-overflow-style:none;scrollbar-width:none}
.page{flex:0 0 100vw;height:100vh;display:flex;align-items:center;justify-content:center;scroll-snap-align:center;padding:32px}

/* === CARD SHELL === */
.card{position:relative;overflow:hidden;border-radius:6px}
/* 实际宽高由 gen_draft.py 按 aspect_ratio 生成 */
.card--cover{max-width:calc(100vw - 48px)}
.card--content{max-width:calc(100vw - 48px)}
.article{height:100%;overflow-y:auto;background:inherit}
.article::-webkit-scrollbar{width:8px}
.article::-webkit-scrollbar-track{background:rgba(0,0,0,.05)}
.article::-webkit-scrollbar-thumb{background:rgba(0,0,0,.15);border-radius:8px}

/* === SHARED COMPONENT STYLES === */
ul{margin:4px 0 14px 16px}
li{font-size:16px;line-height:1.55;color:#333;margin-bottom:6px;font-weight:300}
.status{font-size:12px;font-weight:700;color:#4caf50}
.status-red{font-size:12px;font-weight:700;color:#e53935}

/* === DOT NAVIGATION === */
.dots{position:fixed;bottom:24px;left:50%;transform:translateX(-50%);display:flex;gap:8px;z-index:100}
.dots button{width:8px;height:8px;border-radius:50%;border:1px solid rgba(255,255,255,.4);background:rgba(255,255,255,.2);cursor:pointer;transition:all .3s}
.dots button.active{background:#fff;transform:scale(1.3)}

/* === RESPONSIVE === */
@media(max-width:650px){
  .page{padding:10px}
  .card--cover,.card--content{width:100%;height:auto}
  .article{height:auto;overflow:visible}
}

/* === REDUCED MOTION === */
@media(prefers-reduced-motion:reduce){
  *{animation:none!important;transition:none!important;opacity:1!important;transform:none!important;clip-path:none!important}
}
```

---

## Theme 1: consulting-report (咨询报告)

**配色**: 藏蓝 `#1b2a4a` / 青 `#00a9f4` / 白底
**风格**: 专业、可信、商务

```css
:root{
  --navy:#1b2a4a;--dark:#151f35;--cyan:#00a9f4;--light-cyan:#4fc3f7;
  --text:#1a1a1a;--gray600:#555;--gray400:#999;--gray200:#e0e0e0;--gray100:#f5f5f5;--white:#fff;
  --green:#4caf50;--amber:#ffc107;--red:#e53935;
  --serif:"Noto Serif SC","Source Han Serif SC","Songti SC",Georgia,serif;
  --sans:"PingFang SC","Noto Sans SC","Microsoft YaHei",Arial,sans-serif;
}

/* Body */
body{background:linear-gradient(135deg,#0f1728,#1b2a4a 48%,#0c111d);font-family:var(--sans);color:var(--text)}

/* Cover card */
.card--cover{background:var(--navy);color:#fff;box-shadow:0 24px 48px rgba(15,25,45,.28)}
.card--cover::after{content:"";position:absolute;inset:0;pointer-events:none;border:1px solid rgba(255,255,255,.08)}

/* Cover overlay: crosshatch grid */
.card--cover .hero,
.card--content .cover{
  background:var(--navy);
  background-image:
    repeating-linear-gradient(90deg,transparent,transparent 39px,rgba(255,255,255,.035) 39px,rgba(255,255,255,.035) 40px),
    repeating-linear-gradient(0deg,transparent,transparent 39px,rgba(255,255,255,.035) 39px,rgba(255,255,255,.035) 40px);
  color:#fff;
}

/* Content card */
.card--content{background:#fff;box-shadow:0 25px 50px rgba(0,0,0,.42),0 10px 30px rgba(0,10,20,.3)}
.article{background:#fff}
.article::-webkit-scrollbar-thumb{background:#9fb4c8}

/* Cover section (content page) */
.cover{min-height:280px;padding:38px 42px;display:flex;flex-direction:column;justify-content:space-between}
.logo{font-family:var(--serif);font-size:22px;line-height:1.35}
.logo span{display:block;padding-left:1em;color:rgba(255,255,255,.78);font-weight:400}
.cover h1{font-family:var(--serif);font-size:36px;line-height:1.18;margin-bottom:16px}
.sub{font-family:var(--serif);font-size:18px;line-height:1.5;color:rgba(255,255,255,.84)}
.date{font-size:13px;color:rgba(255,255,255,.58);letter-spacing:.08em}

/* Cover page specific */
.top{position:absolute;z-index:2;top:44px;left:46px;right:46px;display:flex;justify-content:space-between;gap:22px;color:rgba(255,255,255,.62);font-size:12px;line-height:1.7;letter-spacing:.08em}
.hero{position:absolute;z-index:2;left:46px;right:46px;top:286px}
.label{margin-bottom:18px;color:rgba(255,255,255,.62);font-size:12px;letter-spacing:.12em}
.title{max-width:450px;font-family:var(--serif);font-size:52px;font-weight:700;line-height:1.14}
.footer{position:absolute;z-index:2;left:46px;right:46px;bottom:44px;display:flex;align-items:baseline;justify-content:space-between;gap:18px;border-top:1px solid rgba(255,255,255,.28);padding-top:14px;color:rgba(255,255,255,.48);font-size:11px;letter-spacing:.08em}
.firm{font-family:var(--serif);color:rgba(255,255,255,.68);letter-spacing:.12em}

/* Body area */
.body{padding:20px 34px 24px}
.breadcrumb{text-align:right;font-size:11px;color:var(--gray400);letter-spacing:.08em;margin-bottom:18px}

/* Components */
h2{font-family:var(--serif);font-size:24px;line-height:1.35;margin:20px 0 8px;color:#000}
.rule{height:1px;background:#000;margin-bottom:10px}
.exec{background:var(--gray100);border-left:4px solid var(--cyan);padding:12px 16px;margin:14px 0}
.exec p{margin:0}
p{font-size:18px;line-height:1.65;color:#333;margin-bottom:12px;font-weight:300}
strong{color:#000;font-weight:700}
.metrics{display:grid;grid-template-columns:1fr 1fr;gap:1px;background:var(--gray200);margin:14px 0 18px}
.metric{background:#fff;padding:12px}
.metric b{display:block;font-family:Georgia,serif;font-size:42px;line-height:1;color:var(--cyan);margin-bottom:8px}
.metric span{display:block;font-size:14px;font-weight:700;color:#000}
.metric small{display:block;font-size:13px;line-height:1.55;color:var(--gray600);margin-top:8px}
.table{border-top:1px solid #000;border-bottom:1px solid #000;margin:14px 0 18px}
.row{display:grid;grid-template-columns:92px 1fr 58px;gap:12px;padding:9px 0;border-bottom:1px solid var(--gray200);align-items:start}
.row:last-child{border-bottom:0}
.row b{font-size:12px;color:var(--gray400);letter-spacing:.08em}
.row span{font-size:18px;line-height:1.45;color:#111}
.status{font-size:12px;font-weight:700;color:var(--green)}
.status-red{font-size:12px;font-weight:700;color:var(--red)}
ul{margin:4px 0 14px 18px}
li{font-size:17px;line-height:1.55;color:#333;margin-bottom:8px;font-weight:300}
.source{margin-top:20px;padding-top:8px;border-top:1px solid var(--gray200);display:flex;justify-content:space-between;font-size:10px;color:var(--gray400);letter-spacing:.08em}
```

---

## Theme 2: editorial (杂志风)

**配色**: 米白 `#faf8f3` / 墨色 `#111` / 衬线为主
**风格**: 杂志排版、留白克制

```css
:root{
  --paper:#faf8f3;--ink:#111;--mid:#555;--faint:#8d8a84;--line:#e4e0d7;--accent:#111;--cream:#d8d4cc;
  --display:"Songti SC","Noto Serif SC","STSong",Georgia,serif;
  --body:"PingFang SC","Noto Sans SC","Microsoft YaHei",Arial,sans-serif;
  --mono:"SFMono-Regular","Menlo","Consolas",monospace;
}

body{
  background:radial-gradient(900px 620px at 50% -10%,rgba(250,248,243,.24),transparent 64%),linear-gradient(135deg,#232321,#34322d 50%,#191917);
  font-family:var(--body);color:var(--ink);-webkit-font-smoothing:antialiased
}

/* Card */
.card--cover,.card--content{background:var(--paper);border-radius:10px;box-shadow:0 25px 50px rgba(0,0,0,.42),0 10px 30px rgba(0,10,20,.30)}
/* SVG noise overlay */
.card::after{content:"";position:absolute;inset:0;pointer-events:none;opacity:.035;background:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='300'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.75' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")}

/* Cover page */
.card--cover{color:var(--ink)}
.card--cover .top{position:absolute;top:44px;left:46px;right:46px;display:flex;justify-content:space-between;font-size:12px;color:var(--faint);letter-spacing:.08em}
.card--cover .hero{position:absolute;left:46px;right:46px;top:260px}
.card--cover .label{font-family:var(--mono);font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--faint);margin-bottom:18px}
.card--cover .title{font-family:var(--display);font-size:52px;font-weight:900;line-height:1.14;color:var(--ink)}
.card--cover .sub{font-family:var(--display);font-size:22px;line-height:1.48;color:var(--mid);margin-top:20px}
.card--cover .footer{position:absolute;left:46px;right:46px;bottom:44px;border-top:1px solid var(--line);padding-top:14px;font-size:11px;color:var(--faint);display:flex;justify-content:space-between}

/* Content card */
.card--content{border-radius:10px}
.article{
  background:
    linear-gradient(90deg,transparent 0 45px,rgba(17,17,17,.06) 45px 46px,transparent 46px),
    linear-gradient(180deg,rgba(17,17,17,.035) 0 1px,transparent 1px 48px),
    var(--paper)
}

/* Cover section */
.cover{min-height:280px;padding:42px 46px;background:var(--paper);color:var(--ink);border-bottom:1px solid var(--line)}
.cover h1{font-family:var(--display);font-size:42px;font-weight:900;line-height:1.14}
.sub{font-family:var(--display);font-size:18px;color:var(--mid)}

/* Body */
.body{padding:24px 46px 28px}
.breadcrumb{font-family:var(--mono);font-size:10px;color:var(--faint);letter-spacing:.14em;text-transform:uppercase;text-align:right;margin-bottom:18px}

/* Components */
h2{font-family:var(--display);font-size:31px;font-weight:900;color:var(--ink);margin:24px 0 10px}
h2::before{content:"";display:block;width:44px;height:1px;background:var(--ink);margin-bottom:12px}
.rule{display:none}
p{font-family:var(--body);font-size:22px;line-height:1.82;color:#333;font-weight:300;margin-bottom:14px}
.drop:first-letter{font-family:var(--display);font-size:72px;font-weight:900;float:left;line-height:.85;margin-right:8px;color:var(--ink)}
mark{background:#111;color:var(--paper);padding:0 4px}
blockquote{border-left:3px solid var(--ink);font-family:var(--display);font-size:29px;line-height:1.55;padding:8px 0 8px 20px;color:var(--ink);margin:18px 0}
.side-note{background:#efebe2;border:1px solid var(--line);padding:14px 18px;margin:16px 0;font-size:18px;line-height:1.65}
.score{height:7px;background:#e5e1d8;border-radius:4px;margin:8px 0 16px;overflow:hidden}
.score .fill{height:100%;background:var(--ink);border-radius:4px}
.source{font-family:var(--mono);font-size:10px;letter-spacing:.14em;text-transform:uppercase;color:var(--faint);border-top:1px solid var(--line);padding-top:10px;margin-top:24px;display:flex;justify-content:space-between}
.exec{background:#efebe2;border-left:3px solid var(--ink);padding:14px 18px;margin:16px 0}
.metrics{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:16px 0}
.metric{padding:14px;border:1px solid var(--line)}
.metric b{display:block;font-family:var(--display);font-size:36px;font-weight:900;color:var(--ink);margin-bottom:4px}
.metric span{display:block;font-size:14px;font-weight:700;color:var(--ink)}
.metric small{display:block;font-size:13px;color:var(--mid);margin-top:6px}
.table{margin:16px 0}
.row{display:grid;grid-template-columns:92px 1fr 58px;gap:12px;padding:10px 0;border-bottom:1px solid var(--line);align-items:start}
.row:last-child{border-bottom:0}
.row b{font-family:var(--mono);font-size:11px;color:var(--faint);letter-spacing:.08em}
.row span{font-size:18px;line-height:1.5;color:var(--ink)}
```

---

## Theme 3: geek-report (极客风格)

**配色**: 暖灰 `#e2deda` / 荧光绿 `#c9f044` / 终端深色
**风格**: 技术文档、黑白对比

```css
:root{
  --frame:#252525;--paper:#e2deda;--ink:#292929;--soft:rgba(41,41,41,.62);
  --line:rgba(41,41,41,.18);--line-strong:rgba(41,41,41,.36);
  --red:#eb4e3d;--blue:#7f9cb4;--acid:#c9f044;--terminal:#202020;--terminal-text:#e2deda;
  --mono:Consolas,"SFMono-Regular",Menlo,Monaco,"Courier New","PingFang SC","Microsoft YaHei",monospace;
  --sans:"PingFang SC","Microsoft YaHei",Arial,sans-serif;
}

body{
  background:radial-gradient(circle at 50% 48%,rgba(226,222,218,.09),transparent 48%),repeating-linear-gradient(45deg,rgba(226,222,218,.05) 0 1px,transparent 1px 4px),#262625;
  font-family:var(--sans);color:var(--ink)
}

/* Card */
.card--cover,.card--content{background:var(--paper);border:1px solid rgba(226,222,218,.18);border-radius:8px;box-shadow:0 28px 80px rgba(0,0,0,.45),inset 0 0 54px rgba(0,0,0,.12)}
/* Grid + scanline overlays */
.card::before{content:"";position:absolute;inset:0;pointer-events:none;
  background:repeating-linear-gradient(90deg,transparent,transparent calc(100%/12 - 1px),rgba(41,41,41,.06) calc(100%/12 - 1px) calc(100%/12)),
  repeating-linear-gradient(0deg,transparent,transparent calc(100%/18 - 1px),rgba(41,41,41,.04) calc(100%/18 - 1px) calc(100%/18))}
.card::after{content:"";position:absolute;inset:0;pointer-events:none;
  background:repeating-linear-gradient(0deg,rgba(0,0,0,.03) 0 1px,transparent 1px 4px);opacity:.12}

/* Cover section */
.cover{min-height:260px;padding:36px 40px;background:var(--paper);color:var(--ink);border-bottom:1px solid var(--line-strong)}
.cover h1{font-size:46px;font-weight:700;line-height:1.12;text-transform:uppercase;letter-spacing:.02em}
.sub{font-size:18px;color:var(--soft)}

/* Body */
.body{padding:20px 36px 24px}
.breadcrumb{font-family:var(--mono);font-size:10px;color:var(--soft);letter-spacing:.08em;text-align:right;margin-bottom:16px}

/* Components */
h2{font-size:25px;font-weight:700;border-top:1px solid var(--line-strong);padding-top:14px;margin:22px 0 10px}
.rule{display:none}
p{font-size:20px;line-height:1.72;color:var(--soft);margin-bottom:12px}
mark{background:var(--acid);color:var(--ink);font-family:var(--mono);padding:0 4px}
.prompt{background:var(--terminal);color:var(--terminal-text);border:1px solid var(--line-strong);border-radius:4px;padding:16px 20px;margin:14px 0;font-family:var(--mono);font-size:14px;line-height:1.6;box-shadow:0 10px 24px rgba(0,0,0,.14)}
.prompt b{color:var(--acid);font-weight:700}
.code{background:var(--terminal);color:var(--terminal-text);font-family:var(--mono);font-size:14px;padding:14px 18px;border-radius:4px;margin:14px 0;line-height:1.6;overflow-x:auto}
.verdict{border:2px solid var(--ink);padding:16px 20px;margin:16px 0;background:rgba(235,78,61,.08)}
.verdict b{color:var(--red)}
.metrics{display:grid;grid-template-columns:1fr 1fr 1fr;gap:1px;background:var(--line-strong);margin:14px 0}
.metric{background:var(--paper);padding:12px}
.metric b{display:block;font-family:var(--mono);font-size:22px;color:var(--ink);margin-bottom:4px}
.metric span{display:block;font-size:12px;color:var(--soft)}
.table{border-top:1px solid var(--line-strong);border-bottom:1px solid var(--line-strong);margin:14px 0}
.row{display:grid;grid-template-columns:92px 1fr 58px;gap:12px;padding:9px 0;border-bottom:1px solid var(--line);align-items:start}
.row:last-child{border-bottom:0}
.row b{font-family:var(--mono);font-size:11px;color:var(--soft)}
.row span{font-size:17px;color:var(--ink)}
.exec{background:rgba(201,240,68,.08);border-left:4px solid var(--acid);padding:12px 16px;margin:14px 0;font-family:var(--mono);font-size:14px}
.source{font-family:var(--mono);font-size:10px;color:var(--soft);border-top:1px solid var(--line-strong);padding-top:10px;margin-top:20px;display:flex;justify-content:space-between}
```

---

## Theme 4: rain-notes (雨天手记)

**配色**: 纸张 `#f5eddb` / 雨蓝 `#52768e` / 暖墨
**风格**: 纸感、文艺、安静

```css
:root{
  --ink:#282824;--ink-soft:#57544d;--ink-faint:#8a8477;
  --paper:#f5eddb;--paper-deep:#ded0b3;
  --rule:rgba(52,50,46,.16);--rain:#52768e;--rain-soft:rgba(82,118,142,.56);--seal:#8b4d45;
  --serif:"Songti SC","STSong","Noto Serif SC","SimSun",serif;
  --sans:"PingFang SC","Noto Sans SC","Microsoft YaHei",Arial,sans-serif;
}

body{
  background:radial-gradient(1100px 760px at 50% -10%,rgba(250,246,235,.18),transparent 64%),linear-gradient(135deg,#1f252b 0%,#28313a 48%,#161a1e 100%);
  font-family:var(--sans);color:var(--ink)
}

/* Card */
.card--cover,.card--content{background:#d9ccb0;border-radius:14px;box-shadow:0 25px 50px rgba(0,0,0,.38),0 10px 30px rgba(0,0,0,.24)}

/* Article: paper texture */
.article{
  background-color:rgba(248,243,230,.88);
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='300'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.65' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='.18'/%3E%3C/svg%3E"),
    linear-gradient(168deg,rgba(255,250,238,.84),rgba(237,226,205,.82) 52%,rgba(218,204,174,.82))
}

/* Cover section */
.cover{min-height:280px;padding:40px 44px;background:transparent;color:var(--ink)}
.cover h1{font-family:var(--serif);font-size:48px;font-weight:300;line-height:1.18}
.cover h1 .ink{color:#15283a;font-weight:700}
.sub{font-family:var(--serif);font-size:18px;color:var(--ink-soft)}

/* Body */
.body{padding:22px 38px 26px}

/* Components */
h2{font-family:var(--serif);font-size:28px;font-weight:400;color:var(--ink);margin:22px 0 10px}
.rule{height:1px;background:var(--rule);margin-bottom:10px}
p{font-family:var(--serif);font-size:22px;line-height:1.86;color:var(--ink-soft);font-weight:300;margin-bottom:14px}
mark{background:linear-gradient(180deg,transparent 48%,rgba(255,224,104,.62) 48%);padding:0 2px}
.note{border-left:2px solid var(--rain-soft);background:rgba(255,251,239,.34);padding:14px 18px;margin:16px 0;font-size:20px;line-height:1.72}
.exec{border-left:2px solid var(--rain-soft);background:rgba(255,251,239,.34);padding:12px 16px;margin:14px 0}
/* Corner brackets */
.card--content .body::before,.card--content .body::after{content:"";position:absolute;width:13px;height:13px;border:1px solid var(--rain-soft)}
/* Stamp */
.stamp{width:54px;height:54px;border:1px solid var(--rain-soft);color:var(--rain);font-family:var(--serif);font-size:12px;display:flex;align-items:center;justify-content:center;text-align:center;border-radius:4px;transform:rotate(-8deg)}
.score{height:3px;background:rgba(82,118,142,.14);border-radius:2px;margin:8px 0 16px;overflow:hidden}
.score .fill{height:100%;background:linear-gradient(90deg,rgba(82,118,142,.52),rgba(21,40,58,.74));border-radius:2px}
.source{font-size:10px;color:var(--ink-faint);border-top:1px solid var(--rule);padding-top:10px;margin-top:20px;display:flex;justify-content:space-between}
```

---

## Theme 5: sunrise (日光)

**配色**: 暖纸 `#ece2d8` / 金 `#b48a4a` / 棕墨
**风格**: 温暖、金色点缀、衬线优雅

```css
:root{
  --ink:#2a1d14;--ink-mid:rgba(42,29,20,.70);--ink-faint:rgba(42,29,20,.48);--ink-fainter:rgba(42,29,20,.32);
  --line:rgba(42,29,20,.18);--gold:#b48a4a;--gold-soft:rgba(180,138,74,.55);--paper:#ece2d8;
  --serif:"Cormorant Garamond","EB Garamond","Noto Serif SC","Songti SC",Georgia,serif;
  --cn-serif:"Noto Serif SC","Songti SC","STSong",serif;
  --sans:"Noto Sans SC","PingFang SC","Microsoft YaHei",Arial,sans-serif;
}

body{
  background:radial-gradient(ellipse at 18% 18%,rgba(232,178,140,.32),transparent 50%),radial-gradient(ellipse at 82% 72%,rgba(206,148,158,.26),transparent 52%),#34251b;
  font-family:var(--sans);color:var(--ink)
}

/* Card */
.card--cover,.card--content{background:var(--paper);border-radius:12px;box-shadow:0 25px 50px rgba(0,0,0,.38),0 10px 30px rgba(0,0,0,.24)}
/* Grain overlay */
.card::after{content:"";position:absolute;inset:0;pointer-events:none;opacity:.045;mix-blend-mode:multiply;
  background:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='300'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.8' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")}

/* Cover section */
.cover{min-height:280px;padding:40px 44px;background:transparent;color:var(--ink)}
.cover h1{font-family:var(--cn-serif);font-size:40px;font-weight:600;line-height:1.2}
.sub{font-family:var(--cn-serif);font-size:18px;color:var(--ink-mid)}

/* Body */
.body{padding:22px 38px 26px}

/* Components */
h2{font-family:var(--cn-serif);font-size:26px;font-weight:600;color:var(--ink);margin:24px 0 10px}
h2::before{content:attr(data-num);display:block;font-family:var(--serif);font-size:14px;color:var(--gold);letter-spacing:.12em;margin-bottom:6px}
h2::after{content:"";display:block;width:60px;height:1px;background:var(--gold-soft);margin-top:8px}
.rule{display:none}
p{font-family:var(--cn-serif);font-size:24px;line-height:1.8;color:var(--ink-mid);font-weight:300;margin-bottom:14px}
mark{background:#fff2a8;border-bottom:2px solid var(--gold);padding:0 4px}
blockquote{border-top:1px solid var(--gold-soft);border-bottom:1px solid var(--gold-soft);text-align:center;font-family:var(--cn-serif);font-size:24px;padding:16px 20px;margin:18px 0;color:var(--ink)}
.note{border:1px solid var(--line);background:linear-gradient(135deg,rgba(255,250,244,.34),rgba(236,212,200,.20));padding:16px 20px;margin:16px 0;border-radius:6px}
.exec{border:1px solid var(--line);background:linear-gradient(135deg,rgba(255,250,244,.34),rgba(236,212,200,.20));padding:14px 18px;margin:14px 0;border-radius:6px}
.metrics{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:16px 0}
.metric{padding:14px;border:1px solid var(--line);border-radius:6px;background:rgba(255,250,244,.2)}
.metric b{display:block;font-family:var(--serif);font-size:36px;color:var(--gold);margin-bottom:4px}
.metric span{display:block;font-size:14px;font-weight:700;color:var(--ink)}
.metric small{display:block;font-size:13px;color:var(--ink-faint);margin-top:6px}
.source{font-size:10px;color:var(--ink-faint);border-top:1px solid var(--line);padding-top:10px;margin-top:20px;display:flex;justify-content:space-between;letter-spacing:.08em}
```

---

## Theme 6: terminal (终端风)

**配色**: 深框 `#252524` / 纸色 `#e8e6e2` / 粗黑体
**风格**: 热敏纸上的命令行输出、开发者气质

```css
:root{
  --frame:#252524;--paper:#e8e6e2;--paper-hot:#f4f2ee;
  --ink:#2d2d2c;--soft:rgba(45,45,44,.62);--faint:rgba(45,45,44,.38);
  --line:rgba(45,45,44,.16);--line-strong:rgba(45,45,44,.34);
  --terminal:#202020;--terminal-hot:#f0eee9;
  --mono:"SFMono-Regular",Consolas,Menlo,Monaco,"Courier New","PingFang SC","Microsoft YaHei",monospace;
  --sans:"Arial Black","Helvetica Neue",Arial,"PingFang SC","Noto Sans SC","Microsoft YaHei",sans-serif;
  --body:"PingFang SC","Noto Sans SC","Microsoft YaHei",Arial,sans-serif;
}

body{
  background:radial-gradient(circle at 50% 44%,rgba(232,230,226,.07),transparent 46%),repeating-linear-gradient(0deg,rgba(232,230,226,.025) 0 1px,transparent 1px 4px),#111;
  font-family:var(--body);color:var(--ink)
}

/* Card: dark frame */
.card--cover,.card--content{
  background:radial-gradient(circle at 17% 6%,rgba(255,255,255,.72),transparent 30%),radial-gradient(circle at 90% 72%,rgba(210,208,202,.34),transparent 32%),linear-gradient(180deg,var(--paper-hot),var(--paper) 58%,#dedbd5);
  border-radius:8px;box-shadow:0 30px 86px rgba(0,0,0,.54),inset 0 1px 0 rgba(255,255,255,.08);
  border:1px solid rgba(45,45,44,.2)
}
/* Scanlines on paper */
.article::after{content:"";position:absolute;inset:0;pointer-events:none;background:repeating-linear-gradient(0deg,rgba(45,45,44,.02) 0 1px,transparent 1px 4px);opacity:.11}

/* Cover section */
.cover{min-height:260px;padding:36px 40px;background:transparent;color:var(--ink)}
.cover h1{font-family:var(--sans);font-size:48px;font-weight:900;line-height:1.12}
.sub{font-size:18px;color:var(--soft)}

/* Body */
.body{padding:20px 36px 24px}

/* Components */
h2{font-family:var(--sans);font-size:25px;font-weight:900;border-top:1px solid var(--line-strong);padding-top:14px;margin:22px 0 10px}
.rule{display:none}
p{font-family:var(--body);font-size:22px;line-height:1.78;color:var(--soft);font-weight:300;margin-bottom:12px}
.prompt{background:var(--terminal);color:var(--terminal-hot);border:1px solid var(--line-strong);border-radius:4px;padding:16px 20px;margin:14px 0;font-family:var(--mono);font-size:14px;line-height:1.6}
.prompt b{font-family:var(--sans);font-weight:900;color:var(--terminal-hot)}
.code{background:var(--terminal);color:var(--terminal-hot);font-family:var(--mono);font-size:14px;padding:14px 18px;border-radius:4px;margin:14px 0}
.verdict{border:2px solid var(--ink);padding:16px 20px;margin:16px 0;background:rgba(47,47,47,.06)}
.metrics{display:grid;grid-template-columns:1fr 1fr 1fr;gap:1px;background:var(--line-strong);margin:14px 0}
.metric{background:var(--paper);padding:12px}
.metric b{display:block;font-family:var(--sans);font-size:19px;color:var(--ink);margin-bottom:4px}
.metric span{display:block;font-family:var(--mono);font-size:11px;color:var(--soft);text-transform:uppercase;letter-spacing:.06em}
.exec{background:rgba(45,45,44,.06);border-left:4px solid var(--ink);padding:12px 16px;margin:14px 0}
.source{font-family:var(--mono);font-size:10px;color:var(--faint);border-top:1px solid var(--line-strong);padding-top:10px;margin-top:20px;display:flex;justify-content:space-between}
```

---

## Theme 7: clean-review (简约测评)

**配色**: 红 `#e8382a` / 珊瑚 `#f05a3e` / 橙红渐变
**风格**: 极简、高对比、红橙主视觉

```css
:root{
  --red:#e8382a;--coral:#f05a3e;--orange:#f4845f;
  --black:#111110;--grey:#f2f0ec;--grey2:#e6e4e0;
  --text:#1a1a18;--muted:#77766e;
  --sans:"PingFang SC","Noto Sans SC","Microsoft YaHei",Arial,sans-serif;
}

body{background:linear-gradient(135deg,#1b1513,#3a1712 45%,#140f0d);font-family:var(--sans);color:var(--text)}

/* Card */
.card--cover,.card--content{background:#fff;border-radius:12px;box-shadow:0 25px 50px rgba(0,0,0,.42),0 10px 30px rgba(0,10,20,.3)}

/* Cover page hero */
.card--cover{overflow:hidden}
.card--cover .hero{background:linear-gradient(135deg,#e83028 0%,#f05a3e 45%,#f4a96a 100%);position:absolute;inset:0;display:flex;flex-direction:column;justify-content:flex-end;padding:46px;color:#fff}
.card--cover .title{font-size:54px;font-weight:900;line-height:1.04;letter-spacing:-.02em}
.card--cover .sub{font-size:22px;opacity:.85;margin-top:16px}

/* Content card: white top, grey bottom */
.article{background:linear-gradient(180deg,#fff 0,#fff 36%,var(--grey) 36%)}

/* Cover section */
.cover{min-height:300px;padding:38px 42px;background:linear-gradient(135deg,#e83028 0%,#f05a3e 45%,#f4a96a 100%);color:#fff}
.cover h1{font-size:42px;font-weight:900;line-height:1.08;letter-spacing:-.02em}
.sub{font-size:18px;opacity:.85}

/* Body */
.body{padding:22px 36px 26px}

/* Components */
h2{font-size:30px;font-weight:800;color:var(--black);margin:22px 0 10px}
.rule{height:3px;background:var(--red);margin-bottom:10px;border-radius:2px}
p{font-size:22px;line-height:1.78;color:#333;font-weight:300;margin-bottom:14px}
mark{background:rgba(240,90,62,.16);color:var(--coral);padding:0 4px}
.exec{background:var(--black);color:#fff;border-left:4px solid rgba(255,255,255,.35);padding:16px 20px;margin:14px 0;border-radius:0 8px 8px 0}
.exec p{color:#fff}
.metrics{display:grid;grid-template-columns:1fr 1fr;gap:1px;background:var(--grey2);margin:16px 0;border-radius:8px;overflow:hidden}
.metric{background:#fff;padding:16px}
.metric b{display:block;font-size:36px;font-weight:900;color:var(--red);margin-bottom:4px}
.metric span{display:block;font-size:14px;font-weight:700;color:var(--black)}
.metric small{display:block;font-size:13px;color:var(--muted);margin-top:6px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:1px;background:var(--grey2);margin:16px 0;border-radius:8px;overflow:hidden}
.cell{background:#fff;padding:16px}
.cell.dark{background:var(--black);color:#fff}
.cell b{display:block;font-size:12px;color:var(--coral);margin-bottom:6px;text-transform:uppercase;letter-spacing:.06em}
.table{margin:16px 0}
.row{display:grid;grid-template-columns:92px 1fr 58px;gap:12px;padding:10px 0;border-bottom:1px solid var(--grey2);align-items:start}
.row:last-child{border-bottom:0}
.row b{font-size:12px;color:var(--muted)}
.row span{font-size:18px;color:var(--black)}
.status{font-size:12px;font-weight:700;color:var(--coral)}
.source{font-size:10px;color:var(--muted);border-top:1px solid var(--grey2);padding-top:10px;margin-top:20px;display:flex;justify-content:space-between}
```

---

## Theme 8: dot-matrix (点阵编辑风)

**配色**: 中性 `#fbfaf6` / 低饱和灰 / 数据信号色
**风格**: 技术编辑、数据驱动、点阵画布

```css
:root{
  --bg:#deded9;--paper:#fbfaf6;--ink:#24221f;--muted:rgba(36,34,31,.66);--quiet:rgba(36,34,31,.28);
  --line:rgba(36,34,31,.18);--cyan:#3e4744;--green:#716d62;--rose:#8b7c6b;--blue:#8e9694;
  --display:"Songti SC","Noto Serif CJK SC","STSong","SimSun",serif;
  --body:"PingFang SC","Noto Sans CJK SC","Microsoft YaHei",Arial,sans-serif;
  --mono:"SFMono-Regular","Menlo","Consolas",monospace;
}

body{
  background:radial-gradient(circle at 72% 26%,rgba(142,150,148,.22),transparent 23%),radial-gradient(circle at 50% 112%,rgba(120,115,106,.18),transparent 34%),linear-gradient(90deg,rgba(251,250,246,.5),transparent 38%,rgba(222,222,217,.64)),var(--bg);
  font-family:var(--body);color:var(--ink)
}

/* Card */
.card--cover,.card--content{
  background:radial-gradient(circle at 20% 10%,rgba(62,71,68,.06),transparent 30%),var(--paper);
  border:1px solid rgba(36,34,31,.2);border-radius:10px;
  box-shadow:0 25px 50px rgba(60,56,48,.22),0 10px 30px rgba(60,56,48,.18)
}
/* Grid overlay */
.card::before{content:"";position:absolute;inset:0;pointer-events:none;
  background:repeating-linear-gradient(90deg,transparent,transparent calc(100%/12 - 1px),rgba(36,34,31,.05) calc(100%/12 - 1px) calc(100%/12)),
  repeating-linear-gradient(0deg,transparent,transparent calc(100%/20 - 1px),rgba(36,34,31,.04) calc(100%/20 - 1px) calc(100%/20))}

/* Cover section */
.cover{min-height:280px;padding:40px 44px;background:transparent;color:var(--ink)}
.cover h1{font-family:var(--display);font-size:48px;font-weight:400;color:var(--cyan);line-height:1.15}
.sub{font-family:var(--display);font-size:20px;color:var(--muted)}

/* Body */
.body{padding:22px 38px 26px}

/* Components */
h2{font-family:var(--display);font-size:34px;font-weight:400;color:var(--ink);margin:24px 0 10px}
h2 span{color:var(--rose);font-size:16px;display:block;margin-bottom:4px}
.rule{height:1px;background:var(--line);margin-bottom:10px}
p{font-size:22px;line-height:1.78;color:var(--muted);margin-bottom:14px}
blockquote{border:1px solid var(--line);background:rgba(246,244,239,.72);padding:18px 22px;margin:16px 0;font-family:var(--display);font-size:28px;line-height:1.5;color:var(--ink);border-radius:4px}
.exec{border:1px solid var(--line);background:rgba(246,244,239,.72);padding:14px 18px;margin:14px 0;border-radius:4px}
.metrics{display:grid;grid-template-columns:1fr 1fr;gap:1px;background:var(--line);margin:16px 0}
.metric{background:var(--paper);padding:14px}
.metric b{display:block;font-family:var(--mono);font-size:14px;color:var(--cyan);margin-bottom:6px;text-transform:uppercase;letter-spacing:.06em}
.metric span{display:block;font-size:28px;font-weight:700;color:var(--ink);margin-bottom:4px}
.metric small{display:block;font-size:13px;color:var(--muted)}
.score{height:3px;background:rgba(36,34,31,.1);border-radius:2px;margin:8px 0 16px;overflow:hidden}
.score .fill{height:100%;background:var(--cyan);border-radius:2px}
.source{font-family:var(--mono);font-size:10px;color:var(--quiet);border-top:1px solid var(--line);padding-top:10px;margin-top:20px;display:flex;justify-content:space-between}
```

---

## Theme 9: pixel-report (黑底闪光)

**配色**: 黑 `#070909` / 荧光 `#c7f75a` / 青灰 `#8faab2`
**风格**: 复古游戏界面、霓虹网格、赛博朋克

```css
:root{
  --black:#000;--bg:#070909;--white:#f6f7f3;--muted:rgba(246,247,243,.58);
  --line:rgba(246,247,243,.16);--line2:rgba(246,247,243,.34);
  --teal:#8faab2;--acid:#c7f75a;--amber:#f4be64;--red:#ff6d5d;
  --font:"Roboto Condensed","Arial Narrow","Helvetica Neue",Arial,"PingFang SC","Microsoft YaHei",sans-serif;
  --mono:"Courier New","Lucida Console",monospace;
}

body{background:#000;font-family:var(--font);color:var(--white)}

/* Card */
.card--cover,.card--content{
  background:
    repeating-linear-gradient(90deg,transparent,transparent 41px,rgba(246,247,243,.06) 41px 42px),
    repeating-linear-gradient(0deg,transparent,transparent 41px,rgba(246,247,243,.06) 41px 42px),
    radial-gradient(circle at 10% 10%,rgba(143,170,178,.12),transparent 30%),
    radial-gradient(circle at 90% 90%,rgba(199,247,90,.08),transparent 30%),
    linear-gradient(135deg,#000,#060808 48%,#101515);
  border:1px solid var(--line2);border-radius:8px;box-shadow:0 28px 76px rgba(0,0,0,.72)
}
/* Pixel grid overlay */
.card::after{content:"";position:absolute;inset:0;pointer-events:none;mix-blend-mode:screen;opacity:.22;
  background-image:linear-gradient(rgba(255,255,255,.06) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.04) 1px,transparent 1px);
  background-size:5px 5px,11px 11px}

/* Cover section */
.cover{min-height:260px;padding:36px 40px;background:transparent;color:var(--white)}
.cover h1{font-size:58px;font-weight:900;line-height:1.0;text-transform:uppercase}
.cover h1 .pixel{color:var(--acid);text-shadow:3px 3px 0 rgba(0,0,0,.8)}
.sub{font-size:18px;color:var(--muted)}

/* Body */
.body{padding:20px 36px 24px}

/* Components */
h2{font-size:24px;font-weight:700;text-transform:uppercase;letter-spacing:.04em;color:var(--white);border-top:1px solid var(--line2);padding-top:14px;margin:22px 0 10px}
.rule{display:none}
p{font-size:20px;line-height:1.72;color:var(--muted);margin-bottom:12px}
mark{background:var(--acid);color:#041006;padding:0 4px}
.panel{border:1px solid var(--line2);background:rgba(0,0,0,.38);box-shadow:6px 6px 0 rgba(199,247,90,.13);padding:16px 20px;margin:14px 0;border-radius:4px}
.exec{border:1px solid var(--acid);background:rgba(199,247,90,.06);padding:14px 18px;margin:14px 0;color:var(--acid);font-family:var(--mono);font-size:14px}
.metrics{display:grid;grid-template-columns:1fr 1fr;gap:1px;background:var(--line);margin:14px 0}
.metric{background:rgba(255,255,255,.04);padding:14px}
.metric b{display:block;font-family:var(--acid);font-size:34px;color:var(--acid);margin-bottom:4px}
.metric span{display:block;font-family:var(--mono);font-size:11px;color:var(--teal);text-transform:uppercase;letter-spacing:.06em}
.code{background:#000;border:1px solid var(--line2);color:var(--acid);font-family:var(--mono);font-size:14px;padding:14px 18px;border-radius:4px;margin:14px 0}
.source{font-family:var(--mono);font-size:10px;color:var(--muted);border-top:1px solid var(--line);padding-top:10px;margin-top:20px;display:flex;justify-content:space-between}
```

---

## Theme 10: shiny-tiles (镭射网格)

**配色**: 黑 `#050505` / 玻璃质感 / 银白
**风格**: 冷光、镭射玻璃、科技感

```css
:root{
  --black:#050505;--ink:#111113;--muted:#77777c;
  --panel:#e7e2df;--panel2:#d8d5d2;
  --glass:rgba(255,255,255,.68);--line:rgba(255,255,255,.55);--shadow:rgba(0,0,0,.22);
}
:root{font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif}

body{background:#050505;color:#f4f4f2}

/* Card */
.card--cover,.card--content{
  background:radial-gradient(circle at 18% 8%,rgba(220,232,246,.13),transparent 24%),radial-gradient(circle at 86% 16%,rgba(255,255,255,.1),transparent 20%),linear-gradient(135deg,#050505,#0c0c0d 48%,#050505);
  border:1px solid rgba(255,255,255,.28);border-radius:24px;
  box-shadow:0 30px 96px rgba(0,0,0,.76),inset 0 0 0 1px rgba(255,255,255,.12)
}
/* Diagonal shine + grid */
.card::before{content:"";position:absolute;inset:0;pointer-events:none;
  background:linear-gradient(110deg,transparent 0 28%,rgba(255,255,255,.075) 36%,transparent 45% 100%),
  linear-gradient(90deg,rgba(255,255,255,.028) 1px,transparent 1px),
  linear-gradient(rgba(255,255,255,.023) 1px,transparent 1px);
  background-size:auto,18px 18px,18px 18px}

/* Cover section */
.cover{min-height:260px;padding:36px 40px;background:transparent;color:#f4f4f2}
.cover h1{font-size:48px;font-weight:900;line-height:1.0}
.sub{font-size:18px;color:rgba(244,244,242,.6)}

/* Body */
.body{padding:20px 36px 24px}

/* Glass morphism */
.glass{
  background:linear-gradient(135deg,rgba(255,255,255,.94),rgba(218,224,232,.72) 42%,rgba(255,255,255,.84));
  border:1px solid rgba(255,255,255,.72);
  box-shadow:inset 0 1px 0 rgba(255,255,255,.88),inset 18px 18px 46px rgba(255,255,255,.24),inset -22px -28px 50px rgba(0,0,0,.12),0 28px 80px rgba(0,0,0,.34);
  border-radius:8px;padding:20px;color:#111113
}

/* Components */
h2{font-size:34px;font-weight:800;color:#fff;margin:24px 0 12px}
.rule{height:1px;background:rgba(255,255,255,.2);margin-bottom:10px}
p{font-size:22px;line-height:1.78;color:rgba(244,244,242,.72);margin-bottom:14px}
.tiles{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:16px 0}
.tile{padding:20px}
.tile b{display:block;font-size:11px;color:#555;margin-bottom:8px;text-transform:uppercase;letter-spacing:.06em}
.tile span{display:block;font-size:24px;font-weight:900;color:var(--ink)}
blockquote{background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.22);padding:18px 22px;margin:16px 0;border-radius:8px;font-size:26px;font-weight:800;color:#fff}
.exec{background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.22);padding:14px 18px;margin:14px 0;border-radius:8px;color:#fff}
.source{font-size:10px;color:rgba(244,244,242,.4);border-top:1px solid rgba(255,255,255,.15);padding-top:10px;margin-top:20px;display:flex;justify-content:space-between}
```

---

## Theme 11: story-field (故事集)

**配色**: 沙色 `#a89474` / 石色 `#2c2824` / 浅色 `#f4efe6`
**风格**: 电影感、档案感、安静的纪实

```css
:root{
  --sand:#a89474;--stone:#2c2824;--light:#f4efe6;
  --soft:rgba(44,40,36,.62);--line:rgba(44,40,36,.22);
  --body:"PingFang SC","Noto Sans CJK SC","Microsoft YaHei",Arial,sans-serif;
  --display:"Songti SC","Noto Serif CJK SC","STSong","Times New Roman",serif;
}

body{background:linear-gradient(135deg,#2c2824,#6f624d 52%,#201d1a);font-family:var(--body);color:var(--stone)}

/* Card */
.card--cover,.card--content{background:var(--sand);border-radius:8px;box-shadow:0 28px 76px rgba(0,0,0,.38)}
/* Grid overlay */
.card::after{content:"";position:absolute;inset:0;pointer-events:none;
  background:linear-gradient(90deg,rgba(44,40,36,.06) 1px,transparent 1px),linear-gradient(180deg,rgba(44,40,36,.05) 1px,transparent 1px);
  background-size:48px 48px}

/* Cover page */
.card--cover .frame{border:1px solid rgba(44,40,36,.35);padding:24px;background:rgba(244,239,230,.18);min-height:730px;display:flex;flex-direction:column;justify-content:space-between}
.card--cover .title{font-family:var(--display);font-size:56px;font-weight:400;text-transform:uppercase;letter-spacing:-.045em;line-height:1.05;color:var(--stone)}
.card--cover .sub{font-family:var(--display);font-size:22px;color:var(--soft);margin-top:16px}

/* Content card */
.article{background:var(--light)}

/* Cover section */
.cover{min-height:280px;padding:40px 44px;background:var(--sand);color:var(--stone)}
.cover h1{font-family:var(--display);font-size:42px;font-weight:400;text-transform:uppercase;letter-spacing:-.035em;line-height:1.1}
.sub{font-family:var(--body);font-size:18px;color:var(--soft)}

/* Body */
.body{padding:22px 38px 26px}

/* Components */
h2{font-family:var(--display);font-size:36px;font-weight:400;text-transform:uppercase;letter-spacing:-.035em;color:var(--stone);margin:24px 0 12px}
.rule{height:1px;background:var(--line);margin-bottom:10px}
p{font-family:var(--body);font-size:22px;line-height:1.68;color:var(--stone);font-weight:300;margin-bottom:14px}
blockquote{font-family:var(--display);font-size:30px;line-height:1.5;border-left:2px solid var(--stone);padding:8px 0 8px 20px;margin:18px 0;color:var(--stone)}
.field-note{border-top:1px solid var(--line);padding:16px 0;margin:16px 0}
.field-note b{font-family:var(--display);font-size:25px;display:block;margin-bottom:8px}
.exec{background:rgba(244,239,230,.5);border-left:2px solid var(--stone);padding:14px 18px;margin:14px 0}
.metrics{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:16px 0}
.metric{padding:14px;border:1px solid var(--line);background:rgba(244,239,230,.3)}
.metric b{display:block;font-family:var(--display);font-size:28px;color:var(--stone);margin-bottom:4px}
.metric span{display:block;font-size:14px;color:var(--soft)}
.source{font-size:10px;color:var(--soft);border-top:1px solid var(--line);padding-top:10px;margin-top:20px;display:flex;justify-content:space-between;letter-spacing:.08em}
```

---

## Theme 12: y2k-brand (千禧品牌)

**配色**: 铬银 / 热粉 / 赛博蓝
**风格**: 千禧网页、镀铬文字、闪光、像素窗口

```css
:root{
  --chrome:#c0c0c0;--pink:#ff69b4;--blue:#00bfff;--purple:#9b59b6;
  --black:#1a1a2e;--white:#f0f0f5;--silver:#d4d4dc;
  --hot:#ff1493;--cyber:#00d4ff;
  --sans:"Arial Black","Helvetica Neue",Arial,"PingFang SC","Noto Sans SC","Microsoft YaHei",sans-serif;
  --body:"PingFang SC","Noto Sans SC","Microsoft YaHei",Arial,sans-serif;
}

body{
  background:linear-gradient(135deg,#1a1a2e,#16213e 50%,#0f3460);
  font-family:var(--body);color:var(--black)
}

/* Card */
.card--cover,.card--content{
  background:linear-gradient(135deg,#e8e8f0,#d4d4dc 40%,#c0c0c8 60%,#e8e8f0);
  border:2px solid rgba(255,255,255,.4);border-radius:16px;
  box-shadow:0 20px 60px rgba(0,0,0,.4),inset 0 1px 0 rgba(255,255,255,.6)
}
/* Sparkle dots */
.card::after{content:"";position:absolute;inset:0;pointer-events:none;
  background:radial-gradient(2px 2px at 20% 30%,var(--pink),transparent),
  radial-gradient(2px 2px at 80% 20%,var(--cyber),transparent),
  radial-gradient(2px 2px at 60% 70%,var(--pink),transparent),
  radial-gradient(2px 2px at 30% 80%,var(--cyber),transparent),
  radial-gradient(2px 2px at 90% 60%,var(--pink),transparent);
  opacity:.6}

/* Cover section */
.cover{min-height:280px;padding:38px 42px;
  background:linear-gradient(135deg,rgba(255,105,180,.15),rgba(0,191,255,.15));
  color:var(--black)}
.cover h1{font-family:var(--sans);font-size:48px;font-weight:900;line-height:1.05;
  background:linear-gradient(135deg,var(--hot),var(--cyber));-webkit-background-clip:text;-webkit-text-fill-color:transparent;
  background-clip:text}
.sub{font-size:18px;color:var(--black);opacity:.7}

/* Body */
.body{padding:22px 36px 26px}

/* Components */
h2{font-family:var(--sans);font-size:28px;font-weight:900;color:var(--black);margin:22px 0 10px;
  background:linear-gradient(90deg,var(--hot),var(--cyber));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.rule{height:2px;background:linear-gradient(90deg,var(--pink),var(--blue));margin-bottom:10px;border-radius:2px}
p{font-size:20px;line-height:1.72;color:rgba(26,26,46,.75);margin-bottom:14px}
mark{background:linear-gradient(90deg,rgba(255,105,180,.2),rgba(0,212,255,.2));color:var(--black);padding:0 4px;border-radius:4px}
.exec{background:linear-gradient(135deg,rgba(255,105,180,.08),rgba(0,212,255,.08));border:1px solid rgba(255,105,180,.3);border-radius:12px;padding:14px 18px;margin:14px 0}
.metrics{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:16px 0}
.metric{padding:16px;border:1px solid rgba(255,255,255,.5);border-radius:12px;background:rgba(255,255,255,.4);backdrop-filter:blur(4px)}
.metric b{display:block;font-size:32px;font-weight:900;background:linear-gradient(135deg,var(--hot),var(--cyber));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin-bottom:4px}
.metric span{display:block;font-size:14px;font-weight:700;color:var(--black)}
.source{font-size:10px;color:rgba(26,26,46,.4);border-top:1px solid rgba(0,0,0,.1);padding-top:10px;margin-top:20px;display:flex;justify-content:space-between}
```

---

## 封面页通用布局

封面页（第 0 页）的布局在各主题下略有差异，但基本结构一致。下方 CSS 只描述通用位置关系，实际尺寸同样由 `gen_draft.py` 按 `aspect_ratio` 生成。

```css
/* Cover page card */
.card--cover{position:relative;color:#fff}

/* Top bar: logo + meta */
.top{position:absolute;top:44px;left:46px;right:46px;display:flex;justify-content:space-between;align-items:flex-start;gap:22px;font-size:12px;line-height:1.7;letter-spacing:.08em}
.logo{font-size:23px;font-weight:600;line-height:1.35}
.logo span{display:block;padding-left:1em;font-weight:400;opacity:.78}

/* Hero section */
.hero{position:absolute;left:46px;right:46px;top:286px}
.label{font-size:12px;letter-spacing:.12em;opacity:.62;margin-bottom:18px}
.title{font-size:52px;font-weight:700;line-height:1.14}
.sub{font-size:22px;line-height:1.48;opacity:.82;margin-top:20px}

/* Footer */
.footer{position:absolute;left:46px;right:46px;bottom:44px;display:flex;justify-content:space-between;align-items:baseline;gap:18px;border-top:1px solid rgba(255,255,255,.28);padding-top:14px;font-size:11px;letter-spacing:.08em;opacity:.6}
```

---

## 动画系统（所有主题通用）

动画由播放引擎按音频时间轴驱动：音频到达每段旁白的开始时间后，引擎给对应元素加上 `.visible`。元素初始隐藏由 `initElements()` 设置内联 `opacity:0`，不要再用 `.page:not(.in-view)` 这类规则控制显隐。

```css
/* -- Base transition for all animatable elements -- */
.cover > *,
#cover-label, #cover-title, #cover-subtitle,
#cover-tags, #cover-footer,
.body > .breadcrumb,
.body > h2, .body > .rule,
.body > .exec, .body > p,
.body > ul, .body > .table,
.body > blockquote, .body > .source,
.body > .metrics, .body > .grid {
  opacity: 0;
  transform: translateY(20px);
  transition: opacity .75s cubic-bezier(.22,1,.36,1),
              transform .75s cubic-bezier(.22,1,.36,1);
}

/* -- When .visible is added by timeline JS -- */
.cover > *.visible,
#cover-label.visible, #cover-title.visible, #cover-subtitle.visible,
#cover-tags.visible, #cover-footer.visible,
.visible {
  opacity: 1 !important;
  transform: translateY(0) !important;
}

/* -- Keyframes for staggered children -- */
@keyframes fadeUp         { from { opacity:0; transform:translateY(24px) } to { opacity:1; transform:translateY(0) } }
@keyframes slideFromLeft  { from { opacity:0; transform:translateX(-40px) } to { opacity:1; transform:translateX(0) } }
@keyframes slideFromRight { from { opacity:0; transform:translateX(40px) } to { opacity:1; transform:translateX(0) } }
@keyframes scaleBounce    { 0% { opacity:0; transform:scale(.82) } 65% { opacity:1; transform:scale(1.05) } 100% { opacity:1; transform:scale(1) } }
@keyframes clipWipe       { from { opacity:0; clip-path:inset(0 100% 0 0) } to { opacity:1; clip-path:inset(0 0 0 0) } }
@keyframes emphasize      { 0% { opacity:0; transform:translateY(14px) scale(.97) } 50% { opacity:1; transform:translateY(0) scale(1.02) } 100% { opacity:1; transform:scale(1) } }

/* -- Staggered children: list items -- */
.visible li,
.visible .row {
  opacity: 0;
  animation: fadeUp .55s cubic-bezier(.22,1,.36,1) forwards;
}
.visible li:nth-child(1), .visible .row:nth-child(1) { animation-delay: 0s }
.visible li:nth-child(2), .visible .row:nth-child(2) { animation-delay: .12s }
.visible li:nth-child(3), .visible .row:nth-child(3) { animation-delay: .24s }
.visible li:nth-child(4), .visible .row:nth-child(4) { animation-delay: .36s }
.visible li:nth-child(5), .visible .row:nth-child(5) { animation-delay: .48s }

/* -- Alternate table row directions -- */
.visible .row:nth-child(odd)  { animation-name: slideFromLeft }
.visible .row:nth-child(even) { animation-name: slideFromRight }
```

---

## 导航脚本

播放引擎已经内置圆点导航、滚动同步和 URL 页码状态，实现在 `gen_draft.py` 的播放脚本里，不需要额外引入 JavaScript。行为约定如下：

- 圆点按钮调用 `goTo(i)` 切页；
- 滚动停止后同步当前页状态；
- URL hash 使用 `#page=N` 记录页码。
