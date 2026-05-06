"""
games/quiz_game.py — Streamlit-native Quiz Game (no canvas needed).
"""
from __future__ import annotations
import time
import random
import logging
import streamlit as st
from utils.db import add_score
from utils.session import get_player_name

logger = logging.getLogger(__name__)

# ── Question Bank (50+ questions) ────────────────────────────────────────────
QUESTIONS = [
    # Technology
    {"id":"q001","category":"Technology","difficulty":"Easy","question":"What does CPU stand for?","options":["Central Processing Unit","Computer Personal Unit","Central Program Utility","Computed Processing Unit"],"answer":0,"explanation":"CPU = Central Processing Unit — the brain of a computer."},
    {"id":"q002","category":"Technology","difficulty":"Easy","question":"What does HTML stand for?","options":["HyperText Markup Language","High Transfer Markup Logic","HyperText Machine Language","Hyper Transfer Markup Language"],"answer":0,"explanation":"HTML = HyperText Markup Language, used to build web pages."},
    {"id":"q003","category":"Technology","difficulty":"Medium","question":"Which language is primarily used for styling web pages?","options":["JavaScript","Python","CSS","SQL"],"answer":2,"explanation":"CSS (Cascading Style Sheets) controls the visual presentation of web pages."},
    {"id":"q004","category":"Technology","difficulty":"Medium","question":"What does API stand for?","options":["Application Programming Interface","Automated Program Integrator","Applied Protocol Instance","Application Protocol Index"],"answer":0,"explanation":"API = Application Programming Interface — a contract for software components to communicate."},
    {"id":"q005","category":"Technology","difficulty":"Hard","question":"What is the time complexity of binary search?","options":["O(n)","O(n²)","O(log n)","O(1)"],"answer":2,"explanation":"Binary search halves the search space each step → O(log n)."},
    {"id":"q006","category":"Technology","difficulty":"Hard","question":"Which sorting algorithm has the best average-case time complexity?","options":["Bubble Sort","Insertion Sort","Merge Sort","Quick Sort"],"answer":3,"explanation":"QuickSort averages O(n log n) with very low constants in practice."},
    {"id":"q007","category":"Technology","difficulty":"Medium","question":"What does 'RAM' stand for?","options":["Random Access Memory","Read-only Active Memory","Rapid Array Module","Remote Access Module"],"answer":0,"explanation":"RAM = Random Access Memory — volatile memory used while a computer is running."},
    {"id":"q008","category":"Technology","difficulty":"Easy","question":"Which company created the Python language?","options":["Google","Guido van Rossum","Microsoft","Oracle"],"answer":1,"explanation":"Python was created by Guido van Rossum and first released in 1991."},
    {"id":"q009","category":"Technology","difficulty":"Hard","question":"What does SOLID stand for in software engineering?","options":["Single, Open, Liskov, Interface, Dependency","Simple, Object, Logic, Interface, Design","Structured, Open, Linked, Integrated, Dependency","Single, Optimized, Linked, Interface, Design"],"answer":0,"explanation":"SOLID = Single responsibility, Open-closed, Liskov substitution, Interface segregation, Dependency inversion."},
    {"id":"q010","category":"Technology","difficulty":"Medium","question":"What is a 'Git branch'?","options":["A backup of the repo","A parallel line of development","A merge conflict","A remote repository"],"answer":1,"explanation":"A Git branch is an independent line of development that can be merged later."},

    # Science
    {"id":"q011","category":"Science","difficulty":"Easy","question":"What is the chemical symbol for water?","options":["WA","H2O","HO","W2H"],"answer":1,"explanation":"Water is composed of 2 hydrogen atoms and 1 oxygen atom → H₂O."},
    {"id":"q012","category":"Science","difficulty":"Easy","question":"How many planets are in our Solar System?","options":["7","8","9","10"],"answer":1,"explanation":"There are 8 recognised planets after Pluto was reclassified in 2006."},
    {"id":"q013","category":"Science","difficulty":"Medium","question":"What is the speed of light (approx)?","options":["300,000 km/s","150,000 km/s","1,080,000 km/h","186,000 mph"],"answer":0,"explanation":"Light travels at ~299,792 km/s in a vacuum."},
    {"id":"q014","category":"Science","difficulty":"Medium","question":"What force keeps planets in orbit around the sun?","options":["Magnetism","Gravity","Electromagnetism","Nuclear force"],"answer":1,"explanation":"Gravity is the attractive force between masses that keeps planets in orbit."},
    {"id":"q015","category":"Science","difficulty":"Hard","question":"What particle has no electric charge?","options":["Proton","Electron","Neutron","Positron"],"answer":2,"explanation":"Neutrons carry no electric charge; protons are positive, electrons negative."},
    {"id":"q016","category":"Science","difficulty":"Hard","question":"What is the atomic number of Carbon?","options":["6","12","8","14"],"answer":0,"explanation":"Carbon has atomic number 6 (6 protons)."},
    {"id":"q017","category":"Science","difficulty":"Easy","question":"What gas do plants absorb during photosynthesis?","options":["Oxygen","Nitrogen","Carbon Dioxide","Hydrogen"],"answer":2,"explanation":"Plants absorb CO₂ and release O₂ during photosynthesis."},
    {"id":"q018","category":"Science","difficulty":"Medium","question":"What is the powerhouse of the cell?","options":["Nucleus","Ribosome","Mitochondria","Golgi apparatus"],"answer":2,"explanation":"Mitochondria produce ATP — the energy currency of the cell."},
    {"id":"q019","category":"Science","difficulty":"Hard","question":"What theory describes the large-scale structure of space-time?","options":["Quantum mechanics","String theory","General relativity","Special relativity"],"answer":2,"explanation":"Einstein's General Relativity describes gravity as curvature of space-time."},
    {"id":"q020","category":"Science","difficulty":"Medium","question":"Which element is the most abundant in Earth's atmosphere?","options":["Oxygen","Carbon Dioxide","Argon","Nitrogen"],"answer":3,"explanation":"Nitrogen makes up ~78% of Earth's atmosphere."},

    # History
    {"id":"q021","category":"History","difficulty":"Easy","question":"In which year did World War II end?","options":["1943","1944","1945","1946"],"answer":2,"explanation":"WWII ended in 1945: Germany surrendered in May, Japan in September."},
    {"id":"q022","category":"History","difficulty":"Easy","question":"Who was the first President of the United States?","options":["Abraham Lincoln","Thomas Jefferson","John Adams","George Washington"],"answer":3,"explanation":"George Washington served as the 1st US President (1789–1797)."},
    {"id":"q023","category":"History","difficulty":"Medium","question":"The Renaissance began in which country?","options":["France","England","Italy","Spain"],"answer":2,"explanation":"The Renaissance started in the Italian city-states in the 14th century."},
    {"id":"q024","category":"History","difficulty":"Medium","question":"Which empire was the largest in history by land area?","options":["Roman Empire","British Empire","Mongol Empire","Ottoman Empire"],"answer":2,"explanation":"The Mongol Empire at its peak covered ~24 million km²."},
    {"id":"q025","category":"History","difficulty":"Hard","question":"What year did the Berlin Wall fall?","options":["1987","1989","1991","1993"],"answer":1,"explanation":"The Berlin Wall fell on November 9, 1989."},
    {"id":"q026","category":"History","difficulty":"Hard","question":"Who wrote 'The Art of War'?","options":["Confucius","Lao Tzu","Sun Tzu","Mencius"],"answer":2,"explanation":"Sun Tzu wrote The Art of War, a treatise on military strategy."},
    {"id":"q027","category":"History","difficulty":"Easy","question":"Which ancient wonder was in Alexandria, Egypt?","options":["Colossus of Rhodes","Great Lighthouse","Hanging Gardens","Statue of Zeus"],"answer":1,"explanation":"The Great Lighthouse of Alexandria was one of the Seven Wonders of the Ancient World."},
    {"id":"q028","category":"History","difficulty":"Medium","question":"Napoleon Bonaparte was exiled to which island?","options":["Corsica","Elba","Sardinia","Saint Helena"],"answer":3,"explanation":"Napoleon was finally exiled to Saint Helena after Waterloo (1815)."},

    # General Knowledge
    {"id":"q029","category":"General Knowledge","difficulty":"Easy","question":"What is the capital of France?","options":["Lyon","Marseille","Paris","Nice"],"answer":2,"explanation":"Paris is the capital and largest city of France."},
    {"id":"q030","category":"General Knowledge","difficulty":"Easy","question":"How many continents are on Earth?","options":["5","6","7","8"],"answer":2,"explanation":"Earth has 7 continents: Africa, Antarctica, Asia, Australia, Europe, North America, South America."},
    {"id":"q031","category":"General Knowledge","difficulty":"Medium","question":"What is the longest river in the world?","options":["Amazon","Yangtze","Mississippi","Nile"],"answer":3,"explanation":"The Nile is traditionally considered the longest river at ~6,650 km."},
    {"id":"q032","category":"General Knowledge","difficulty":"Medium","question":"Which planet is closest to the Sun?","options":["Venus","Earth","Mars","Mercury"],"answer":3,"explanation":"Mercury is the closest planet to the Sun."},
    {"id":"q033","category":"General Knowledge","difficulty":"Hard","question":"What is the smallest country in the world?","options":["Monaco","San Marino","Vatican City","Liechtenstein"],"answer":2,"explanation":"Vatican City covers ~0.44 km² making it the smallest sovereign state."},
    {"id":"q034","category":"General Knowledge","difficulty":"Easy","question":"How many sides does a hexagon have?","options":["5","6","7","8"],"answer":1,"explanation":"A hexagon has 6 sides."},
    {"id":"q035","category":"General Knowledge","difficulty":"Medium","question":"Which ocean is the largest?","options":["Atlantic","Indian","Arctic","Pacific"],"answer":3,"explanation":"The Pacific Ocean is the largest, covering about 165 million km²."},

    # Sports
    {"id":"q036","category":"Sports","difficulty":"Easy","question":"How many players are on a standard football (soccer) team?","options":["9","10","11","12"],"answer":2,"explanation":"A football team has 11 players on the field."},
    {"id":"q037","category":"Sports","difficulty":"Easy","question":"In which sport is a 'grand slam' achieved?","options":["Tennis","Basketball","Cricket","Golf"],"answer":0,"explanation":"In tennis, a Grand Slam means winning all four major tournaments in a year."},
    {"id":"q038","category":"Sports","difficulty":"Medium","question":"How many rings are on the Olympic flag?","options":["4","5","6","7"],"answer":1,"explanation":"The Olympic flag has 5 rings representing 5 continents."},
    {"id":"q039","category":"Sports","difficulty":"Medium","question":"What is the maximum score in a single game of ten-pin bowling?","options":["200","250","300","360"],"answer":2,"explanation":"A perfect game in bowling is 300 (12 consecutive strikes)."},
    {"id":"q040","category":"Sports","difficulty":"Hard","question":"Which country has won the most FIFA World Cups?","options":["Germany","Argentina","Italy","Brazil"],"answer":3,"explanation":"Brazil has won the FIFA World Cup 5 times (1958, 1962, 1970, 1994, 2002)."},
    {"id":"q041","category":"Sports","difficulty":"Hard","question":"How long is a marathon?","options":["40 km","42.195 km","43 km","41.5 km"],"answer":1,"explanation":"A marathon is exactly 42.195 km (26.2 miles)."},
    {"id":"q042","category":"Sports","difficulty":"Easy","question":"What sport is played at Wimbledon?","options":["Badminton","Squash","Tennis","Cricket"],"answer":2,"explanation":"Wimbledon is the world's oldest tennis Grand Slam tournament."},
    {"id":"q043","category":"Sports","difficulty":"Medium","question":"How many players are on a basketball team on the court at once?","options":["4","5","6","7"],"answer":1,"explanation":"Each basketball team has 5 players on the court simultaneously."},

    # Extra Technology
    {"id":"q044","category":"Technology","difficulty":"Easy","question":"What does 'URL' stand for?","options":["Uniform Resource Locator","Universal Record Link","Uniform Relay Link","User Reference Locator"],"answer":0,"explanation":"URL = Uniform Resource Locator — the address of a resource on the web."},
    {"id":"q045","category":"Technology","difficulty":"Medium","question":"Which data structure uses LIFO (Last In, First Out)?","options":["Queue","Stack","Tree","Graph"],"answer":1,"explanation":"A stack uses LIFO — the last item pushed is the first popped."},
    {"id":"q046","category":"Technology","difficulty":"Hard","question":"What does DNS stand for?","options":["Domain Name System","Digital Network Server","Data Name Service","Domain Network Structure"],"answer":0,"explanation":"DNS = Domain Name System — translates domain names to IP addresses."},
    {"id":"q047","category":"Technology","difficulty":"Medium","question":"Which of these is NOT a Python data type?","options":["list","tuple","vector","dict"],"answer":2,"explanation":"Python has lists, tuples, and dicts built-in, but 'vector' is not a built-in type."},
    {"id":"q048","category":"Technology","difficulty":"Hard","question":"What does 'ORM' stand for in databases?","options":["Object-Relational Mapping","Optimised Record Model","Open Relational Method","Object Record Manager"],"answer":0,"explanation":"ORM = Object-Relational Mapping — lets you interact with a DB using objects."},
    {"id":"q049","category":"Science","difficulty":"Medium","question":"What is the boiling point of water at sea level (°C)?","options":["90","95","100","105"],"answer":2,"explanation":"Water boils at 100°C (212°F) at standard atmospheric pressure."},
    {"id":"q050","category":"General Knowledge","difficulty":"Hard","question":"What is the currency of Japan?","options":["Yuan","Won","Baht","Yen"],"answer":3,"explanation":"Japan's currency is the Yen (¥)."},
]

