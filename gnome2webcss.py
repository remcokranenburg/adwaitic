#!/usr/bin/env python3

import re
import sys
from pyparsing import *

comment = original_text_for(Literal("/*") + ... + Literal("*/"))

color_name = Word(alphanums + "-_")
color_value_variable = original_text_for(Literal("var(--") + color_name + ")")
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

color_value_alpha = Forward()

color_value_mix = Forward()

color_value_generic_function = Forward()

color_value_keyword = Word(alphanums + "-")

color_value = (
    color_value_variable
    | color_value_variable_gnome
    | color_value_hex
    | color_value_rgb
    | color_value_alpha
    | color_value_mix
    | color_value_generic_function
    | color_value_keyword
)

color_value_alpha <<= Literal("alpha(") + color_value("color") + "," + color_channel("alpha") + ")"

@color_value_alpha.set_parse_action
def convert_alpha(results: ParseResults):
    color = results["color"][0]
    alpha = float(results["alpha"][0]) * 100
    return f"color-mix(in srgb, {color} {alpha}%, transparent)"

color_value_mix <<= (
    Literal("mix(")
    + color_value("c1") + ","
    + color_value("c2") + ","
    + color_channel("alpha") + ")"
)

@color_value_mix.set_parse_action
def convert_mix(results: ParseResults):
    c1 = results["c1"][0]
    c2 = results["c2"][0]
    alpha = float(results["alpha"][0]) * 100
    return f"color-mix(in srgb, {c1} {alpha}%, {c2})"

color_value_generic_function = (
    Combine(Word(alphanums + "-_") + "(")
    + OneOrMore(color_value | Literal("/") | Literal(",") | Literal("%"))
    + ")"
)

color_definition = (
    Keyword("@define-color")
    + color_name("color_name")
    + color_value("color_value")
    + ";"
)

@color_definition.set_parse_action
def convert_color_definition(results: ParseResults):
    color_name = results["color_name"]
    color_value = results["color_value"]
    return f":root {{ --{color_name}: {color_value[0]}; }}"

selector = SkipTo("{") + "{"

@selector.set_parse_action
def convert_selector(results: ParseResults):
    return results[0]

declaration_name = Word(alphanums + "-_")

declaration_value = (
    OneOrMore(color_value | Literal("/") | Literal(",") | Literal("|"))
    + FollowedBy(ZeroOrMore(Literal(";") | Literal("}")))
)

@declaration_value.set_parse_action
def convert_declaration_value(results: ParseResults):
    return " ".join(results)

declaration = declaration_name("name") + ":" + declaration_value("value")

@declaration.set_parse_action
def convert_declaration(results: ParseResults):
    return results["name"] + ": " + results["value"]

declaration_list = delimited_list(declaration, delim=";", allow_trailing_delim=True)

@declaration_list.set_parse_action
def convert_declarations(results: ParseResults):
    return "".join(f"    {d};\n" for d in results)

css_rule = (
    selector("selector")
    + Opt(declaration_list).set_results_name("declarations")
    + Suppress("}")
)

@css_rule.set_parse_action
def convert_rule(results: ParseResults):
    selector = results["selector"]
    return f"{selector} {{\n" + results["declarations"][0] + "}"

keyframes = (
    Literal("@keyframes")
    + Word(alphanums + "-_")
    + "{"
    + OneOrMore(one_of(["to", "from"]) + "{" + declaration_list + "}")
    + "}"
)

rule = (
    color_definition
    | css_rule
    | keyframes
    | comment
)

rules = ZeroOrMore(rule)

@rules.set_parse_action
def convert_rules(results: ParseResults):
    return "\n".join(results)

def test():
    color_name.run_tests("""
        hi
        hello_world
        foo-bar
    """)

    color_value_rgb.run_tests("""
        rgb(1, 2, 3)
        rgba( 123 ,234, 345, 0.1)
        rgb(100%, 1.5, -3, .1)
    """)

    color_value_variable.run_tests("""
        var(--hello-world)
        var(--foo_bar)
        var(--hi2)
    """)

    color_value_alpha.run_tests("""
        alpha(red, 0.15)
        alpha(#123, 0.59)
        alpha(@something, 0.3)
    """)

    color_definition.run_tests("""
        @define-color foo var(--bar);
        @define-color hello_world @foo;
        @define-color hi2 red;
    """)

    selector.run_tests("""
        .foo {
        foo {
        a + b {
        a~b{
    """)

    declaration_value.run_tests("""
        solid line 12px @thiscolor
        12 boo / @blah 10px
        alpha(@view_fg_color,0.1)
    """)

    declaration.run_tests("""
        a:b
        background-color: alpha(@view_fg_color,0.1)
        -gtk-icon-shadow: 0 -1px rgba(0, 0, 0, 0.05), 1px 0 rgba(0, 0, 0, 0.1)
    """)

    declaration_list.run_tests("""
        a:b; c:24px;
        a:b
        c:24px; d: 12 boo / @blah 10px
        background-color: alpha(@view_fg_color,0.1); color: transparent;
    """)

    rule.run_tests("""
        .foo { a:b }
        a + b { c:24px; d:bar }
        a + b { c:24px; d: 12 boo / @blah 10px }
        @define-color blue_1 #123324;
        selection  { background-color: alpha(@view_fg_color,0.1); color: transparent; }
    """)

if "--test" in sys.argv:
    test()
    exit(0)

for filename in sys.argv[1:]:
    with open(filename) as f:
        print(rules.parse_file(f)[0])
