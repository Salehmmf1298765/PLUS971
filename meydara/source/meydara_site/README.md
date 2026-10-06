# Midara Site

Independent Odoo 19 website addon created on 8 September 2026.
It does not depend on or modify the previous `meydara_website` addon.

Source text is English. Arabic is in `i18n/ar_001.po`, exported from
the installed module with Odoo's `trans_export`, translated, imported and
exported again. Odoo supplies the language direction and localized styles.

The site contains 23 page records, including a 16-section homepage, product
tour, platform, reports, assistant, integrations, solutions, pricing,
ten workflow pages, contact, presentation request and confirmation.
Application media are the supplied product screenshots.
The customer-map and Odoo performance screenshots were captured from the
running application on 8 September 2026 (actions 624 and 613). They capture
the application work area, excluding environment notifications and account
controls. Report grouping was selected through the application's filters;
no screen values were fabricated. Full-resolution links accompany these images.

## Preview

- Arabic: http://127.0.0.1:8089/ar/home
- English: http://127.0.0.1:8089/home
- Database: `meydara_site_new_20260908`
- Runtime: Odoo 19 Community, local interface only.
- Default website is the installation target. This addon is intended for
  a dedicated website database; retarget scoped XML records before installing
  into a database whose default website belongs to another brand.

The header uses native Odoo menu recursion, language selection and account
controls. The footer intentionally removes Odoo's default copyright strip.
Menu seeds and theme font settings are protected with `noupdate`.
Alexandria is supplied locally and seeded through Odoo's editable theme values.
Page architecture is seeded by this addon and then owned by the Website Builder.
The page seeds use `noupdate` so addon upgrades preserve saved editor changes.
Later source content changes require an explicit content migration; an addon
upgrade alone must not replace the editor's page architecture.

The current design follows the local Madarik reference at port 8040:
connected header and hero, asymmetric media panels, workflow cards and angled
section boundaries, recolored for Midara. Headings are approximately 10% smaller
than the initial adaptation. Scroll reveals use opacity only, once per section,
without lateral movement, layout changes or repeating entrance animations.
Reduced-motion preferences are respected.

## Verified locally

- XML parsing, manifest paths and HTML validation.
- Addon installation, repeated upgrades and service restarts.
- 42 exposed English/Arabic routes: HTTP 200, one main heading, no default
  copyright strip.
- Homepage at 320, 375, 390, 768, 1024 and 1440 px in both languages:
  no horizontal overflow.
- Actual desktop/mobile screenshots, native mobile navigation,
  Arabic direction, local font, tour selection and image loading.
- Editor root branding and content editability; standard block insertion,
  undo and save.
- Public presentation form submission, confirmation redirect and persisted
  CRM record including team size. The verification record was archived.
- Homepage localized metadata, self-canonical and language alternates.
- Footer copy contrast: 6.15:1; footer CTA text: 7.80:1; green primary CTA
  text: 5.14:1 in the inspected normal states.

The preceding verification list is historical (September 2026), not a current
production-state statement.
The contact details, commercial scope and product capability descriptions
remain subject to business review before public launch.

## Editor repair staged on 4 October 2026

Version `19.0.4.13.0` consolidates the 18 content enrichment views into their
original editable page templates, retaining the existing content, images and
visual identity. The former enrichment XMLIDs remain as inactive empty views.
The pre-upgrade migration preserves the installed English/Arabic content and
existing sibling editor views, verifies the resulting combined architecture,
and aborts if it cannot preserve it. Homepage and contact seeds are protected
as well; the redundant empty homepage seed has been removed.

Editable content images use native `img-fluid` without intrinsic width/height
attributes. Odoo's HTML editor otherwise converts those attributes to fixed
inline pixels when saving a replacement image. The upgrade normalizes this
within editable page/contact inheritance families while preserving intentional
inline styles and layout-logo dimensions.

Disposable-clone proof on 4 October completed: 57 native save tests passed,
actual Website Builder image replacement and block insertion/move/padding/
duplicate/removal survived reload, and a repeated upgrade preserved all 24
protected view architectures. English/Arabic page text and legal-page output
were checked against the pre-upgrade clone. This is clone evidence only; the
live site addon remains version `19.0.4.12.0` pending supervisor review.
Anonymous post-save homepage rendering still requires a fresh-runtime check
after the rescue lane is idle; authenticated rendering and stored architecture
are proven. Current evidence and caveats: `tasks/central_domain/evidence/site_editor_clone/`
and `CODEX_TO_CLAUDE_CD_0029.md`. Image provenance/cropping replacement is a
separate planned increment `19.0.4.14.0`; current product artwork is not certified
as real complete screenshots by this editor repair.