CATEGORIES = ["General Knowledge", "Science", "History", "Sports", "Technology"]
DIFFICULTIES = ["Easy", "Medium", "Hard"]
TIME_LIMITS = {"Easy": 15, "Medium": 20, "Hard": 30}
BASE_POINTS = {"Easy": 100, "Medium": 200, "Hard": 300}


def _get_questions(category: str, difficulty: str) -> list[dict]:
    pool = [q for q in QUESTIONS if q["category"] == category and q["difficulty"] == difficulty]
    if len(pool) < 10:
        extra = [q for q in QUESTIONS if q["category"] == "General Knowledge" and q not in pool]
        pool += extra
    random.shuffle(pool)
    return pool[:10]


def render_quiz() -> None:
    """Main entry-point called from app.py."""
    st.markdown("""
    <style>
    .quiz-card{background:#1A1A2E;border-radius:14px;padding:22px;margin-bottom:12px;border:1px solid #6C63FF44;}
    .quiz-option button{width:100%;text-align:left;background:#12122A;border:1.5px solid #333;color:#EAEAEA;
      padding:10px 16px;border-radius:8px;font-size:0.95rem;cursor:pointer;transition:all 0.2s;margin-bottom:6px;}
    .quiz-option button:hover{border-color:#6C63FF;background:#1e1e3a;}
    .correct-ans{border-color:#69F0AE!important;background:#0d2b1e!important;color:#69F0AE!important;}
    .wrong-ans{border-color:#FF5252!important;background:#2b0d0d!important;color:#FF5252!important;}
    .streak-badge{background:#6C63FF;color:#fff;padding:3px 12px;border-radius:12px;font-size:0.8rem;font-weight:700;}
    </style>
    """, unsafe_allow_html=True)

    st.markdown("## 🧠 Quiz Game")

    if not st.session_state.get("quiz_active"):
        _render_quiz_setup()
    else:
        _render_quiz_question()


