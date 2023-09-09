#!/usr/bin/env python3

import re
import sys
from pyparsing import *

# This script depends on the following packages:
#
# - pyparsing

# TODO: use a real parser generator like pyparsing

color_name = Word("[a-z0-9_]")
color_value = (

)
color_definition = (
    Keyword("@define-color")
    + color_name("color_name")
    + color_value("color_value")
)

COLOR_DEFINITION_REGEX = re.compile(r"@define-color ([a-z0-9_]*) (.*);")
COLOR_USE_REGEX = re.compile(r"@([a-z0-9_]*)")
CSS_MIX_REGEX = re.compile(r"(?<!color-)mix\(")

def replace_color_use(matchobj):
    return f"var(--{matchobj[1]})"

def replace_all(t):
    t = COLOR_USE_REGEX.sub(replace_color_use, t)
    t = CSS_MIX_REGEX.sub("color-mix(", t)
    return t

for filename in sys.argv[1:]:
    with open(filename) as f:
        for line in f:
            color_definition = COLOR_DEFINITION_REGEX.match(line)

            if color_definition:
                color_name = color_definition[1]
                color_value = replace_all(color_definition[1])
                print(f":root {{ --{color_name}: {color_value}; }}")
            else:
                print(replace_all(line))
