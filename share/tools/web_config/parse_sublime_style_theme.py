import json as js
import argparse as argp

# todo - convertion between config color names and set_color
def fishify_color(color_string):
    return color_string


def make_style(foreground, background, font_style):
    if foreground is None and background is None and font_style is None:
        return None
    foreground = fishify_color(foreground) if foreground else ""
    background = "--background {}".format(fishify_color(background)) if background else ""
    font_style = font_style or ""
    font_style_str = ""
    for flag, name in (("--bold ", "bold"), ("--italics ", "italics")):
        if name in font_style:
            font_style_str += flag
    return "{} {} {}".format(foreground, background, font_style_str)


class StyleConfig:

    def __init__(self, path):
        with open(path) as json_file:
            self.config_dict = js.load(json_file)
        # replace list of rules with dict sorted by rule scope, last scope counts
        if "rules" in self.config_dict:
            self.config_dict["rules"] = {
                rule["scope"]: rule for rule in self.config_dict["rules"]
            }

    def get_by_path(self, path, default=None):
        if path is None:
            return default
        try:
            current = self.config_dict
            for label in path:
                current = current[label]
            return current
        except KeyError:
            return default


class FishVariable:

    def __init__(self, variable_name, color_path=(), bg_path=(), style_path=()):
        self.variable_name = variable_name
        self.color_path = color_path
        self.bg_path = bg_path
        self.style_path = style_path

    def build_from_config(self, config_dict, flag="-g"):
        style = make_style(
            foreground=config_dict.get_by_path(self.color_path),
            background=config_dict.get_by_path(self.bg_path),
            font_style=config_dict.get_by_path(self.style_path)
        )
        return "set {} {} {}".format(
            flag,
            self.variable_name,
            style
        ) if style else None


variables = [
    FishVariable(
        "fish_color_normal",
        color_path=["globals", "foreground"],
        bg_path=["globals", "background"],
        style_path=["globals", "font_style"]
    ),
    FishVariable(
        "fish_color_command",
        color_path=["rules", "command", "foreground"],
        bg_path=["rules", "command", "background"],
        style_path=["rules", "command", "font_style"]
    ),
    FishVariable(
        "fish_color_selection",
        color_path=["globals", "selection_foreground"],
        bg_path=["globals", "selection"]
    )
]


def main(args):
    config_dict = StyleConfig(args.theme_path)

    for var in variables:
        str_var = var.build_from_config(config_dict, flag="-U" if args.universal else "-g")
        if str_var is not None:
            print(str_var)


if __name__ == "__main__":
    parser = argp.ArgumentParser(description="Script for translating sublime themes into fish "
                                             "variables")
    parser.add_argument("--universal", help="Use -U instead of -g", action="store_true")
    parser.add_argument("theme_path")
    args = parser.parse_args()
    main(args)