def _render_quiz_setup() -> None:
    col1, col2 = st.columns(2)
    with col1:
        cat = st.selectbox("📚 Category", CATEGORIES, key="quiz_cat_sel")
    with col2:
        diff = st.selectbox("⚡ Difficulty", DIFFICULTIES, key="quiz_diff_sel")

    st.markdown(f"""
    <div class="quiz-card">
      <b>Settings</b><br>
      Category: <span style="color:#6C63FF">{cat}</span> &nbsp;|&nbsp;
      Difficulty: <span style="color:#6C63FF">{diff}</span> &nbsp;|&nbsp;
      Time: <span style="color:#6C63FF">{TIME_LIMITS[diff]}s per question</span><br>
      Points: <span style="color:#6C63FF">{BASE_POINTS[diff]} base + time bonus</span> &nbsp;|&nbsp;
      Streak bonus at 3+ correct: <span style="color:#6C63FF">1.5×</span>
    </div>
    """, unsafe_allow_html=True)

    if st.button("▶ Start Quiz", use_container_width=True):
        qs = _get_questions(cat, diff)
        st.session_state.update({
            "quiz_active": True,
            "quiz_question_idx": 0,
            "quiz_score": 0,
            "quiz_correct": 0,
            "quiz_wrong": 0,
            "quiz_skipped": 0,
            "quiz_streak": 0,
            "quiz_multiplier": 1.0,
            "quiz_lifelines": {"fifty_fifty": True, "skip": True},
            "quiz_category": cat,
            "quiz_difficulty": diff,
            "quiz_answers": [],
            "quiz_start_time": time.time(),
            "quiz_q_start": time.time(),
            "quiz_questions": qs,
            "quiz_fifty_fifty_options": None,
            "quiz_answered": False,
            "quiz_last_correct": None,
            "quiz_last_explanation": "",
        })
        st.rerun()


