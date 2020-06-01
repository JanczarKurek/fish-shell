import json as js
import argparse as argp
import re


# todo - convertion between config color names and set_color
def fishify_color(color_string):

    maybe_variable_reference = re.fullmatch(r"var\((.*)\)", color_string)
    if maybe_variable_reference:
        return "${}".format(maybe_variable_reference.group(1))

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
        # Split rules with multiple scopes
        if "rules" in self.config_dict:
            self.config_dict["rules"] = {
                scope: rule for rule in self.config_dict["rules"] for scope in rule["scope"].replace(" ", "").split(",")
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

    def __init__(self, variable_name, color_path=(), bg_path=(), style_path=(), common_path=None):
        self.variable_name = variable_name
        if not common_path:
            self.color_path = color_path
            self.bg_path = bg_path
            self.style_path = style_path
        else:
            self.color_path = common_path + ["foreground"]
            self.bg_path = common_path + ["background"]
            self.style_path = common_path + ["font_style"]

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


def parse_local_variables(style_config):
    return [
        'set -l {} "{}"'.format(var_name, var_value)
        for var_name, var_value in style_config.get_by_path(["variables"]).items()
    ]


variables = [
    FishVariable(
        "fish_color_normal",
        common_path=["globals"]
    ),
    FishVariable(
        "fish_color_command",
        common_path=["rules", "command"]
    ),
    FishVariable(
        "fish_color_selection",
        color_path=["globals", "selection_foreground"],
        bg_path=["globals", "selection"]
    ),
    FishVariable(
        "fish_color_comment",
        common_path=["rules", "comment"]
    ),
    FishVariable(
        "fish_color_operator",
        common_path=["rules", "keyword.operator"]
    ),
    FishVariable(
        "fish_color_quote",
        common_path=["rules", "string"]
    ),
    FishVariable(
        "fish_color_escape",
        common_path=["rules", "constant.character"]
    ),
    FishVariable(
        "fish_color_end",
        common_path=["rules", "punctuation.separator"]
    ),
    FishVariable(
        "fish_color_error",
        common_path=["rules", "message.error"]
    )
]


def main(args):
    config_dict = StyleConfig(args.theme_path)

    for local_variable_definition in parse_local_variables(config_dict):
        print(local_variable_definition)

    print()

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
