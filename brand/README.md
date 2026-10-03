# brand/

This folder holds all of Xenoglyphiq's brand assets. Every file here is generated. To
change anything, edit `tokens.json` and rebuild. The rules for using the assets are in
[`../BRAND.md`](../BRAND.md).

## Rebuild

```sh
cd brand
python3 build.py
```

It needs Python 3 with `fontTools` and `Pillow`, plus the system `librsvg-2` and `cairo`
libraries. On macOS, install those with `brew install librsvg`. If the libraries aren't
found there, point `DYLD_FALLBACK_LIBRARY_PATH` at `/opt/homebrew/lib`.

- **SVGs** are written straight from the geometry and color tokens.
- **Wordmark text** is laid out from the Chakra Petch font files, including the font's
  own kerning.
- **Every PNG** is rendered from the *outlined* SVG of the same asset by
  `rsvg_render.py`. Rasters and vectors therefore always match, and no installed fonts
  are needed.

## What's here

```
tokens.json                                   single source of truth: geometry, palette, type, lockups, banner layouts
build.py                                      generator
rsvg_render.py                                SVG to PNG via librsvg (ctypes)
fonts/                                        Chakra Petch Regular / Medium / SemiBold + OFL license

mark/
  xenoglyphiq-mark.svg                        for light backgrounds (wine in front)
  xenoglyphiq-mark-dark.svg                   for dark backgrounds (amber in front)
  xenoglyphiq-mark-mono-ink.svg               one color, stacked
  xenoglyphiq-mark-mono-white.svg             one color, knockout
  xenoglyphiq-mark-knockout-wine.svg          white mark reversed out of a wine tile
  xenoglyphiq-mark-knockout-night.svg         color mark on the night tile
  png/                                        256 / 512 / 1024
  chain/                                      4, 5, 7-hex display chains, large surfaces only

lockups/
  xenoglyphiq-lockup-{primary,compact,stacked}-{light,dark}.svg            live text
  xenoglyphiq-lockup-{primary,compact,stacked}-{light,dark}-outlined.svg   text as paths
  png/                                        @2x

banners/
  github-banner-{light,dark}                  1500x500, profile README (<picture>-switched)
  twitter-header-{dark,light}                 1500x500, lockup clear of the avatar corner
  social-preview-{dark,light}                 1280x640, repo social preview / Open Graph
  *-live.svg                                  same art with live text
  png/

icons/
  avatar-{dark,light}-500.png                 org / Twitter avatar (dark is primary)
  icon-{1024,512,192}.png, apple-touch-icon.png
  favicon.ico (16/32/48), favicon-{16,32,48,64}.png
  favicon-small-cut.svg, icon-{dark,light}.svg

web/
  favicon.svg                                 adapts to light/dark
  xenoglyphiq-mark-adaptive.svg               adapts to light/dark
  xenoglyphiq-lockup-primary-adaptive.svg     adapts to light/dark, outlined text
  xenoglyphiq-mark-currentcolor.svg           takes the surrounding text color
  brand.css                                   CSS variables + @font-face
  head-snippet.html, site.webmanifest
```

## Setting up the org on GitHub

1. **Avatar:** upload `icons/avatar-dark-500.png` under Organization settings → Profile.
2. **Social preview:** in each repo, go to Settings → General → Social preview and upload
   `banners/png/social-preview-dark.png`.
3. **Twitter / X:** use `banners/png/twitter-header-dark.png` as the header and
   `icons/avatar-dark-500.png` as the profile picture.

The profile README loads its banners from
`raw.githubusercontent.com/Xenoglyphiq/.github/main/...`. If the repo's default branch
isn't `main`, update those two URLs.
