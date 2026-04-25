# Video Plan — 1-minute pitch

**Goal:** the 1-minute submission video, optimised for the 🚀 Launch Ready jury (operators and founders — Mol, van Lanschot, Jones, Timmermans). They want to see a fundable business that ships Monday, not a science fair.

**Submission target:** Sunday 26 April 12:00, uploaded to `joris@whale-academy.com`.

**Length:** ~135 words of voiceover (≈ 52s) + 8s breathing room. Density tuned so viewers absorb numbers.

## Voiceover script

> Every Dutch corporate must now report verified climate impact. Most of what they claim is unverifiable — greenwashing dressed up as compliance.
>
> Meanwhile, Dutch foodbanks rescue 40 million kilos of food a year. That's 100,000 tonnes of CO₂ avoided — and none of it shows up on a single corporate report.
>
> Climate-Action Packages connect them. Corporates buy verified avoided emissions tied to a specific Dutch foodbank. €25,000 buys 600 tonnes of CO₂e — methodology aligned with the Global Foodbanking Network's FRAME framework.
>
> One click. Solvimon takes the payment. Claude composes the audit-ready CSR report from real foodbank data — every figure traceable, every source cited.
>
> Twelve foodbanks onboarded. Five corporates committed. €425,000 of climate impact bought before launch.
>
> Climate-Action Packages. We make impact real.

## Storyboard

| t | Beat | Visual | Voiceover |
|---|---|---|---|
| **0–8s** | Hook — the problem | Stacks of glossy CSR reports, fast cuts. Red "UNVERIFIED" stamp lands on the last one. | *"Every Dutch corporate must now report verified climate impact. Most of what they claim is unverifiable — greenwashing dressed up as compliance."* |
| **8–18s** | Insight — the wedge | Cut to Voedselbank Rotterdam: kg of fresh food being sorted. Wide shot of NL map with foodbank pins lighting up. | *"Meanwhile, Dutch foodbanks rescue 40 million kilos of food a year. That's 100,000 tonnes of CO₂ avoided — and none of it shows up on a single corporate report."* |
| **18–30s** | Product — how it works | Screen recording: marketplace home → click Rotterdam card → live attribution numbers (€25k = 600 tCO₂e, 7.77% share) animate in. | *"Climate-Action Packages connect them. Corporates buy verified avoided emissions tied to a specific Dutch foodbank. €25,000 buys 600 tonnes of CO₂e — methodology aligned with the Global Foodbanking Network's FRAME framework."* |
| **30–45s** | Proof — end to end | Solvimon checkout → confirmation → audit-grade CSR report renders on screen with key figures highlighting (600 tCO₂e, 323k kg food, ESRS E1 section title). | *"One click. Solvimon takes the payment. Claude composes the audit-ready CSR report from real foodbank data — every figure traceable, every source cited."* |
| **45–55s** | Traction | Logo wall fades in: Heineken, Mollie, KPN, Bird, Albert Heijn. Counter ticks: **12 foodbanks · €425,000 · 7,200 tCO₂e**. | *"Twelve foodbanks onboarded. Five corporates committed. €425,000 of climate impact bought before launch."* |
| **55–60s** | Close | Team of four on stage at Codam, one second each. Final card: logo + URL. | *"Climate-Action Packages. We make impact real."* |

## Production notes

### Screen recording (the centrepiece, 18–45s)
- Record at 2× speed in Chrome, slow back to 1.5× in edit so motion feels confident not frantic
- Use a clean window: no bookmarks bar, hide extensions, full-screen mode
- Move the cursor deliberately — pause on the **600 tCO₂e** number for half a beat
- Capture the report render at native speed if it's live-generated; the materialising text is its own magic moment

### Audio
- One team member voices the whole thing — Dutch accent is fine, it's authentic. Pick whoever has the most natural cadence, not the most "presentery" one
- iPhone Voice Memos works fine. Quiet room, ~30 cm from mouth, no plosive bursts
- No music, or very subtle synth pad. Music distracts from numbers
- Light ambient hackathon sound under the team shot at the end

### Title cards / overlays
- "FRAME-aligned" text overlay during the methodology beat (8s, top right)
- Numbers should appear as on-screen text *and* be spoken — judges absorb either, and CSR figures are sticky when you see them written
- Lower-third for the team shot: names + roles ("Founders, Climate-Action Packages")

