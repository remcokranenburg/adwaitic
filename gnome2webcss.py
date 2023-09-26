#!/usr/bin/env python3

import re
import sys
from pyparsing import *

color_name = Word(alphanums + "-_")

color_name.run_tests("""
    hi
    hello_world
    foo-bar
""")

color_value_variable = original_text_for(Literal("var(--") + color_name + ")")

color_value_variable.run_tests("""
    var(--hello-world)
    var(--foo_bar)
    var(--hi2)
""")

color_value_variable_gnome = Literal("@") + color_name("name")

@color_value_variable_gnome.set_parse_action
def convert_gnome_variable(results: ParseResults):
    return "var(--" + results["name"] + ")"

color_value_hex = Combine("#" + Word(srange("[0-9a-fA-F]")))

color_channel = pyparsing_common.number ^ pyparsing_common.number + "%"

color_value_rgb = original_text_for(
    (Literal("rgb(") | Literal("rgba("))
    + color_channel + ","
    + color_channel + ","
    + color_channel
    + Opt("," + color_channel)
    + ")"
)


color_value_rgb.run_tests("""
    rgb(1, 2, 3)
    rgba( 123 ,234, 345, 0.1)
    rgb(100%, 1.5, -3, .1)
""")

color_value_keyword = Word(alphanums + "-")

color_value = (
    color_value_variable
    | color_value_variable_gnome
    | color_value_hex
    | color_value_rgb
    | color_value_keyword
)

color_definition = (
    Keyword("@define-color")
    + color_name("color_name")
    + color_value("color_value")
    + ";"
)

color_definition.run_tests("""
    @define-color foo var(--bar);
    @define-color hello_world @foo;
    @define-color hi2 red;
""")

autoname_elements()

for filename in sys.argv[1:]:
    with open(filename) as f:
        for line in f:
            try:
                cd = color_definition.parse_string(line)

                # print("DEBUG:", repr(cd))

                color_name = cd["color_name"]
                color_value = cd["color_value"]
                # print(f":root {{ --{color_name}: {color_value[0]}; }}")
            except:
                pass
                print(line)
