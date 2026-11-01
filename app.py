"""app.py - Birthday Quest UI. Game rules, content and image magic live in engine.py."""
import json
import random

import streamlit as st
import streamlit.components.v1 as components

import engine as eg
from engine import CONFIG

st.set_page_config(page_title="Birthday Quest", page_icon="🎂", layout="centered")

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@400;500;600;700&family=Pacifico&display=swap');
:root{--beige:#F5EBDD;--pink:#F7C6D0;--brown:#6F4E37;--cream:#FFF8F0;--rose:#E88AA0;}
.stApp, .stApp p, .stApp label, .stApp li, .stApp button, .stApp input, .stApp textarea, .stApp h1, .stApp h2, .stApp h3, .stApp h4{font-family:'Quicksand',sans-serif !important;color:var(--brown);}
.stApp{background:linear-gradient(160deg,var(--beige),var(--pink));}
[data-testid="stHeader"]{background:transparent;}
#MainMenu, footer{visibility:hidden;}
.block-container{position:relative;z-index:1;padding-top:1.2rem;max-width:860px;}
[data-testid="stSidebar"]{background:var(--beige);border-right:3px dashed var(--pink);}
.stButton>button, .stDownloadButton>button{width:100%;border-radius:999px;border:2px solid var(--brown);background:var(--pink);color:var(--brown);font-weight:700;box-shadow:0 4px 0 var(--brown);transition:all .15s;padding:.55rem 1rem;}
.stButton>button p, .stDownloadButton>button p{color:var(--brown);font-weight:700;}
.stButton>button:hover, .stDownloadButton>button:hover{transform:translateY(-2px) rotate(-1deg);background:#fbd6de;border-color:var(--brown);color:var(--brown);}
.stButton>button:active{transform:translateY(3px);box-shadow:0 1px 0 var(--brown);}
.stButton>button:disabled{opacity:.5;}
[class*="st-key-gift"] button, [class*="st-key-mem"] button{min-height:118px;background:repeating-linear-gradient(45deg,var(--pink),var(--pink) 10px,#fbdce3 10px,#fbdce3 20px);border-radius:22px;}
[class*="st-key-gift"] button p, [class*="st-key-mem"] button p{font-size:2.3rem;}
.stTextInput input{border-radius:16px;border:2px solid var(--brown);background:var(--cream);color:var(--brown);}
.stRadio label{background:var(--cream);border:2px solid var(--pink);border-radius:16px;padding:.35rem .8rem;margin:.2rem 0;}
div[role="progressbar"] > div{background:var(--rose) !important;}
.cute-card{background:var(--cream);border:3px solid var(--pink);border-radius:28px;padding:1.1rem 1.4rem;box-shadow:0 10px 25px rgba(111,78,55,.18);margin:.8rem 0;}
.card-title{font-family:'Pacifico',cursive !important;font-size:1.7rem;line-height:1.3;}
.card-sub{opacity:.85;}
.banner img{width:100%;border-radius:26px;border:4px solid var(--pink);box-shadow:0 10px 25px rgba(111,78,55,.2);display:block;}
.hero{display:flex;align-items:center;gap:1rem;margin:.7rem 0;}
.hero img{width:88px;height:88px;filter:drop-shadow(0 6px 8px rgba(111,78,55,.25));}
.app-title{font-family:'Pacifico',cursive !important;font-size:2.1rem;line-height:1.1;}
.bd-title{font-family:'Pacifico',cursive !important;font-size:clamp(2.3rem,8vw,4.2rem);text-align:center;color:var(--brown);text-shadow:3px 3px 0 var(--pink);margin:.4rem 0 .8rem 0;}
.bd-title span{display:inline-block;animation:bounce 1.6s ease-in-out infinite;}
.chip{display:inline-block;background:var(--cream);border:2px solid var(--pink);border-radius:999px;padding:.2rem .8rem;margin:.15rem;font-weight:700;box-shadow:0 3px 8px rgba(111,78,55,.15);}
.reveal{background:var(--cream);border:3px dashed var(--pink);border-radius:22px;padding:.7rem;text-align:center;min-height:118px;display:flex;align-items:center;justify-content:center;animation:pop .45s ease;box-shadow:0 6px 14px rgba(111,78,55,.15);font-weight:600;}
.reveal img{width:100%;border-radius:12px;display:block;}
.mem-face{background:var(--cream);border-radius:20px;border:3px solid var(--pink);padding:4px;animation:pop .35s ease;box-shadow:0 6px 14px rgba(111,78,55,.18);}
.mem-face img{width:100%;border-radius:14px;display:block;}
.mem-face.matched{border-color:var(--rose);box-shadow:0 0 18px rgba(232,138,160,.8);}
.big-emoji{font-size:5rem;text-align:center;animation:bounce 2s ease-in-out infinite;}
.candles{text-align:center;font-size:2.4rem;letter-spacing:.3rem;}
.candles span{display:inline-block;animation:flicker .9s ease-in-out infinite;}
.collage img{width:100%;border-radius:26px;border:4px solid var(--pink);box-shadow:0 10px 25px rgba(111,78,55,.2);display:block;}
.float-layer{position:fixed;inset:0;pointer-events:none;overflow:hidden;z-index:0;opacity:.75;}
.float-item{position:absolute;top:0;animation:rise linear infinite;}
.confetti{position:fixed;top:0;pointer-events:none;z-index:0;animation:fall linear infinite;border-radius:2px;}
@keyframes bounce{0%,100%{transform:translateY(0)}50%{transform:translateY(-14px)}}
@keyframes rise{from{transform:translateY(105vh) rotate(-8deg);opacity:0}10%{opacity:.9}to{transform:translateY(-15vh) rotate(8deg);opacity:0}}
@keyframes fall{from{transform:translateY(-10vh) rotate(0deg)}to{transform:translateY(110vh) rotate(720deg)}}
@keyframes twinkle{0%,100%{opacity:.3;transform:scale(.8)}50%{opacity:1;transform:scale(1.2)}}
@keyframes flicker{0%,100%{transform:scale(1) rotate(-3deg)}50%{transform:scale(1.15) rotate(3deg)}}
@keyframes pop{0%{transform:scale(.3);opacity:0}70%{transform:scale(1.08)}100%{transform:scale(1);opacity:1}}
.sparkle{display:inline-block;animation:twinkle 1.8s ease-in-out infinite;}
@media (max-width:640px){
  div[data-testid="stHorizontalBlock"]{flex-direction:row !important;flex-wrap:wrap !important;}
  div[data-testid="stColumn"], div[data-testid="column"]{min-width:calc(33% - 1rem) !important;flex:1 1 calc(33% - 1rem) !important;}
}
"""


def h(s: str) -> str:
    """Strip indentation / blank lines so Markdown never turns HTML into a code block."""
    return "\n".join(line.strip() for line in s.strip().splitlines() if line.strip())


def md(html: str) -> None:
    st.markdown(h(html), unsafe_allow_html=True)


def fill(text: str) -> str:
    return text.replace("{name}", st.session_state.get("name") or CONFIG["default_name"])


# -----------------------------------------------------------------------------
# Decor
# -----------------------------------------------------------------------------
def floating_layer(items, n=16, seed=1):
    rnd = random.Random(seed)
    out = []
    for _ in range(n):
        out.append(
            f'<span class="float-item" style="left:{rnd.randint(0, 96)}%;'
            f'font-size:{rnd.randint(18, 40)}px;animation-delay:-{rnd.uniform(0, 10):.1f}s;'
            f'animation-duration:{rnd.uniform(9, 18):.1f}s">{rnd.choice(items)}</span>')
    md(f'<div class="float-layer">{"".join(out)}</div>')


def confetti_layer(n=70, seed=3):
    rnd = random.Random(seed)
    colors = ["#F7C6D0", "#E88AA0", "#F5EBDD", "#6F4E37", "#FBD9E0", "#F6D58E"]
    out = []
    for _ in range(n):
        w, hh = rnd.randint(6, 12), rnd.randint(8, 16)
        out.append(
            f'<span class="confetti" style="left:{rnd.randint(0, 99)}%;width:{w}px;height:{hh}px;'
            f'background:{rnd.choice(colors)};animation-delay:-{rnd.uniform(0, 8):.1f}s;'
            f'animation-duration:{rnd.uniform(4, 9):.1f}s"></span>')
    md("".join(out))


def title_html(text: str) -> str:
    spans = []
    for i, ch in enumerate(text):
        ch = "&nbsp;" if ch == " " else ch
        spans.append(f'<span style="animation-delay:{i * 0.08:.2f}s">{ch}</span>')
    return f'<div class="bd-title">{"".join(spans)}</div>'


def card(title: str, sub: str = "") -> None:
    md(f'<div class="cute-card"><div class="card-title">{title}</div><div class="card-sub">{sub}</div></div>')


# -----------------------------------------------------------------------------
# State + assets
# -----------------------------------------------------------------------------
GAME_KEYS = ["stage", "name", "gifts", "gift_open", "mem", "mem_msg", "quiz",
             "candles_blown", "just_blown", "card_bytes", "name_input"]


def init_state():
    ss = st.session_state
    ss.setdefault("stage", "welcome")
    ss.setdefault("name", "")
    ss.setdefault("gifts", [])
    ss.setdefault("gift_open", [])
    ss.setdefault("mem", {"deck": [], "flipped": [], "matched": [], "moves": 0})
    ss.setdefault("mem_msg", "Flip two cards to find a matching pair.")
    ss.setdefault("quiz", {"idx": 0, "correct": 0, "checked": False, "last_ok": None, "last_choice": None})
    ss.setdefault("candles_blown", False)
    ss.setdefault("just_blown", False)


def build_assets(photos, using_samples, sig):
    caps = CONFIG["captions"]
    bcols = max(3, min(6, len(photos)))
    banner = eg.scrapbook(photos, size=(1400, 340), cols=bcols, rows=1, seed=11, captions=caps)
    bg = eg.blurred_bg(photos, size=(1000, 700), tint=eg.PINK, strength=0.62)
    return {
        "sig": sig,
        "photos": photos,
        "using_samples": using_samples,
        "gift_uris": [eg.to_data_uri(eg.polaroid(p, caps[i % len(caps)], size=240)) for i, p in enumerate(photos)],
        "mem_uris": [eg.to_data_uri(eg.polaroid(p, "", size=170)) for p in photos],
        "banner_uri": eg.to_data_uri(banner, 80),
        "bg_uri": eg.to_data_uri(bg, 60),
        "avatar_uri": eg.to_data_uri(eg.circle_avatar(photos[0], 200)),
        "collage_uri": None,
    }


def snapshot() -> dict:
    ss = st.session_state
    deck = ss.mem["deck"]
    return {
        "gifts_opened": len(ss.gift_open), "gifts_total": len(ss.gifts),
        "pairs_matched": len(ss.mem["matched"]) // 2, "pairs_total": len(deck) // 2,
        "memory_moves": ss.mem["moves"],
        "quiz_correct": ss.quiz["correct"], "quiz_total": len(CONFIG["quiz"]),
        "quiz_finished": ss.quiz["idx"] >= len(CONFIG["quiz"]),
        "candles_blown": ss.candles_blown,
    }


def stats_bar():
    s = eg.compute_score(snapshot())
    chips = [f'<span class="chip">⭐ {s["stars"]}</span>',
             f'<span class="chip">💖 {s["hearts"]}</span>',
             f'<span class="chip">🏆 {s["points"]} pts</span>']
    chips += [f'<span class="chip">{b}</span>' for b in s["badges"]]
    md(f'<div>{"".join(chips)}</div>')


def progress_bar():
    sn = snapshot()
    done = [
        sn["gifts_total"] > 0 and sn["gifts_opened"] >= sn["gifts_total"],
        sn["pairs_total"] > 0 and sn["pairs_matched"] >= sn["pairs_total"],
        sn["quiz_finished"],
        sn["candles_blown"],
    ]
    st.progress(sum(done) / 4, text=f"Quest progress: {sum(done)}/4 levels complete")


def go(stage: str):
    st.session_state.stage = stage
    st.rerun()


def restart():
    for k in GAME_KEYS:
        st.session_state.pop(k, None)


# -----------------------------------------------------------------------------
# Sidebar + assets
# -----------------------------------------------------------------------------
init_state()
ss = st.session_state

with st.sidebar:
    st.markdown("### 📸 Your photos")
    uploads = st.file_uploader("Add photos", type=["png", "jpg", "jpeg", "webp"],
                               accept_multiple_files=True)
    st.caption("You can also drop photos into an `images/` folder next to app.py. "
               "No photos? Cute sample pictures are used.")
    st.toggle("🎵 Background music", key="music")
    if ss.get("music"):
        try:
            st.audio(CONFIG["music_url"], format="audio/mp3", loop=True, autoplay=True)
        except TypeError:
            st.audio(CONFIG["music_url"], format="audio/mp3")
        st.caption("If your browser blocks autoplay, press play once.")
    st.divider()
    if st.button("🔄 Restart quest", key="restart"):
        restart()
        st.rerun()

sig = eg.photos_signature(uploads)
if ss.get("assets", {}).get("sig") != sig:
    photos, using_samples = eg.load_photos(uploads)
    ss["assets"] = build_assets(photos, using_samples, sig)
A = ss["assets"]

st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)
st.markdown(
    "<style>.stApp{background:linear-gradient(rgba(245,235,221,.80),rgba(247,198,208,.55)),"
    f"url({A['bg_uri']}) center/cover fixed;}}</style>", unsafe_allow_html=True)

floating_layer(["🎈", "💖", "🎀", "✨", "🌸"], n=14, seed=1)
md(f'<div class="banner"><img src="{A["banner_uri"]}"/></div>')
if A["using_samples"]:
    st.caption("Showing sample pictures. Upload your own photos in the sidebar. 📸")


# -----------------------------------------------------------------------------
# Screens
# -----------------------------------------------------------------------------
def screen_welcome():
    md(title_html("Happy Birthday!"))
    md('<div style="text-align:center;font-size:2rem">🎀 🎈 💖 🎂 💖 🎈 🎀</div>')
    card("Welcome to Birthday Quest ✨",
         "Three tiny levels and one big surprise are waiting for you. Who is the birthday star?")
    name = st.text_input("Birthday star's name", key="name_input", placeholder=CONFIG["default_name"])
    if st.button("🎁 Start the quest", key="start"):
        ss.name = name.strip() or CONFIG["default_name"]
        n = len(A["photos"])
        ss.gifts = eg.build_gifts(CONFIG["gift_count"], n)
        ss.gift_open = []
        ss.mem = eg.build_memory(CONFIG["memory_pairs"], n)
        ss.mem_msg = "Flip two cards to find a matching pair."
        ss.quiz = {"idx": 0, "correct": 0, "checked": False, "last_ok": None, "last_choice": None}
        ss.candles_blown = False
        go("gifts")


def hero():
    md(f'<div class="hero"><img src="{A["avatar_uri"]}"/><div><div class="app-title">Birthday Quest</div>'
       f'<div>for <b>{ss.name}</b> <span class="sparkle">✨</span></div></div></div>')
    progress_bar()
    stats_bar()


def screen_gifts():
    hero()
    card("Level 1 · Gift Hunt 🎁", "Tap every gift box to reveal a sweet surprise.")
    cols = st.columns(3)
    for i, g in enumerate(ss.gifts):
        with cols[i % 3]:
            if i in ss.gift_open:
                if g["kind"] == "photo":
                    uri = A["gift_uris"][g["idx"] % len(A["gift_uris"])]
                    md(f'<div class="reveal"><img src="{uri}"/></div>')
                else:
                    md(f'<div class="reveal">{fill(g["text"])}</div>')
            elif st.button("🎁", key=f"gift{i}"):
                ss.gift_open.append(i)
                st.rerun()
    if len(ss.gift_open) >= len(ss.gifts):
        st.success("All gifts opened! 💖")
        if st.button("Next level: Memory Match 🃏", key="gifts_next"):
            go("memory")


def screen_memory():
    hero()
    card("Level 2 · Memory Match 🃏", "Find all the matching photo pairs. Fewer moves means more stars!")
    mem = ss.mem
    deck = mem["deck"]
    st.markdown(f"**{ss.mem_msg}**  ·  Moves: {mem['moves']}")
    ncols = 4
    for r in range(0, len(deck), ncols):
        cols = st.columns(ncols)
        for c, i in zip(cols, range(r, min(r + ncols, len(deck)))):
            with c:
                if i in mem["matched"] or i in mem["flipped"]:
                    cls = "mem-face matched" if i in mem["matched"] else "mem-face"
                    uri = A["mem_uris"][deck[i]["photo"] % len(A["mem_uris"])]
                    md(f'<div class="{cls}"><img src="{uri}"/></div>')
                elif st.button("💖", key=f"mem{i}"):
                    res = eg.memory_flip(mem, i)
                    ss.mem_msg = {"match": "💖 It's a match!",
                                  "miss": "Oops, not a pair. Tap any card to try again.",
                                  "first": "Nice! Now find its twin."}.get(res, ss.mem_msg)
                    st.rerun()
    if len(mem["matched"]) >= len(deck) and deck:
        st.success(f"You matched everything in {mem['moves']} moves! 🎉")
        if st.button("Next level: Birthday Quiz 🎂", key="mem_next"):
            go("quiz")


def screen_quiz():
    hero()
    quiz, items = ss.quiz, CONFIG["quiz"]
    total = len(items)
    if quiz["idx"] >= total:
        card("Quiz complete! 🎂", f"You got <b>{quiz['correct']} / {total}</b> right. "
             + ("You really know them! 🍰" if quiz["correct"] >= total * 0.8 else "Sweet effort! 💕"))
        if st.button("Go to the final surprise 🎉", key="quiz_done"):
            go("final")
        return
    item = items[quiz["idx"]]
    card(f"Level 3 · Birthday Quiz 🎂", f"Question {quiz['idx'] + 1} of {total}")
    choice = st.radio(fill(item["q"]), item["options"], index=None,
                      key=f"quiz_choice_{quiz['idx']}", disabled=quiz["checked"])
    if not quiz["checked"]:
        if st.button("Lock it in ✨", key="quiz_lock", disabled=choice is None):
            ok = item["options"].index(choice) == item["answer"]
            quiz["checked"], quiz["last_ok"] = True, ok
            quiz["correct"] += int(ok)
            st.rerun()
    else:
        if quiz["last_ok"]:
            st.success("Yes! +30 points 🎉")
        else:
            st.error(f"Not quite! The answer was: {item['options'][item['answer']]} 💕")
        if st.button("Next ➜", key="quiz_next"):
            quiz["idx"] += 1
            quiz["checked"], quiz["last_ok"] = False, None
            st.rerun()


def typewriter(text: str):
    safe = json.dumps(text).replace("</", "<\\/")
    height = int(70 + (len(text) / 55 + text.count("\n")) * 30)
    html = """
    <link href="https://fonts.googleapis.com/css2?family=Quicksand:wght@500;700&display=swap" rel="stylesheet">
    <div style="background:#FFF8F0;border:3px solid #F7C6D0;border-radius:28px;padding:22px 26px;
                box-shadow:0 10px 25px rgba(111,78,55,.18);font-family:'Quicksand',sans-serif;
                color:#6F4E37;font-size:19px;line-height:1.6;white-space:pre-wrap;" id="t"></div>
    <style>#t::after{content:'▌';color:#E88AA0;animation:b 1s steps(1) infinite}@keyframes b{50%{opacity:0}}</style>
    <script>
      const text = __TEXT__; const el = document.getElementById('t'); let i = 0;
      function step(){ if(i <= text.length){ el.textContent = text.slice(0, i); i++;
        setTimeout(step, text[i-1] === '\\n' ? 260 : 30); } }
      step();
    </script>
    """.replace("__TEXT__", safe)
    components.html(html, height=min(height, 900), scrolling=True)


def screen_final():
    hero()
    if ss.just_blown:
        st.balloons()
        ss.just_blown = False
    if not ss.candles_blown:
        card("Final Level · Make a wish 🕯️", "Close your eyes, make a wish, then blow out the candles!")
        md('<div class="candles">' + "".join(
            f'<span style="animation-delay:{i * .15:.2f}s">🕯️</span>' for i in range(5)) + "</div>")
        md('<div class="big-emoji">🎂</div>')
        if st.button("🌬️ Blow out the candles", key="blow"):
            ss.candles_blown = True
            ss.just_blown = True
            st.rerun()
        return

    confetti_layer()
    floating_layer(["🎈", "🎈", "🎉", "💖", "✨"], n=18, seed=5)
    md(title_html(f"Happy Birthday, {ss.name}!"))
    md('<div class="big-emoji">🎉</div>')
    typewriter(fill(CONFIG["letter"]))

    if A["collage_uri"] is None:
        cols_n, rows_n = eg.grid_for(len(A["photos"]))
        collage = eg.scrapbook(A["photos"], size=(1200, 360 * rows_n), cols=cols_n, rows=rows_n,
                               seed=21, captions=CONFIG["captions"])
        A["collage_uri"] = eg.to_data_uri(collage, 80)
    card("Our scrapbook 📖", "All your favourite moments in one place.")
    md(f'<div class="collage"><img src="{A["collage_uri"]}"/></div>')

    s = eg.compute_score(snapshot())
    card("Your quest results 🏆", f"⭐ {s['stars']} stars · 💖 {s['hearts']} hearts · {s['points']} points")
    md('<div>' + "".join(f'<span class="chip">{b}</span>' for b in s["badges"]) + "</div>")

    if ss.get("card_bytes") is None:
        ss.card_bytes = eg.birthday_card(ss.name, A["photos"], CONFIG["card_message"])
    st.download_button("💌 Download your birthday card", data=ss.card_bytes,
                       file_name="birthday_card.png", mime="image/png", key="dl_card")
    if st.button("🔁 Play again", key="again"):
        restart()
        st.rerun()


STAGES = {"welcome": screen_welcome, "gifts": screen_gifts, "memory": screen_memory,
          "quiz": screen_quiz, "final": screen_final}
STAGES.get(ss.stage, screen_welcome)()
