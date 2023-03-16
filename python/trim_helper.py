import json
import os
import re
import shutil

from PIL import Image

CLIENT_RESOURCE_DIR = "../src/client/resources/assets/minecraft"
SERVER_DATA_DIR = "../src/main/resources/data/minecraft"

ITEM_MODEL_DIR = f"{CLIENT_RESOURCE_DIR}/models/item"
ATLASES_DIR = f"{CLIENT_RESOURCE_DIR}/atlases"
COLOUR_PALETTES_DIR = f"{CLIENT_RESOURCE_DIR}/textures/trims/color_palettes"
TEMPLATE_DIR = f"{CLIENT_RESOURCE_DIR}/textures/trims/models/armor"

TRIM_MATERIAL_TAG_DIR = f"{SERVER_DATA_DIR}/tags/items/trim_materials"
TRIM_TEMPLATE_TAG_DIR = f"{SERVER_DATA_DIR}/tags/items/trim_templates"

TRIM_MATERIAL_DIR = f"{SERVER_DATA_DIR}/trim_material"
TRIM_TEMPLATE_DIR = f"{SERVER_DATA_DIR}/trim_pattern"

TRIM_MODEL_TEMPLATE = {
        "parent": "minecraft:item/generated",
        "textures": {
            "layer0": "minecraft:item/{armor_type}_{slot}",
            "layer1": "minecraft:trims/items/{slot}_trim_{material}"
        }
}

ARMOR_MODEL_OVERRIDE_TEMPLATE = {
    "model": "minecraft:item/{armor_type}_{slot}_{material}_trim",
    "predicate": {
        "trim_type": None
    }
}

ARMOR_MODEL_TEMPLATE = {
    "parent": "minecraft:item/generated",
    "overrides": [
    ],
    "textures": {
        "layer0": "minecraft:item/{armor_type}_{slot}",
    }
}

TRIM_MATERIAL_TEMPLATE = {
    "asset_name": None,
    "description": {
        "color": None,
        "translate": "trim_material.{modid}.{name}",
    },
    "ingredient": None,
    "item_model_index": None
}

TRIM_TEMPLATE_TEMPLATE = {
    "asset_id": "{modid}:{id}",
    "description": {
        "translate": "trim_pattern.{modid}.{id}",
    },
    "template_item": "{namespace}:{template_id}",
}

ARMOR_TRIM_PERMUTATIONS = {
    "quartz": "trims/color_palettes/quartz",
    "iron": "trims/color_palettes/iron",
    "gold": "trims/color_palettes/gold",
    "diamond": "trims/color_palettes/diamond",
    "netherite": "trims/color_palettes/netherite",
    "redstone": "trims/color_palettes/redstone",
    "copper": "trims/color_palettes/copper",
    "emerald": "trims/color_palettes/emerald",
    "lapis": "trims/color_palettes/lapis",
    "amethyst": "trims/color_palettes/amethyst",
    "iron_darker": "trims/color_palettes/iron_darker",
    "gold_darker": "trims/color_palettes/gold_darker",
    "diamond_darker": "trims/color_palettes/diamond_darker",
    "netherite_darker": "trims/color_palettes/netherite_darker"
}

ATLAS_ARMOR_TRIMS = {
    "sources": [
        {
            "type": "paletted_permutations",
            "textures": [
                "trims/models/armor/coast",
                "trims/models/armor/coast_leggings",
                "trims/models/armor/sentry",
                "trims/models/armor/sentry_leggings",
                "trims/models/armor/dune",
                "trims/models/armor/dune_leggings",
                "trims/models/armor/wild",
                "trims/models/armor/wild_leggings",
                "trims/models/armor/ward",
                "trims/models/armor/ward_leggings",
                "trims/models/armor/eye",
                "trims/models/armor/eye_leggings",
                "trims/models/armor/vex",
                "trims/models/armor/vex_leggings",
                "trims/models/armor/tide",
                "trims/models/armor/tide_leggings",
                "trims/models/armor/snout",
                "trims/models/armor/snout_leggings",
                "trims/models/armor/rib",
                "trims/models/armor/rib_leggings",
                "trims/models/armor/spire",
                "trims/models/armor/spire_leggings"
            ],
            "palette_key": "trims/color_palettes/trim_palette",
            "permutations": ARMOR_TRIM_PERMUTATIONS
        }
    ]
}

ATLAS_BLOCKS = {
    "sources": [
        {
            "type": "directory",
            "source": "block",
            "prefix": "block/"
        },
        {
            "type": "directory",
            "source": "item",
            "prefix": "item/"
        },
        {
            "type": "directory",
            "source": "entity/conduit",
            "prefix": "entity/conduit/"
        },
        {
            "type": "single",
            "resource": "entity/bell/bell_body"
        },
        {
            "type": "single",
            "resource": "entity/decorated_pot/decorated_pot_side"
        },
        {
            "type": "single",
            "resource": "entity/enchanting_table_book"
        },
        {
            "type": "paletted_permutations",
            "textures": [
                "trims/items/leggings_trim",
                "trims/items/chestplate_trim",
                "trims/items/helmet_trim",
                "trims/items/boots_trim"
            ],
            "palette_key": "trims/color_palettes/trim_palette",
            "permutations": ARMOR_TRIM_PERMUTATIONS
        }
    ]
}


