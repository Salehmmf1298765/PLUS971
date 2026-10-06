from pathlib import Path

from lxml import etree

from odoo import api, SUPERUSER_ID


def normalize_tree(tree):
    return tuple(
        (node.tag, tuple(sorted(node.attrib.items())), " ".join((node.text or "").split()), " ".join((node.tail or "").split()))
        for node in tree.iter()
        if isinstance(node.tag, str)
    )


def prepare_editor_views(env):
    source = Path(__file__).resolve().parents[2]
    website = env.ref("website.default_website")
    retirement = etree.parse(str(source / "views" / "content_enrichment.xml"))
    snapshots = {}
    seeds = {}
    legacy_views = env["ir.ui.view"]
    languages = list(dict.fromkeys(["en_US", *website.language_ids.mapped("code")]))
    for record in retirement.xpath("//record[@model='ir.ui.view']"):
        legacy = env.ref("meydara_site." + record.get("id"), raise_if_not_found=False)
        parent_ref = record.xpath("field[@name='inherit_id']/@ref")[0]
        parent = env.ref(parent_ref)
        if parent.website_id != website or parent.mode != "primary" or parent.inherit_id:
            raise ValueError("Editable page binding differs from the expected website")
        if not legacy or not legacy.active:
            continue
        if legacy.website_id != website or legacy.inherit_id != parent:
            raise ValueError("Legacy content view binding differs from the expected page")
        if env["ir.ui.view"].search_count([("inherit_id", "=", legacy.id), ("active", "=", True)]):
            raise ValueError("Legacy content has dependent views requiring a separate migration")
        snapshots[parent.id] = {
            language: etree.tostring(
                parent.with_context(lang=language, website_id=website.id, load_all_views=True)._get_combined_arch(),
                encoding="unicode",
            )
            for language in languages
        }
        seeds[parent.id] = {
            language: etree.tostring(
                parent.apply_inheritance_specs(
                    etree.fromstring(parent.with_context(lang=language).arch.encode()),
                    etree.fromstring(legacy.with_context(lang=language).arch.encode()),
                ),
                encoding="unicode",
            )
            for language in languages
        }
        legacy_views |= legacy
    legacy_views.with_context(no_cow=True).write({"active": False})
    for parent_id, translations in seeds.items():
        parent = env["ir.ui.view"].browse(parent_id).with_context(no_cow=True, delay_translations=False)
        english = translations["en_US"]
        field = parent._fields["arch_db"]
        english_terms = field.get_trans_terms(english)
        if any(len(field.get_trans_terms(value)) != len(english_terms) for value in translations.values()):
            raise ValueError("Page translation structures differ; flattening cannot preserve them safely")
        dictionary = field.get_translation_dictionary(english, {lang: value for lang, value in translations.items() if lang != "en_US"})
        parent.with_context(lang="en_US").write({"arch_db": english})
        translated_terms = {
            lang: {term: values[lang] for term, values in dictionary.items()}
            for lang in translations if lang != "en_US"
        }
        parent.update_field_translations("arch_db", translated_terms, source_lang="en_US")
        for language, previous in snapshots[parent_id].items():
            actual = parent.with_context(lang=language, website_id=website.id, load_all_views=True)._get_combined_arch()
            if normalize_tree(actual) != normalize_tree(etree.fromstring(previous.encode())):
                raise ValueError("Page content or translations changed during editor migration")
    for filename in ("home.xml", "pages.xml", "contact.xml", "native_contact.xml"):
        document = etree.parse(str(source / "views" / filename))
        for template in document.xpath("//template[@id]"):
            view = env.ref("meydara_site." + template.get("id"), raise_if_not_found=False)
            if view and view.website_id != website:
                raise ValueError("Editable view binding differs from the expected website")
            if view:
                env["ir.model.data"].search([
                    ("module", "=", "meydara_site"), ("name", "=", template.get("id")),
                    ("model", "=", "ir.ui.view"), ("res_id", "=", view.id),
                ]).write({"noupdate": True})
    return {"flattened_pages": len(snapshots), "retired_content_views": len(legacy_views)}


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {"lang": None, "no_cow": True})
    prepare_editor_views(env)
