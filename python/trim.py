import trim_helper


def main():
    trim_helper.set_modid("moretrims")
    trim_helper.add_custom_material("echo", "minecraft:echo_shard", "palettes/echo.png")
    trim_helper.add_custom_material("prismarine", "minecraft:prismarine_crystals", "palettes/prismarine.png")
    trim_helper.create_files()


if __name__ == '__main__':
    main()
