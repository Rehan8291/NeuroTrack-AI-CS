# NeuroTrack AI — Setup & Status

## How to run

```bash
pip install customtkinter matplotlib
python main.py
```

The very first run will automatically:
- Create any missing tables
- **Migrate your old database schema** (see below) into the new one, keeping your old rows safe in a backup table

## 🔧 What was actually broken (and fixed)

1. **Database schema mismatch (the real crash cause)**
   Your `neurotrack.db` file's `user_logs` table was still using the
   old CLI-prototype schema (`name, age, study, scroll, sleep,
   exercise, mood, focus_score`) — no `username` or `log_date` column.
   Your current `db.py` code expects the new GUI schema
   (`username, study, sleep, exercise, scroll, mood, focus_score,
   log_date`). Any call to `save_log()` or `get_all_logs()` from the
   GUI would crash with `no column named username`.

   **Fix:** `create_tables()` now detects the old schema automatically,
   renames it to `user_logs_legacy_backup` (your old data is preserved,
   just not linked to any GUI feature), and creates the correct table.
   This is safe to run every time the app starts.

2. **`dashboard.py` navigation** — I reviewed this file carefully: all
   navigation methods (`show_dashboard`, `show_analytics`, etc.) are
   already correctly indented inside the `Dashboard` class in the
   version you sent me — this part was actually fine. The real reason
   nothing worked end-to-end was #1 above, plus the fact that every
   page was showing **hardcoded placeholder data**, not real data from
   the database (see below).

3. **`ai_coach.py` typo** — two strings were concatenated without a
   space (`"...scrolling."` + `"reduce..."` → `"scrolling.reduce"`).
   Fixed.

4. **Focus Age feature had no age to use** — `focus_age.py` needs a
   user's age, but the `users` table had no `age` column and signup
   never asked for one. Added an `age` column (auto-migrates existing
   DBs) and an optional "Age" field on the signup screen.

## ✅ What was added (previously just placeholders)

| Module | What's new |
|---|---|
| **Log Today** (new) | A popup form (`gui/log_entry.py`) to enter study/sleep/exercise/scroll hours + mood. Calculates your Focus Score using the same formula from your old CLI version, saves it, and checks for new achievements. This was the missing piece — nothing else can show real data without it. |
| **Dashboard** | Now shows your actual last log (not hardcoded 92%/5.2 Hrs), plus a real AI Coach message and challenge. Shows an empty state if you haven't logged anything yet. |
| **Analytics** | Real averages (focus, study, sleep, exercise) computed from your logs, plus an embedded **Matplotlib** chart (study hours bar + focus score line) for your last 7 entries. |
| **AI Coach page** | Now actually calls your existing `ai_coach.py`, `daily_challenge.py`, `focus_age.py`, `future_self.py`, and `producticity_animal.py` — all of which were already written but never connected to the GUI. |
| **History** | Shows your real logs from the database, with a live search box (by date or mood) and a "📥 Export CSV" button. |
| **Achievements** | 6 real badges (7 Day Streak, 100 Study Hours, Sleep Champion, Fitness Badge, Focus Master, Consistency Badge) computed from your actual stats and saved to the `achievements` table. Locked badges show 🔒. |
| **Profile** | Real total study hours, average focus, total logs, and current streak. |
| **Settings** | Working Dark/Light mode toggle (saved to DB), notifications toggle, change-password form, and a "Reset All Data" button (with confirmation). |

## 🧪 Testing note

I don't have a display environment here, so I couldn't click through the
actual GUI. I did verify, without customtkinter:
- Every file compiles (no syntax errors)
- All database functions work correctly end-to-end (signup, login,
  logging data, achievements, settings, password change, reset)
- The schema migration works correctly on your actual uploaded `.db` file
- Every function `dashboard.py` imports actually exists with the right signature

**Please do a manual click-through on your machine** (since you have
customtkinter installed) and tell me if anything looks visually off —
I can't see the rendered UI from here.

## 🟡 Still not done 

- **Profile picture** — not implemented (would need a file picker + image display)
- **PDF Report / Pomodoro Timer / Focus Music / Weather Widget** — bonus features, not started
- Achievement badges don't have custom icons/artwork, just emoji


