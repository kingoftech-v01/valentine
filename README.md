# valentine

A small, self-contained HTML Valentine's Day card - animated, responsive, and written in pure HTML + CSS (no build step, no dependencies).

💕 A little love letter in code. 💕

## What's inside

Three variants of the same card. Open any of them directly in a browser to view:

| File | Notes |
|------|-------|
| `valentine.html` | Main version |
| `valentine (1).html` | Alternate variant |
| `valentine (2).html` | Alternate variant |

Each file is a fully standalone page with:

- A deep rose / wine gradient background
- Floating animated hearts
- Pulsing hero hearts
- Custom heart-shaped cursor
- Serif typography (Great Vibes, Playfair Display, Lora) loaded from Google Fonts
- French copy ("Joyeuse Saint-Valentin")

## Usage

Clone the repo and open a file in your browser:

```bash
git clone https://github.com/kingoftech-v01/valentine.git
cd valentine
xdg-open valentine.html   # Linux
open valentine.html       # macOS
start valentine.html      # Windows
```

No build step, no install - it's just HTML, CSS and a bit of inline JavaScript.

## Customization

- Change the recipient's name or message directly in the HTML.
- Tweak the colors via the `:root` CSS variables (`--rose-deep`, `--rose-hot`, `--gold`, `--wine`, …).
- Adjust the density of floating hearts in the `hearts-container` section.

## Contributing

Pull requests welcome - new card variants, accessibility improvements, English translations, or lighter alternatives that work offline (without the Google Fonts dependency) are all appreciated.

## License

No license file is attached. Feel free to open an issue if you'd like to reuse this code.
