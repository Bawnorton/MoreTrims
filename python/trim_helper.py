import json
import os

ITEM_MODEL_DIR = "../src/client/resources/assets/minecraft/models/item"

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

armor_types = ["leather", "chainmail", "iron", "gold", "diamond", "netherite"]
slots = ["helmet", "chestplate", "leggings", "boots"]
custom_materials = ["echo", "prismarine"]
all_materials = {key: value / 10 for value, key in enumerate([
    "quartz",
    "iron",
    "netherite",
    "redstone",
    "copper",
    "gold",
    "emerald",
    "diamond",
    "lapis",
    "amethyst",
    "echo",
    "prismarine"
])}


def main():
    for armor_type in armor_types:
        for slot in slots:
            for material in custom_materials:
                if material == armor_type:
                    material = material + "_darker"
                model = json.loads(json.dumps(TRIM_MODEL_TEMPLATE))
                model["textures"]["layer0"] = model["textures"]["layer0"]\
                    .format(armor_type=armor_type, slot=slot)
                model["textures"]["layer1"] = model["textures"]["layer1"]\
                    .format(slot=slot, material=material)

                if armor_type == "leather":
                    model["textures"]["layer2"] = model["textures"]["layer1"]
                    model["textures"]["layer1"] = f"minecraft:item/leather_{slot}_overlay"

                model_path = os.path.join(ITEM_MODEL_DIR, f"{armor_type}_{slot}_{material}_trim.json")
                os.makedirs(os.path.dirname(model_path), exist_ok=True)
                with open(model_path, "w") as f:
                    json.dump(model, f, indent=4)

            model = json.loads(json.dumps(ARMOR_MODEL_TEMPLATE))
            for material in all_materials:
                if material == armor_type:
                    material = material + "_darker"
                model["overrides"].append(json.loads(json.dumps(ARMOR_MODEL_OVERRIDE_TEMPLATE)))
                model["overrides"][-1]["model"] = model["overrides"][-1]["model"]\
                    .format(armor_type=armor_type, slot=slot, material=material)
                if material not in all_materials:
                    material = material[:-7]
                trim_type = all_materials[material] + 0.1
                if trim_type > 1.0:
                    trim_type /= 10
                model["overrides"][-1]["predicate"]["trim_type"] = round(trim_type, 3)
                model["textures"]["layer0"] = model["textures"]["layer0"]\
                    .format(armor_type=armor_type, slot=slot)
            model_path = os.path.join(ITEM_MODEL_DIR, f"{armor_type}_{slot}.json")
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            with open(model_path, "w") as f:
                json.dump(model, f, indent=4)


if __name__ == "__main__":
    main()