def _render_quiz_question() -> None:
    qs = st.session_state["quiz_questions"]
    idx = st.session_state["quiz_question_idx"]

    if idx >= len(qs):
        _render_quiz_results()
        return

    q = qs[idx]
    diff = st.session_state["quiz_difficulty"]
    time_limit = TIME_LIMITS[diff]
    elapsed = time.time() - st.session_state.get("quiz_q_start", time.time())
    remaining = max(0.0, time_limit - elapsed)
    pct = remaining / time_limit

    # HUD
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Question", f"{idx+1}/10")
    col2.metric("Score", f"{st.session_state['quiz_score']:,}")
    col3.metric("Streak", st.session_state["quiz_streak"])
    col4.metric("⏱ Time", f"{remaining:.1f}s")

    # Timer bar
    bar_color = "#69F0AE" if pct > 0.5 else ("#FFD740" if pct > 0.25 else "#FF5252")
    st.markdown(f"""
    <div style="background:#1A1A2E;border-radius:6px;height:8px;margin-bottom:12px;overflow:hidden">
      <div style="width:{pct*100:.1f}%;height:100%;background:{bar_color};border-radius:6px;transition:width 0.5s"></div>
    </div>
    """, unsafe_allow_html=True)

    # Auto-timeout
    if remaining <= 0 and not st.session_state.get("quiz_answered"):
        st.session_state["quiz_skipped"] += 1
        st.session_state["quiz_answers"].append({"q": q["question"], "correct": False, "skipped": True})
        _advance_question()
        st.rerun()
        return

    # Question
    st.markdown(f"""
    <div class="quiz-card">
      <div style="color:#888;font-size:0.78rem">{q['category']} · {q['difficulty']}</div>
      <div style="font-size:1.15rem;font-weight:700;margin-top:6px">{q['question']}</div>
    </div>
    """, unsafe_allow_html=True)

    answered = st.session_state.get("quiz_answered", False)
    fifty_fifty = st.session_state["quiz_fifty_fifty_options"]
    options = q["options"]
    visible_indices = fifty_fifty if fifty_fifty is not None else list(range(len(options)))

    if not answered:
        cols = st.columns(2)
        for i, opt in enumerate(options):
            if i not in visible_indices:
                continue
            with cols[i % 2]:
                if st.button(f"{'ABCD'[i]}. {opt}", key=f"opt_{idx}_{i}", use_container_width=True):
                    _handle_answer(q, i, elapsed, time_limit)
                    st.rerun()

        # Lifelines
        st.markdown("---")
        lcol1, lcol2 = st.columns(2)
        with lcol1:
            ff_avail = st.session_state["quiz_lifelines"]["fifty_fifty"] and len(visible_indices) > 2
            if st.button("🔀 50/50", disabled=not ff_avail, use_container_width=True):
                wrong = [i for i in range(len(options)) if i != q["answer"]]
                random.shuffle(wrong)
                st.session_state["quiz_fifty_fifty_options"] = [q["answer"], wrong[0]]
                st.session_state["quiz_lifelines"]["fifty_fifty"] = False
                st.rerun()
        with lcol2:
            skip_avail = st.session_state["quiz_lifelines"]["skip"]
            if st.button("⏭ Skip", disabled=not skip_avail, use_container_width=True):
                st.session_state["quiz_lifelines"]["skip"] = False
                st.session_state["quiz_skipped"] += 1
                st.session_state["quiz_answers"].append({"q": q["question"], "correct": False, "skipped": True})
                _advance_question()
                st.rerun()
    else:
        # Show result feedback
        correct = st.session_state.get("quiz_last_correct")
        for i, opt in enumerate(options):
            label = f"{'ABCD'[i]}. {opt}"
            if i == q["answer"]:
                st.success(f"✅ {label}")
            elif i == st.session_state.get("quiz_selected_idx"):
                st.error(f"❌ {label}")
            else:
                st.markdown(f"<div style='color:#555;padding:4px 0'>{label}</div>", unsafe_allow_html=True)

        expl = st.session_state.get("quiz_last_explanation", "")
        if expl:
            st.info(f"💡 {expl}")

        if st.button("➡ Next Question", use_container_width=True):
            _advance_question()
            st.rerun()


