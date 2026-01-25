#!/usr/bin/env python3
import sys
import gi

gi.require_version("Gimp", "3.0")
gi.require_version("Gio", "2.0")
gi.require_version("Gegl", "0.4")

from gi.repository import Gimp, Gio, GLib, Gegl


# ==============================================================
# Tipos de imagem – tamanhos IDEAIS (KDP + todos os dispositivos)
# ==============================================================

IMAGE_TYPES = {
    "capa": {
        "width": 2560,
        "height": 1600,
        "safe_ratio": 0.08,
    },
    "abertura_capitulo": {
        "width": 2400,
        "height": 1350,
        "safe_ratio": 0.05,
    },
    "ilustracao": {
        "width": 2400,
        "height": 1800,
        "safe_ratio": 0.05,
    },
    "imagem_informativa": {
        "width": 2400,
        "height": 1600,
        "safe_ratio": 0.06,
    },
    "linha_do_tempo": {
        "width": 2560,
        "height": 900,
        "safe_ratio": 0.05,
    },
    "mapa": {
        "width": 2560,
        "height": 1800,
        "safe_ratio": 0.05,
    },
    "personagem": {
        "width": 1800,
        "height": 2400,
        "safe_ratio": 0.05,
    },
    "ambiente": {
        "width": 2560,
        "height": 1440,
        "safe_ratio": 0.05,
    },
    "fac_simile": {
        "width": 1800,
        "height": 2600,
        "safe_ratio": 0.03,
    },
    "divisor": {
        "width": 1600,
        "height": 300,
        "safe_ratio": 0.10,
    },
    "ornamento": {
        "width": 1400,
        "height": 400,
        "safe_ratio": 0.10,
    },
    "decorativa_pura": {
        "width": 2000,
        "height": 1400,
        "safe_ratio": 0.10,
    },
}

SAFE_STROKE_COLOR = "#00ff00"
SAFE_STROKE_WIDTH = 2.0


# ==============================================================
# Plug-in
# ==============================================================

class KindleTemplates(Gimp.PlugIn):
    __gtype_name__ = "KindleTemplates"

    # i18n explicitamente desativado
    def set_i18n(self):
        return False

    # ----------------------------------------------------------
    # Registro
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

        procedure.set_menu_label("Criar templates Kindle (por tipo de imagem)")
        procedure.add_menu_path("<Image>/File/Create/Kindle")
        procedure.set_documentation(
            "Cria templates Kindle por tipo de imagem",
            "Gera XCFs com SAFE-AREA e guias para cada tipo semântico",
            name,
        )
        procedure.set_attribution("mjucimara", "mjucimara", "2026")
        procedure.set_sensitivity_mask(Gimp.ProcedureSensitivityMask.ALWAYS)

        return procedure

    # ----------------------------------------------------------
    # Execução principal
    # ----------------------------------------------------------
    def run(self, procedure, run_mode, image, n_drawables, drawables, args):

        for image_type, spec in IMAGE_TYPES.items():
            width = spec["width"]
            height = spec["height"]
            safe_ratio = spec["safe_ratio"]

            img = self._create_image(width, height)

            self._new_layer(img, "ARTE", width, height).fill(
                Gimp.FillType.WHITE
            )
            safe_layer = self._new_layer(
                img, "SAFE-AREA", width, height
            )

            self._draw_safe_area(
                img, safe_layer, width, height, safe_ratio
            )
            self._lock_layer(safe_layer)
            self._add_guides(img, width, height, safe_ratio)
            self._save_template(img, image_type, width, height)

            img.delete()

        return procedure.new_return_values(
            Gimp.PDBStatusType.SUCCESS,
            None,
        )

    # ----------------------------------------------------------
    # Criação da imagem e camadas
    # ----------------------------------------------------------
    def _create_image(self, width, height):
        return Gimp.Image.new(
            width,
            height,
            Gimp.ImageBaseType.RGB,
        )

    def _new_layer(self, image, name, width, height):
        layer = Gimp.Layer.new(
            image,
            name,
            width,
            height,
            Gimp.ImageType.RGBA_IMAGE,
            100.0,
            Gimp.LayerMode.NORMAL,
        )
        image.insert_layer(layer, None, 0)
        return layer

    # ----------------------------------------------------------
    # SAFE-AREA
    # ----------------------------------------------------------
    def _draw_safe_area(self, image, layer, width, height, ratio):
        margin_x = int(width * ratio)
        margin_y = int(height * ratio)

        image.select_rectangle(
            Gimp.ChannelOps.REPLACE,
            margin_x,
            margin_y,
            width - margin_x * 2,
            height - margin_y * 2,
        )

        Gimp.context_set_foreground(
            Gegl.Color.new(SAFE_STROKE_COLOR)
        )
        Gimp.context_set_line_width(SAFE_STROKE_WIDTH)

        layer.edit_stroke_item(layer)
        Gimp.Selection.none(image)

    def _lock_layer(self, layer):
        layer.set_lock_content(True)
        layer.set_lock_position(True)

    # ----------------------------------------------------------
    # Guias
    # ----------------------------------------------------------
    def _add_guides(self, image, width, height, ratio):
        margin_x = int(width * ratio)
        margin_y = int(height * ratio)

        image.add_hguide(margin_y)
        image.add_hguide(height - margin_y)
        image.add_vguide(margin_x)
        image.add_vguide(width - margin_x)

    # ----------------------------------------------------------
    # Salvamento
    # ----------------------------------------------------------
    def _save_template(self, image, image_type, width, height):
        base_dir = f"{GLib.get_home_dir()}/.config/GIMP/3.0/templates/Kindle"
        type_dir = f"{base_dir}/{image_type}"
    
        GLib.mkdir_with_parents(type_dir, 0o755)
    
        filename = f"{image_type}_{width}x{height}.xcf"
        file = Gio.File.new_for_path(
            f"{type_dir}/{filename}"
        )
    
        Gimp.file_save(
            Gimp.RunMode.NONINTERACTIVE,
            image,
            file,
            None,
        )
    


# ==============================================================
# Entrada
# ==============================================================

Gimp.main(KindleTemplates.__gtype_name__, sys.argv)