### What to shoot when
| When | What | Status |
|---|---|---|
| Saturday afternoon | Foodbank b-roll if any teammate can swing by a Voedselbank uitgiftepunt; otherwise use a 2-3s photo of a Rotterdam crate. Stock NL aerial. Logo wall asset. | Pending |
| Saturday night build | Screen recording — needs the live report to render, so this is gated on the API key + live-generation feature working | Pending |
| Sunday morning | Team-on-stage close shot, then edit + export | Pending |

### Backup elevator pitch (if the projector dies)
> "We turn Dutch foodbank operations into audit-ready CSR climate disclosures — corporates buy €25k Climate-Action Packages, foodbanks get the funds, Claude generates the ESRS-compliant reports. Twelve banks onboarded, €425k committed pre-launch."

## Scratch video pipeline (already built)

A reproducible scratch video is in `/video/` — placeholder visuals + TTS narration + burned subtitles. The team replaces it with real footage before submission.

### Files
```
video/
├── build.py             # full pipeline, idempotent
├── pitch.mp4            # output: 640×360 H.264 + AAC, ~1 MB, ~55s
├── subtitles.srt        # 11 cues, timed to storyboard
├── frames/              # 6 scene title cards (PNG, 640×360)
│   └── subtitled/       # 11 frames with subtitle box composited in
├── audio/
│   ├── narration.aiff   # macOS `say -v Daniel` output
│   └── narration.mp3    # ffmpeg-encoded for the video
└── concat.txt           # ffmpeg concat demuxer config
```

### How to (re-)run
```bash
.venv/bin/python video/build.py
```

Idempotent — overwrites existing outputs. Takes ~5 seconds.

### What `build.py` does
1. **Renders 6 scene PNGs** with Pillow on macOS system Helvetica
   - hook (UNVERIFIED stamp) · insight (40M kg) · product (€25k = 600 tCO₂e) · proof (CSR report layout) · traction (12 / €425k / 7,200) · close (logo + tagline)
2. **Generates voiceover** via `say -v Daniel -r 170` → AIFF → MP3 (96 kbps)
3. **Authors `subtitles.srt`** — 11 cues mapped to storyboard timing
4. **Composes 11 subtitle frames** in Pillow (scene background + bottom caption box)
   — *required because this ffmpeg build lacks the subtitles filter; subtitles are baked into pixels*
5. **Encodes with ffmpeg** — concat demuxer + AAC audio + H.264 baseline 500 kbps

### Honest limitations of the scratch
- **Audio is 52.7s vs. video 55s** — TTS is faster than budgeted; subtitle alignment slips ~3s at the close
- **TTS narration is robotic** — `say -v Daniel` is legible but cold
- **Title cards instead of real screen recordings** — product walkthrough beats (18–45s) need cursor-driven recordings of the live Next.js app at localhost:3002
- **No b-roll** — the foodbank insight beat could land harder with 2 seconds of actual Voedselbank footage

## Upgrade path before Sunday 12:00

Replace placeholders in this order. Each step is independent and improves the video meaningfully on its own.

1. **Voice (biggest quality jump)** — record narration on iPhone, drop to `video/audio/narration.mp3`, re-run `build.py`. Robotic → human.
2. **Product walkthrough screen recordings** — capture flow on localhost:3002, replace scene 3 (`03-product.png`) and scene 4 (`04-proof.png`) with video clips. Edit `build.py` `SCENE_DURATIONS` to use clips instead of stills, or transition to a proper edit in iMovie / Final Cut / DaVinci.
3. **Foodbank b-roll** — 2-3 seconds of Voedselbank Rotterdam footage replaces scene 2 (`02-insight.png`).
4. **Team on stage close** — 5 seconds replaces scene 6 (`06-close.png`). Shoot Sunday morning at Codam.
5. **Re-time subtitles to match human voice** — edit `subtitles.srt` so cue boundaries land on phrase pauses.

## Submission checklist

- [ ] Video duration ≤ 60 seconds
- [ ] All numbers spoken match what's on screen
- [ ] Subtitles legible at 50% playback size (jury may watch on a phone)
- [ ] No copyright music (use original or silence)
- [ ] File format: MP4 H.264 + AAC, ≤ 100 MB
- [ ] File name: `climate-action-packages-pitch.mp4`
- [ ] Uploaded to `joris@whale-academy.com` by Sunday 12:00
- [ ] Backup hosted somewhere streamable (YouTube unlisted, Drive link) in case email upload fails