def _handle_answer(q: dict, selected: int, elapsed: float, time_limit: float) -> None:
    correct = selected == q["answer"]
    diff = st.session_state["quiz_difficulty"]
    base = BASE_POINTS[diff]
    time_bonus = int(base * max(0, (time_limit - elapsed) / time_limit) * 0.5)

    if correct:
        st.session_state["quiz_correct"] += 1
        st.session_state["quiz_streak"] += 1
        streak = st.session_state["quiz_streak"]
        mult = 1.5 if streak >= 3 else 1.0
        pts = int((base + time_bonus) * mult)
        st.session_state["quiz_score"] += pts
        st.session_state["quiz_multiplier"] = mult
    else:
        st.session_state["quiz_wrong"] += 1
        st.session_state["quiz_streak"] = 0
        st.session_state["quiz_multiplier"] = 1.0

    st.session_state["quiz_answered"] = True
    st.session_state["quiz_last_correct"] = correct
    st.session_state["quiz_selected_idx"] = selected
    st.session_state["quiz_last_explanation"] = q.get("explanation", "")
    st.session_state["quiz_answers"].append({
        "q": q["question"], "correct": correct, "skipped": False, "selected": selected
    })


def _advance_question() -> None:
    st.session_state["quiz_question_idx"] += 1
    st.session_state["quiz_answered"] = False
    st.session_state["quiz_last_correct"] = None
    st.session_state["quiz_selected_idx"] = None
    st.session_state["quiz_fifty_fifty_options"] = None
    st.session_state["quiz_q_start"] = time.time()