TRIM_MATERIAL_TAG = {
    "replace": False,
    "values": [
    ]
}

TRIM_TEMPLATE_TAG = {
    "replace": False,
    "values": [
    ]
}

MAX_MATERIALS = 100

armor_types = ["leather", "chainmail", "iron", "gold", "diamond", "netherite"]
slots = ["helmet", "chestplate", "leggings", "boots"]
all_materials = {key: value / 10 + 0.1 for value, key in enumerate([
    "quartz",
    "iron",
    "netherite",
    "redstone",
    "copper",
    "gold",
    "emerald",
    "diamond",
    "lapis",
    "amethyst"
])}

custom_materials = {}
custom_templates = {}

modid = "minecraft"


def copy_of(original):
    return json.loads(json.dumps(original))


def set_modid(new_modid):
    global modid
    modid = new_modid
    print(f"Mod ID set to {modid}")


def set_max_materials(max_materials):
    global MAX_MATERIALS
    MAX_MATERIALS = max_materials
    print(f"Max materials set to {MAX_MATERIALS}")


def add_custom_material(name, ingredient_identifier, colour_palette_texture_path):
    # validate name and texture_path (no spaces, no special characters)
    if not re.compile(r"^[a-zA-Z0-9_]+$").match(name):
        raise ValueError("Invalid material name")
    if not re.compile(r"^[a-zA-Z0-9_./]+$").match(colour_palette_texture_path):
        raise ValueError("Invalid texture path")
    # ingredient identifier must be in the format namespace:id
    if len(ingredient_identifier.split(":")) != 2:
        raise ValueError("Invalid ingredient identifier, must be in the format namespace:id")
    # check if texture file exists
    if not os.path.isfile(colour_palette_texture_path):
        raise FileNotFoundError("Texture file not found")

    if not colour_palette_texture_path.endswith(".png"):
        raise ValueError("Invalid texture file type, must be .png")

    image = Image.open(colour_palette_texture_path)
    if image.size != (8, 1):
        raise ValueError("Invalid texture size, must be 8x1")

    custom_materials[name] = (ingredient_identifier, colour_palette_texture_path)
    all_materials[name] = (len(all_materials) - 9) / MAX_MATERIALS
    ARMOR_TRIM_PERMUTATIONS[name] = "trims/color_palettes/" + name
    print("Added custom material: " + name)


def add_custom_template(name, template_identifier, template_texture_path):
    # validate name and template_item (no spaces, no special characters)
    pattern = re.compile(r"^[a-zA-Z0-9_]+$")
    if not pattern.match(name):
        raise ValueError("Invalid template name")

    # template identifier must be in the format namespace:id
    if len(template_identifier.split(":")) != 2:
        raise ValueError("Invalid template identifier, must be in the format namespace:id")

    # check if texture file exists
    if not os.path.isfile(template_texture_path):
        raise FileNotFoundError("Texture file not found")

    if not template_texture_path.endswith(".png"):
        raise ValueError("Invalid texture file type, must be .png")

    image = Image.open(template_texture_path)
    if image.size != (16, 16):
        raise ValueError("Invalid texture size, must be 16x16")

    custom_templates[name] = (template_identifier, template_texture_path)
    ATLAS_ARMOR_TRIMS["sources"][0]["textures"].append("trims/models/armor/" + name)
    ATLAS_ARMOR_TRIMS["sources"][0]["textures"].append("trims/models/armor/" + name + "_leggings")
    print("Added custom template: " + name)


def add_material_tag(identifier):
    if len(identifier.split(":")) != 2:
        raise ValueError("Invalid material identifier, must be in the format namespace:id")
    TRIM_MATERIAL_TAG["values"].append(identifier)


def add_template_tag(identifier):
    if len(identifier.split(":")) != 2:
        raise ValueError("Invalid material identifier, must be in the format namespace:id")
    TRIM_TEMPLATE_TAG["values"].append(identifier)


def create_tag_files():
    os.makedirs(TRIM_MATERIAL_TAG_DIR, exist_ok=True)
    os.makedirs(TRIM_TEMPLATE_TAG_DIR, exist_ok=True)
    with open(os.path.join(TRIM_MATERIAL_TAG_DIR, "trim_materials.json"), "w") as f:
        json.dump(TRIM_MATERIAL_TAG, f, indent=4)
    with open(os.path.join(TRIM_TEMPLATE_TAG_DIR, "trim_templates.json"), "w") as f:
        json.dump(TRIM_TEMPLATE_TAG, f, indent=4)


