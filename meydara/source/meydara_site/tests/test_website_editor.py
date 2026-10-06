from copy import deepcopy
from pathlib import Path
import re

from lxml import etree, html

from odoo.tests import TransactionCase, tagged


MODULE_PATH = Path(__file__).resolve().parents[1]
RETIREMENT_SOURCE = etree.parse(str(MODULE_PATH / "views" / "content_enrichment.xml"))
RETIRED_MAPPING = {
    record.get("id"): record.xpath("field[@name='inherit_id']")[0].get("ref")
    for record in RETIREMENT_SOURCE.xpath("/odoo/record[@model='ir.ui.view']")
}


def normalized_text(element):
    return re.sub(r"\s+", " ", " ".join(element.itertext())).strip()


@tagged("post_install", "-at_install")
class TestWebsiteEditor(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.website = cls.env.ref("website.default_website")
        cls.env = cls.env(context=dict(cls.env.context, website_id=cls.website.id, lang="en_US", no_cow=True))

    def combined_wrap(self, view):
        wraps = view._get_combined_arch().xpath("//*[@id='wrap']")
        self.assertEqual(len(wraps), 1)
        return deepcopy(wraps[0])

    def rendered_wrap(self, view):
        markup = view.env["ir.qweb"]._render(self.combined_wrap(view), {}, minimal_qcontext=True)
        return html.fromstring(str(markup))

    def save_image_only(self, parent_xmlid, language):
        view = self.env.ref(parent_xmlid).with_env(self.env).with_context(lang=language)
        self.assertEqual(view.website_id, self.website)
        before = self.combined_wrap(view)
        images = before.xpath(".//img")
        self.assertTrue(images)
        original_images = [dict(image.attrib) for image in images]
        original_text = normalized_text(before)
        original_sections = etree.tostring(before, method="c14n")
        child_ids_before = self.env["ir.ui.view"].search([
            ("inherit_id", "=", view.id),
            ("website_id", "=", self.website.id),
            ("active", "=", True),
        ]).ids
        image_source = "/meydara_site/static/src/img/product/reference/hero.png?image_only_regression=1"
        images[0].set("src", image_source)
        view.save(etree.tostring(before, encoding="unicode"), xpath="//*[@id='wrap']")
        primary_arch = etree.fromstring(view.arch.encode("utf-8"))
        primary_wrap = primary_arch.xpath("//*[@id='wrap']")
        self.assertEqual(len(primary_wrap), 1)
        self.assertTrue(len(primary_wrap[0]))
        self.assertEqual(primary_wrap[0].xpath(".//img")[0].get("src"), image_source)
        self.assertEqual(self.env["ir.ui.view"].search([
            ("inherit_id", "=", view.id),
            ("website_id", "=", self.website.id),
            ("active", "=", True),
        ]).ids, child_ids_before)
        combined = self.combined_wrap(view)
        combined.xpath(".//img")[0].set("src", original_images[0]["src"])
        self.assertEqual(etree.tostring(combined, method="c14n"), original_sections)
        rendered = self.rendered_wrap(view)
        expected_images = deepcopy(original_images)
        expected_images[0]["src"] = image_source
        self.assertEqual(normalized_text(rendered), original_text)
        self.assertEqual([dict(image.attrib) for image in rendered.xpath(".//img")], expected_images)

    def save_first_image(self, parent_xmlid):
        view = self.env.ref(parent_xmlid).with_env(self.env)
        self.assertEqual(view.website_id, self.website)
        before = self.combined_wrap(view)
        images = before.xpath(".//img")
        self.assertTrue(images)
        original_images = [dict(image.attrib) for image in images]
        original_text = normalized_text(before)
        structure_id = f"oe_structure_editor_{parent_xmlid.split('.')[-1]}"
        structure = etree.Element("div", id=structure_id, attrib={"class": "oe_structure"})
        structure.text = before.text
        before.text = None
        for child in list(before):
            before.remove(child)
            structure.append(child)
        before.append(structure)
        seeded_arch = view.replace_arch_section("//*[@id='wrap']", before)
        view.write({"arch": etree.tostring(seeded_arch, encoding="unicode")})
        seeded_structure = etree.fromstring(view.arch.encode("utf-8")).xpath(
            "//*[@id=$anchor]", anchor=structure_id,
        )
        self.assertEqual(len(seeded_structure), 1)
        self.assertTrue(len(seeded_structure[0]))
        self.assertEqual(normalized_text(self.rendered_wrap(view)), original_text)
        image_source = "/meydara_site/static/src/img/product/reference/hero.png?editor_regression=1"
        structure.xpath(".//img")[0].set("src", image_source)
        view.save(etree.tostring(before, encoding="unicode"), xpath="//*[@id='wrap']")
        primary_arch = etree.fromstring(view.arch.encode("utf-8"))
        empty_anchor = primary_arch.xpath("//*[@id=$anchor]", anchor=structure_id)
        self.assertEqual(len(empty_anchor), 1)
        self.assertEqual(len(empty_anchor[0]), 0)
        self.assertFalse((empty_anchor[0].text or "").strip())
        children = self.env["ir.ui.view"].search([
            ("inherit_id", "=", view.id),
            ("key", "=", f"{view.key}_{structure_id}"),
            ("website_id", "=", self.website.id),
            ("active", "=", True),
        ])
        self.assertEqual(len(children), 1)
        rendered = self.rendered_wrap(view)
        self.assertEqual(normalized_text(rendered), original_text)
        expected_images = deepcopy(original_images)
        expected_images[0]["src"] = image_source
        self.assertEqual([dict(image.attrib) for image in rendered.xpath(".//img")], expected_images)
        return view, children, structure_id

    def save_structure(self, parent_view, child_view, structure_id, mutation):
        combined = self.combined_wrap(parent_view)
        structure = combined.xpath("//*[@id=$anchor]", anchor=structure_id)[0]
        mutation(structure)
        child_view.save(
            etree.tostring(structure, encoding="unicode"),
            xpath=f"//*[@id='{structure_id}']",
        )
        return self.rendered_wrap(parent_view)

    def test_native_block_insert_duplicate_remove(self):
        view, child, structure_id = self.save_first_image("meydara_site.page_platform")
        original = self.rendered_wrap(view)
        section_count = len(original.xpath(".//section"))
        original_images = [dict(image.attrib) for image in original.xpath(".//img")]
        marker = "Editor block regression"

        def insert_block(structure):
            section = etree.SubElement(structure, "section", attrib={"class": "s_text_block", "data-name": "Editor regression"})
            etree.SubElement(section, "p").text = marker

        inserted = self.save_structure(view, child, structure_id, insert_block)
        self.assertEqual(len(inserted.xpath(".//section")), section_count + 1)
        self.assertEqual(normalized_text(inserted).count(marker), 1)
        self.assertEqual([dict(image.attrib) for image in inserted.xpath(".//img")], original_images)

        def duplicate_block(structure):
            section = structure.xpath(".//section[@data-name='Editor regression']")[0]
            structure.append(deepcopy(section))

        duplicated = self.save_structure(view, child, structure_id, duplicate_block)
        self.assertEqual(len(duplicated.xpath(".//section")), section_count + 2)
        self.assertEqual(normalized_text(duplicated).count(marker), 2)

        def remove_blocks(structure):
            for section in structure.xpath(".//section[@data-name='Editor regression']"):
                section.getparent().remove(section)

        removed = self.save_structure(view, child, structure_id, remove_blocks)
        self.assertEqual(len(removed.xpath(".//section")), section_count)
        self.assertEqual(normalized_text(removed), normalized_text(original))
        self.assertEqual([dict(image.attrib) for image in removed.xpath(".//img")], original_images)
        self.assertEqual(len(self.env["ir.ui.view"].search([
            ("inherit_id", "=", view.id),
            ("key", "=", child.key),
            ("active", "=", True),
        ])), 1)

    def test_homepage_unwrapped_block_insert_duplicate_remove(self):
        view = self.env.ref("meydara_site.homepage").with_env(self.env)
        original = self.combined_wrap(view)
        original_architecture = etree.tostring(original, method="c14n")
        original_text = normalized_text(original)
        original_images = [dict(image.attrib) for image in original.xpath(".//img")]
        section_count = len(original.xpath(".//section"))
        child_ids_before = self.env["ir.ui.view"].search([
            ("inherit_id", "=", view.id),
            ("website_id", "=", self.website.id),
            ("active", "=", True),
        ]).ids
        marker = "Homepage editor block regression"

        def save_wrap(wrap):
            view.save(etree.tostring(wrap, encoding="unicode"), xpath="//*[@id='wrap']")
            return self.rendered_wrap(view)

        section = etree.SubElement(original, "section", attrib={"class": "s_text_block", "data-name": "Homepage editor regression"})
        etree.SubElement(section, "p").text = marker
        inserted = save_wrap(original)
        self.assertEqual(len(inserted.xpath(".//section")), section_count + 1)
        self.assertEqual(normalized_text(inserted).count(marker), 1)
        self.assertEqual([dict(image.attrib) for image in inserted.xpath(".//img")], original_images)

        wrap = self.combined_wrap(view)
        section = wrap.xpath(".//section[@data-name='Homepage editor regression']")[0]
        wrap.append(deepcopy(section))
        duplicated = save_wrap(wrap)
        self.assertEqual(len(duplicated.xpath(".//section")), section_count + 2)
        self.assertEqual(normalized_text(duplicated).count(marker), 2)

        wrap = self.combined_wrap(view)
        for section in wrap.xpath(".//section[@data-name='Homepage editor regression']"):
            section.getparent().remove(section)
        removed = save_wrap(wrap)
        self.assertEqual(len(removed.xpath(".//section")), section_count)
        self.assertEqual(normalized_text(removed), original_text)
        self.assertEqual([dict(image.attrib) for image in removed.xpath(".//img")], original_images)
        self.assertEqual(etree.tostring(self.combined_wrap(view), method="c14n"), original_architecture)
        self.assertEqual(self.env["ir.ui.view"].search([
            ("inherit_id", "=", view.id),
            ("website_id", "=", self.website.id),
            ("active", "=", True),
        ]).ids, child_ids_before)

    def test_editable_seed_xmlids_and_retired_views(self):
        self.assertEqual(len(RETIRED_MAPPING), 18)
        template_names = []
        for name in ("pages.xml", "home.xml", "contact.xml", "native_contact.xml"):
            source = etree.parse(str(MODULE_PATH / "views" / name))
            templates = source.xpath("/odoo/data[@noupdate='1']/template")
            self.assertTrue(templates, name)
            template_names.extend(template.get("id") for template in templates)
        for name in template_names:
            with self.subTest(template=name):
                model_data = self.env["ir.model.data"].search([("module", "=", "meydara_site"), ("name", "=", name)])
                self.assertEqual(len(model_data), 1)
                self.assertTrue(model_data.noupdate)
        for retired_name, parent_xmlid in RETIRED_MAPPING.items():
            with self.subTest(retired=retired_name):
                retired = self.env.ref(f"meydara_site.{retired_name}").with_env(self.env)
                self.assertFalse(retired.active)
                self.assertEqual(retired.inherit_id, self.env.ref(parent_xmlid))
                self.assertEqual(retired.website_id, self.website)
                self.assertEqual(retired.type, "qweb")
                self.assertFalse(etree.fromstring(retired.arch.encode("utf-8")).xpath("//xpath"))


def native_save_test(parent_xmlid):
    def test(self):
        self.save_first_image(parent_xmlid)

    return test


def image_only_save_test(parent_xmlid, language):
    def test(self):
        self.save_image_only(parent_xmlid, language)

    return test


for parent_xmlid in RETIRED_MAPPING.values():
    setattr(
        TestWebsiteEditor,
        f"test_native_image_save_{parent_xmlid.split('.')[-1]}",
        native_save_test(parent_xmlid),
    )
    for language in ("en_US", "ar_001"):
        setattr(
            TestWebsiteEditor,
            f"test_image_only_save_{parent_xmlid.split('.')[-1]}_{language.lower()}",
            image_only_save_test(parent_xmlid, language),
        )
