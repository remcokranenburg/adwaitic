# Adwaitic

Adwaita-like widgets for the web. For when you want something to have the Gnome aesthetic but you
want or need to work with web tech.

## License

Adwaitic is licensed under the LGPL-2.1+.

## Building

Clone and build libadwaita:

```
git clone https://gitlab.gnome.org/GNOME/libadwaita.git
meson libadwaita libadwaita/_build
ninja -C libadwaita/_build
```

Convert the stylesheet (depends on pyparsing):

```
./gnome2webcss.py libadwaita/_build/src/stylesheet/base.css libadwaita/_build/src/stylesheet/defaults-light.css > style.css
```

Run a web server to view the example:

```
python3 -m http.server
```
