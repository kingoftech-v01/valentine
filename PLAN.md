# Valentine "Rencontre l'Amour" Platform — Implementation Plan

## Overview
Transform the static Valentine page into a multi-user platform where anyone can create a fully personalized valentine (acrostic, poem, YouTube music) and share it via a unique link to their crush. Built with **Django**.

---

## User Flows

### Sender Flow (Create Page — `/`)
1. Lands on the creation page
2. Enters **their name** (sender)
3. Enters **crush's name** (recipient)
4. Chooses **acrostic mode**:
   - "Automatique" → auto-generated from the existing acrosticDB (client-side)
   - "Personnalisé" → writes a custom phrase for each letter of the crush's name
5. Chooses **poem mode**:
   - "Poème classique" → the existing French poem
   - "Mon propre message" → writes their own poem/message
6. Chooses **music mode**:
   - "Mélodie par défaut" → the built-in Web Audio waltz melody
   - "Ma chanson YouTube" → pastes a YouTube URL → embedded as background audio on receiver page
7. Clicks **"Envoyer"** → POST to backend → returns unique shareable link
8. Sees share screen with link + copy button + WhatsApp/SMS share buttons

### Receiver Flow (View Page — `/v/<id>/`)
1. Opens the unique link
2. Django view fetches the valentine data, renders it into the template
3. Full Valentine experience:
   - Envelope opens → reveals crush's name
   - Hero: "Joyeuse Saint-Valentin, [Name]"
   - Bubbles with acrostic (default or custom)
   - Door scene with characters meeting
   - Poem (default or custom) with typewriter effect
   - Signature: "~ De [Sender], pour [Recipient] ~"
   - Music: default melody OR YouTube song in background
   - All existing effects (sparkles, hearts, confetti, etc.)

### Rate Limiting
- **3 different recipients per sender per day** (tracked by IP)
- Re-sending to the same recipient doesn't count as new
- Over limit → "Tu as déjà envoyé 3 valentins aujourd'hui ! Reviens demain"

---

## Technical Architecture

### Stack
- **Backend**: Django 5.x
- **Database**: SQLite (Django default — zero config)
- **Frontend**: Django templates (two pages: create + view)
- **IDs**: Python `secrets.token_urlsafe(6)` for short unique URLs
- **YouTube**: YouTube IFrame Player API (client-side, loaded from googleapis)

### Project Structure
```
valentine/
├── manage.py
├── valentineproject/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── core/
│   ├── __init__.py
│   ├── models.py          # Valentine model
│   ├── views.py           # create, view, API views
│   ├── urls.py             # route config
│   ├── utils.py            # YouTube URL parser, rate limit check
│   └── templates/
│       └── core/
│           ├── create.html      # Sender page
│           └── valentine.html   # Receiver page
├── static/                  # (optional, Django can serve in dev)
├── db.sqlite3               # auto-created
├── valentine.html           # old file (will be removed)
├── valentine (1).html       # old file (will be removed)
└── valentine (2).html       # old file (will be removed)
```

### Django Model
```python
class Valentine(models.Model):
    uid = models.CharField(max_length=12, unique=True, db_index=True)
    sender_name = models.CharField(max_length=50)
    recipient_name = models.CharField(max_length=50)
    acrostic_mode = models.CharField(max_length=10)    # 'default' or 'custom'
    custom_acrostic = models.JSONField(null=True, blank=True)
    # e.g. [{"letter":"A","phrase":"Au creux de..."},...]
    poem_mode = models.CharField(max_length=10)         # 'default' or 'custom'
    custom_poem = models.TextField(null=True, blank=True)
    music_mode = models.CharField(max_length=10)        # 'default' or 'youtube'
    youtube_id = models.CharField(max_length=20, null=True, blank=True)
    sender_ip = models.GenericIPAddressField()
    created_at = models.DateTimeField(auto_now_add=True)
```

### URL Routes
```
/                  → create page (GET: form, POST: create valentine)
/v/<uid>/          → view valentine (receiver page)
```

### Views
- **create_view (GET)**: Render the creation form page
- **create_view (POST)**: Validate, check rate limit, save to DB, return JSON with link
- **valentine_view (GET)**: Fetch valentine by uid, render receiver template with context data (server-side rendering — all data injected into template as JS variables)

---

## Music: YouTube Integration

### Default Mode
- Existing Web Audio API waltz melody (from valentine (2).html)
- Plays after envelope interaction

### YouTube Mode
- Receiver page loads YouTube IFrame Player API
- Hidden `<div>` (1x1px off-screen) hosts the player
- `new YT.Player(el, { videoId, playerVars: { autoplay:1, loop:1, playlist:videoId } })`
- Music button toggles `player.mute()` / `player.unMute()`
- Fallback: if YouTube fails → silently use default melody

### URL Parsing (server-side in `utils.py`)
Extracts video ID from:
- `youtube.com/watch?v=VIDEO_ID`
- `youtu.be/VIDEO_ID`
- `youtube.com/embed/VIDEO_ID`
- `music.youtube.com/watch?v=VIDEO_ID`
- Returns `None` if invalid → validation error

---

## Page Details

### Create Page (`create.html`)
- Same dark romantic theme (dark bg, rose/gold, Great Vibes + Playfair Display)
- Floating hearts background
- Form in styled cards:
  1. "Crée ton Valentin" header with animated heart
  2. "Ton prénom" — text input
  3. "Le prénom de ton crush" — text input (on change: updates acrostic preview)
  4. Acrostiche — pill toggle: "Automatique" / "Personnalisé"
     - Personnalisé: one input per letter, gold letter on left, appears dynamically
  5. Poème — pill toggle: "Poème classique" / "Mon propre message"
     - Custom: textarea with placeholder
  6. Musique — pill toggle: "Mélodie par défaut" / "Chanson YouTube"
     - YouTube: URL input with validation feedback
  7. "Envoyer" button (gradient, shine animation)
  8. Share modal after success: link + copy + WhatsApp + SMS buttons

### View Page (`valentine.html`)
- Based on existing `valentine (2).html`
- Django injects data as JSON in a `<script>` tag:
  ```html
  <script>
  const VALENTINE_DATA = {{ valentine_json|safe }};
  </script>
  ```
- JS reads `VALENTINE_DATA` and:
  - Sets recipient name in hero title and bubbles
  - Uses custom acrostic if provided, else acrosticDB
  - Uses custom poem if provided, else default
  - Loads YouTube player if `youtubeId` present, else default melody
  - Sets signature with sender name
- 404 page: "Ce valentin n'existe pas... mais l'amour, lui, est partout"

---

## Implementation Steps

1. **Install Django**: `pip install django`
2. **Create Django project + app**: `django-admin startproject valentineproject .` + `python manage.py startapp core`
3. **Define model** in `core/models.py`, run migrations
4. **Create `core/utils.py`**: YouTube URL parser + rate limit helper
5. **Create `core/views.py`**: create_view + valentine_view
6. **Create `core/urls.py`** + wire into `valentineproject/urls.py`
7. **Create `core/templates/core/create.html`**: Sender form page (full styling + JS)
8. **Create `core/templates/core/valentine.html`**: Receiver page (adapted from valentine (2).html)
9. **Test full flow**: create → get link → open → see personalized valentine
10. **Clean up**: Remove old HTML files, PLAN.md
11. **Commit and push** to `claude/code-review-feedback-XPkcV`
