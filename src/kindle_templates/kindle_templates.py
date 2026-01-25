#!/usr/bin/env python3
import sys
import gi

gi.require_version("Gimp", "3.0")
gi.require_version("Gio", "2.0")
gi.require_version("Gegl", "0.4")

from gi.repository import Gimp, Gio, GLib, Gegl


# ==============================================================
# Constantes do template
# ==============================================================

TEMPLATE_WIDTH = 1600
TEMPLATE_HEIGHT = 900

SAFE_MARGIN_RATIO = 0.05

SAFE_STROKE_COLOR = "#00ff00"
SAFE_STROKE_WIDTH = 2.0

TEMPLATE_FILENAME = "Kindle_SAFE_1600x900.xcf"


# ==============================================================
# Plug-in
# ==============================================================

class KindleTemplates(Gimp.PlugIn):
    __gtype_name__ = "KindleTemplates"

    # ----------------------------------------------------------
    # i18n explicitamente desativado
    # ----------------------------------------------------------
    def set_i18n(self):
        return False

    # ----------------------------------------------------------
    # Registro do procedimento
    # ----------------------------------------------------------
    def do_query_procedures(self):
        return ["plug-in-kindle-template-min"]

    def do_create_procedure(self, name):
        procedure = Gimp.ImageProcedure.new(
            self,
            name,
            Gimp.PDBProcType.PLUGIN,
            self.run,
            None,
        )

        procedure.set_menu_label("Criar template Kindle (SAFE-AREA)")
        procedure.add_menu_path("<Image>/File/Create/Kindle")
        procedure.set_documentation(
            "Cria um template Kindle com SAFE-AREA",
            "Gera um XCF com guias e área segura",
            name,
        )
        procedure.set_attribution("mjucimara", "mjucimara", "2026")
        procedure.set_sensitivity_mask(Gimp.ProcedureSensitivityMask.ALWAYS)

        return procedure

    # ----------------------------------------------------------
    # Execução principal
    # ----------------------------------------------------------
    def run(self, procedure, run_mode, image, n_drawables, drawables, args):
        img = self._create_image()

        self._create_art_layer(img)
        safe_layer = self._create_safe_layer(img)

        self._draw_safe_area(img, safe_layer)
        self._lock_layer(safe_layer)
        self._add_guides(img)
        self._save_template(img)

        img.delete()

        return procedure.new_return_values(
            Gimp.PDBStatusType.SUCCESS,
            None,
        )

    # ----------------------------------------------------------
    # Criação da imagem e camadas
    # ----------------------------------------------------------
    def _create_image(self):
        return Gimp.Image.new(
            TEMPLATE_WIDTH,
            TEMPLATE_HEIGHT,
            Gimp.ImageBaseType.RGB,
        )

    def _create_art_layer(self, image):
        layer = self._new_layer(image, "ARTE")
        layer.fill(Gimp.FillType.WHITE)
        return layer

    def _create_safe_layer(self, image):
        return self._new_layer(image, "SAFE-AREA")

    def _new_layer(self, image, name):
        layer = Gimp.Layer.new(
            image,
            name,
            TEMPLATE_WIDTH,
            TEMPLATE_HEIGHT,
            Gimp.ImageType.RGBA_IMAGE,
            100.0,
            Gimp.LayerMode.NORMAL,
        )
        image.insert_layer(layer, None, 0)
        return layer

    # ----------------------------------------------------------
    # SAFE-AREA
    # ----------------------------------------------------------
    def _draw_safe_area(self, image, layer):
        margin_x = int(TEMPLATE_WIDTH * SAFE_MARGIN_RATIO)
        margin_y = int(TEMPLATE_HEIGHT * SAFE_MARGIN_RATIO)

        image.select_rectangle(
            Gimp.ChannelOps.REPLACE,
            margin_x,
            margin_y,
            TEMPLATE_WIDTH - margin_x * 2,
            TEMPLATE_HEIGHT - margin_y * 2,
        )

        Gimp.context_set_foreground(Gegl.Color.new(SAFE_STROKE_COLOR))
        Gimp.context_set_line_width(SAFE_STROKE_WIDTH)

        layer.edit_stroke_item(layer)
        Gimp.Selection.none(image)

    def _lock_layer(self, layer):
        layer.set_lock_content(True)
        layer.set_lock_position(True)

    # ----------------------------------------------------------
    # Guias
    # ----------------------------------------------------------
    def _add_guides(self, image):
        margin_x = int(TEMPLATE_WIDTH * SAFE_MARGIN_RATIO)
        margin_y = int(TEMPLATE_HEIGHT * SAFE_MARGIN_RATIO)

        image.add_hguide(margin_y)
        image.add_hguide(TEMPLATE_HEIGHT - margin_y)
        image.add_vguide(margin_x)
        image.add_vguide(TEMPLATE_WIDTH - margin_x)

    # ----------------------------------------------------------
    # Salvamento
    # ----------------------------------------------------------
    def _save_template(self, image):
        templates_dir = f"{GLib.get_home_dir()}/.config/GIMP/3.0/templates"
        GLib.mkdir_with_parents(templates_dir, 0o755)

        file = Gio.File.new_for_path(
            f"{templates_dir}/{TEMPLATE_FILENAME}"
        )

        Gimp.file_save(
            Gimp.RunMode.NONINTERACTIVE,
            image,
            file,
            None,
        )


# ==============================================================
# Entrada do plug-in
# ==============================================================

Gimp.main(KindleTemplates.__gtype_name__, sys.argv)
