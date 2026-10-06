import re

from lxml import etree

from odoo import api, SUPERUSER_ID


def rename_text(value):
    return re.sub(r"\bMeydara\b", lambda match: "MIDARA" if match.group().isupper() else "Midara", value or "", flags=re.IGNORECASE)


def rename_arch(value, editable_images=False):
    tree = etree.fromstring(value.encode())
    for node in tree.iter():
        if not isinstance(node.tag, str):
            continue
        if node.text:
            node.text = rename_text(node.text)
        if node.tail:
            node.tail = rename_text(node.tail)
        if node.text == "Mey" and len(node) and node[0].tag == "span" and node[0].text == "dara":
            node.text = "Mi"
        for attribute in ("alt", "title", "aria-label", "data-name", "placeholder", "value"):
            if attribute in node.attrib:
                node.set(attribute, rename_text(node.get(attribute)))
    # Native editor converts width/height attributes to inline pixel dimensions.
    # Editable media uses Bootstrap responsive sizing so a save keeps the layout.
    for image in tree.xpath("//img") if editable_images else ():
        image.attrib.pop("width", None)
        image.attrib.pop("height", None)
        classes = (image.get("class") or "").split()
        if "img-fluid" not in classes:
            classes.append("img-fluid")
        image.set("class", " ".join(classes))
    return etree.tostring(tree, encoding="unicode")


def normalized_tree(value):
    return tuple(
        (node.tag, tuple(sorted(node.attrib.items())), " ".join((node.text or "").split()), " ".join((node.tail or "").split()))
        for node in etree.fromstring(value.encode()).iter()
        if isinstance(node.tag, str)
    )


def rename_translated_arch(view, languages, editable_images=False):
    originals = {
        language: view.with_context(lang=language, delay_translations=False).arch_db
        for language in languages
    }
    values = {
        language: rename_arch(value, editable_images=editable_images)
        for language, value in originals.items()
    }
    if all(normalized_tree(value) == normalized_tree(originals[lang]) for lang, value in values.items()):
        return
    english = values["en_US"]
    field = view._fields["arch_db"]
    count = len(field.get_trans_terms(english))
    if any(len(field.get_trans_terms(value)) != count for value in values.values()):
        raise ValueError("Brand migration cannot preserve the translated architecture")
    dictionary = field.get_translation_dictionary(english, {lang: value for lang, value in values.items() if lang != "en_US"})
    view.with_context(lang="en_US", no_cow=True).write({"arch_db": english})
    view.update_field_translations("arch_db", {
        lang: {term: translations[lang] for term, translations in dictionary.items()}
        for lang in values if lang != "en_US"
    }, source_lang="en_US")
    for lang, expected in values.items():
        if normalized_tree(view.with_context(lang=lang, delay_translations=False).arch_db) != normalized_tree(expected):
            raise ValueError("Brand migration changed unrelated translated content")


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {"no_cow": True, "delay_translations": False})
    website = env.ref("website.default_website")
    languages = list(dict.fromkeys(["en_US", *website.language_ids.mapped("code")]))
    owned_views = env["ir.model.data"].search([("module", "=", "meydara_site"), ("model", "=", "ir.ui.view")]).mapped("res_id")
    editable = env["website.page"].search([("website_id", "=", website.id)]).mapped("view_id")
    editable = editable.filtered(lambda view: (view.key or "").startswith("meydara_site."))
    editable |= env.ref("meydara_site.native_contact")
    frontier = editable
    while frontier:
        children = env["ir.ui.view"].with_context(active_test=False).search([
            ("inherit_id", "in", frontier.ids), ("website_id", "=", website.id),
        ]) - editable
        editable |= children
        frontier = children
    views = env["ir.ui.view"].with_context(active_test=False).search([("website_id", "=", website.id)])
    views = views.filtered(lambda view: view.id in owned_views or view in editable or (view.key or "").startswith("meydara_site."))
    for view in views:
        rename_translated_arch(view, languages, editable_images=view in editable)
        for field_name in ("name", "website_meta_title", "website_meta_description", "website_meta_keywords"):
            if field_name not in view._fields:
                continue
            for lang in languages if view._fields[field_name].translate else ["en_US"]:
                localized = view.with_context(lang=lang)
                previous = localized[field_name]
                updated = rename_text(previous)
                if previous and previous != updated:
                    localized.write({field_name: updated})
    updated_name = rename_text(website.name)
    if updated_name != website.name:
        website.write({"name": updated_name})
    owned_menus = env["ir.model.data"].search([("module", "=", "meydara_site"), ("model", "=", "website.menu")]).mapped("res_id")
    for menu in env["website.menu"].browse(owned_menus).exists().filtered(lambda menu: menu.website_id == website):
        for lang in languages:
            localized = menu.with_context(lang=lang)
            updated = rename_text(localized.name)
            if updated != localized.name:
                localized.write({"name": updated})