def _render_quiz_results() -> None:
    score = st.session_state["quiz_score"]
    correct = st.session_state["quiz_correct"]
    wrong = st.session_state["quiz_wrong"]
    skipped = st.session_state["quiz_skipped"]
    total_time = time.time() - (st.session_state.get("quiz_start_time") or time.time())
    cat = st.session_state["quiz_category"]
    diff = st.session_state["quiz_difficulty"]
    player = get_player_name()

    st.markdown(f"""
    <div class="quiz-card" style="text-align:center">
      <div style="font-size:2.5rem">🎯</div>
      <div style="font-size:1.6rem;font-weight:700;color:#6C63FF">{score:,} pts</div>
      <div style="color:#888;margin-top:4px">{player} · {cat} · {diff}</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("✅ Correct", correct)
    col2.metric("❌ Wrong", wrong)
    col3.metric("⏭ Skipped", skipped)
    col4.metric("⏱ Time", f"{total_time:.0f}s")

    # Answer breakdown
    with st.expander("📋 Answer Breakdown"):
        for i, ans in enumerate(st.session_state["quiz_answers"], 1):
            icon = "✅" if ans["correct"] else ("⏭" if ans.get("skipped") else "❌")
            st.markdown(f"{icon} **Q{i}**: {ans['q']}")

    if st.button("💾 Save to Leaderboard", use_container_width=True):
        try:
            add_score(
                player_name=player,
                game="quiz",
                score=score,
                metadata={"category": cat, "difficulty": diff, "correct": correct, "time": round(total_time)},
                session_token=st.session_state.get("session_token"),
            )
            st.success("✅ Score saved to leaderboard!")
        except Exception as e:
            st.error(f"Could not save score: {e}")

    if st.button("🔄 Play Again", use_container_width=True):
        st.session_state["quiz_active"] = False
        st.rerun()
