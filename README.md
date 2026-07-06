# Cookie Run Classic Auto-AFK Bot (iPhone Mirroring / macOS)

Modular bot that plays fixed-layout stages automatically by combining:
- **Vision** (OpenCV template matching) — figures out what screen you're on
- **Macro replay** — plays back a recorded input sequence for the actual
  running/action segment, since your stages have fixed layouts
- **State machine** — decides what to do next based on what vision sees

This mirrors the design from your project doc: vision decides, macro plays.

## Project layout

```
cookierun_bot/
├── config.py            # all tunable settings
├── window_capture.py     # finds + screenshots the iPhone Mirroring window
├── vision.py             # template matching
├── input_controller.py   # sends taps/swipes via cliclick
├── macro.py              # record/replay fixed click sequences
├── state_machine.py       # workflow: shop -> buy -> run -> reward -> retry
├── main.py                # entry point
├── templates/              # your button screenshots go here
└── macros/                 # recorded macros get saved here
```

## 1. Install dependencies

```bash
pip3 install opencv-python pyobjc-framework-Quartz pynput numpy
brew install cliclick
```

## 2. Grant macOS permissions

System Settings → Privacy & Security:
- **Screen Recording** → enable for Terminal (or whatever runs the script)
- **Accessibility** → enable for Terminal (needed for cliclick and pynput)

## 3. Capture button templates

Your actual flow is: **shop (buy loop) → running → reward → back to shop.**
The shop step keeps tapping Multi-Buy until the Double Coins banner shows,
then plays. Templates needed, saved into `templates/` with these exact
names:

```
templates/
├── play_button.png            # green "Play!" button in the shop
├── multi_button.png           # "Multi" button next to Random Boost
├── double_coins_banner.png    # red "Double Coins" banner above Play
├── reward_ok.png              # OK button on the Result screen
└── claim_button.png           # optional claim popup after OK (if any)
```

`play_button.png`, `multi_button.png`, and `double_coins_banner.png` are
already included, cropped from your footage. You'll still need to add
`reward_ok.png` and `claim_button.png` from your own screenshots of the
Result screen — Preview.app → `Cmd+Shift+4` → drag over just the button →
move into `templates/`.

**How the shop loop works** (see `state_machine.py`):
1. Check for the Double Coins banner.
2. If it's showing → tap Play, go to the running stage.
3. If not → tap Multi-Buy, wait ~2s for the reveal animation, check again.
4. Repeat up to `MAX_BUY_ATTEMPTS` (15 by default, in `state_machine.py`)
   before giving up and playing anyway — this caps how many coins it'll
   spend re-rolling in a single shop visit.

## 4. Record the running-segment macro

Since your stage layout is fixed, record it once:

```bash
python3 macro.py stage1_run
```

Then play through the stage normally by clicking in the iPhone Mirroring
window (jump, slide, skills — whatever the stage needs). Press `Ctrl+C`
when the run ends. This saves `macros/stage1_run.json`.

Record as many stages as you need (`stage2_run`, `boss_run`, etc.) and
reference them in `state_machine.py`.

## 5. Edit the workflow if needed

`state_machine.py`'s `STATE_CONFIG` encodes the loop:

```
shop -> buy -> start_run -> running (macro) -> reward -> retry -> shop
```

Add, remove, or reorder states to match your actual game flow — e.g. if
there's a "daily reward" popup only some of the time, you'll want an extra
state or a branch for it.

## 6. Run it

```bash
python3 main.py
```

Ctrl+C to stop. The bot also stops itself automatically if it sits on an
unrecognized screen for too long (`UNKNOWN_SCREEN_TIMEOUT` in `config.py`)
rather than clicking blindly — useful for catching login prompts, network
errors, or unexpected popups.

## Tuning notes

- `CONFIDENCE_THRESHOLD` in `config.py`: lower it if real matches are being
  missed, raise it if it's triggering on the wrong thing.
- `JITTER_PIXELS`: adds small random offset to every tap so repeated taps
  aren't pixel-identical — keep this instead of removing it.
- Keep the iPhone Mirroring window the same size between capturing
  templates/macros and running the bot; template matching and recorded
  coordinates are both resolution-dependent.

## Risk note

This automates your own screen only — it doesn't touch the game's client
or servers directly. That said, most games' Terms of Service prohibit
macros/automation regardless of how it's implemented, so there's some
inherent risk of an account being flagged if this is used heavily.