def create_trim_material_files():
    for name, (ingredient_identifier, colour_palette_texture_path) in custom_materials.items():
        material = copy_of(TRIM_MATERIAL_TEMPLATE)
        material["asset_name"] = name
        material["description"]["translate"] = material["description"]["translate"].format(modid=modid, name=name)
        material["ingredient"] = ingredient_identifier
        material["item_model_index"] = all_materials[name]

        # get lightest colour from texture
        image = Image.open(colour_palette_texture_path)
        lightest_colour = image.getpixel((0, 0))
        for x in range(1, 8):
            colour = image.getpixel((x, 0))
            if colour[0] + colour[1] + colour[2] > lightest_colour[0] + lightest_colour[1] + lightest_colour[2]:
                lightest_colour = colour
        material["description"]["color"] = "#{:02x}{:02x}{:02x}".format(lightest_colour[0], lightest_colour[1], lightest_colour[2]).upper()

        os.makedirs(TRIM_MATERIAL_DIR, exist_ok=True)
        with open(os.path.join(TRIM_MATERIAL_DIR, f"{name}.json"), "w") as f:
            json.dump(material, f, indent=4)


def create_trim_template_files():
    for name, (template_identifier, template_texture_path) in custom_templates.items():
        template = copy_of(TRIM_TEMPLATE_TEMPLATE)
        template["asset_id"] = template["asset_id"].format(modid=modid, id=name)
        template["description"]["translate"] = template["description"]["translate"].format(modid=modid, id=name)
        template["template_item"] = template_identifier

        os.makedirs(TRIM_TEMPLATE_DIR, exist_ok=True)
        with open(os.path.join(TRIM_TEMPLATE_DIR, f"{name}.json"), "w") as f:
            json.dump(template, f, indent=4)


def create_atlas_files():
    os.makedirs(ATLASES_DIR, exist_ok=True)
    with open(os.path.join(ATLASES_DIR, "armor_trims.json"), "w") as f:
        json.dump(ATLAS_ARMOR_TRIMS, f, indent=4)
    with open(os.path.join(ATLASES_DIR, "blocks.json"), "w") as f:
        json.dump(ATLAS_BLOCKS, f, indent=4)


def create_model_files():
    for armor_type in armor_types:
        for slot in slots:
            for material_name in custom_materials.keys():
                if material_name == armor_type:
                    material_name = material_name + "_darker"
                model = json.loads(json.dumps(TRIM_MODEL_TEMPLATE))
                model["textures"]["layer0"] = model["textures"]["layer0"]\
                    .format(armor_type=armor_type, slot=slot)
                model["textures"]["layer1"] = model["textures"]["layer1"]\
                    .format(slot=slot, material=material_name)

                if armor_type == "leather":
                    model["textures"]["layer2"] = model["textures"]["layer1"]
                    model["textures"]["layer1"] = f"minecraft:item/leather_{slot}_overlay"

                model_path = os.path.join(ITEM_MODEL_DIR, f"{armor_type}_{slot}_{material_name}_trim.json")
                os.makedirs(os.path.dirname(model_path), exist_ok=True)
                with open(model_path, "w") as f:
                    json.dump(model, f, indent=4)

            model = json.loads(json.dumps(ARMOR_MODEL_TEMPLATE))
            for material_name in all_materials:
                if material_name == armor_type:
                    material_name = material_name + "_darker"
                model["overrides"].append(json.loads(json.dumps(ARMOR_MODEL_OVERRIDE_TEMPLATE)))
                model["overrides"][-1]["model"] = model["overrides"][-1]["model"]\
                    .format(armor_type=armor_type, slot=slot, material=material_name)
                if material_name not in all_materials:
                    material_name = material_name[:-7]
                model["overrides"][-1]["predicate"]["trim_type"] = round(all_materials[material_name],
                                                                         len(str(MAX_MATERIALS)))
                model["textures"]["layer0"] = model["textures"]["layer0"]\
                    .format(armor_type=armor_type, slot=slot)
            model_path = os.path.join(ITEM_MODEL_DIR, f"{armor_type}_{slot}.json")
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            with open(model_path, "w") as f:
                json.dump(model, f, indent=4)


def create_texture_files():
    for name, (ingredient_identifier, colour_palette_texture_path) in custom_materials.items():
        # move the colour palette texture to the correct location
        os.makedirs(COLOUR_PALETTES_DIR, exist_ok=True)
        shutil.copyfile(colour_palette_texture_path, os.path.join(COLOUR_PALETTES_DIR, f"{name}.png"))
    for name, (template_identifier, template_texture_path) in custom_templates.items():
        # move the template texture to the correct location
        os.makedirs(TEMPLATE_DIR, exist_ok=True)
        shutil.copyfile(template_texture_path, os.path.join(TEMPLATE_DIR, f"{name}.png"))


def create_files():
    create_tag_files()
    create_trim_material_files()
    create_trim_template_files()
    create_atlas_files()
    create_model_files()
    create_texture_files()
    print(f"Created armor trim files for {modid}")
