# PLUS971 Real Estate — Website

Two static sites, no build step. Open any `.html` file directly in a browser.

| Folder | What it is |
|---|---|
| `redesign/` | **New website** built from the client's revision notes (Website.docx): Home, About Us, Our Services, Developers, Contact Us. Unified Black & Gold identity. Fixed header that turns solid on scroll, full-screen menu, page-transition curtain, scroll reveals, horizontal snap carousels and a bottom tab bar on phones (app-like). |
| `clone/` | Replica of the current site at plus971re.odoo.com (Home, About, CEO's Message), kept for before/after comparison. |

## Redesign notes

- Contact details everywhere: +971 56 570 0034 (phone & WhatsApp), Info@plus971re.ae.
- Licenses: Trade License 1616901 · RERA Office 61192 · Dubai Chamber 680891.
- No developer logos or "Our Partners" wording (per notes §15–16); no listings or prices.
- Photos are real Dubai photography from Unsplash (free licence), loaded from `images.unsplash.com`. For production, download and self-host them in `redesign/assets/img/`.
- The contact form currently opens the visitor's email app addressed to Info@plus971re.ae; connect it to a form backend (Odoo, Formspree, etc.) when hosting.
- The LinkedIn URL (`linkedin.com/company/plus971-real-estate`) is a best guess; confirm the exact company page.
- Styles: `redesign/assets/css/style.css` (single gold `#C6A15B`, black `#0B0B0C`, charcoal `#141416`, off-white `#F6F3EE`).
