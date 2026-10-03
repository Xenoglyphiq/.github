# Contributing to Xenoglyphiq

Thanks for helping carry a library into a new language. Every port follows the same
principle: **translation, not transliteration**. Match what the original does, but write
it the way the new language would.

## Before you start

1. **Check the license.** Only port libraries whose license allows it. Keep the
   upstream license file and copyright notice, and add your own as required (for
   example, MIT ports stay MIT).
2. **Check for an existing port.** Search this org and the language's registry. If a
   good port already exists, consider contributing there instead.
3. **Open an issue in the `.github` repo** with the upstream library, the target
   language, and the version you're porting from.

## Naming

Follow [NAMING.md](NAMING.md). In short:

- The repo is named by its ecosystem's convention (`go-<name>`, `swift-<name>`,
  `nim-<name>`, `zig-<name>`, `<name>-rs`).
- Keep the upstream library's name.
- Use the language's normal casing for the package or module.

## What a port includes

- **Behavior that matches upstream** for the version you name, backed by tests. Where
  possible, port the upstream tests too.
- **An idiomatic API.** Use the target language's error handling, naming, iteration,
  and memory patterns. Write a note in the README wherever the API intentionally
  differs from upstream.
- **A README** that has:
  - a first line of `<Language> port of [<upstream>](<link>)`;
  - the upstream version it tracks;
  - install and usage instructions;
  - a short "Differences from upstream" section.
- **CI** that runs the tests on the language's current stable toolchain.
- **GitHub topics:** `port`, the language, and the upstream name.

## Keeping up with upstream

Track the upstream version in the README. When upstream ships a release, open an issue
titled `Sync with <upstream> vX.Y.Z` and link to the upstream changelog.

## Style

Use the language's standard formatter and linter (`gofmt`/`go vet`, `swift-format`,
`nimpretty`, `zig fmt`, `rustfmt`/`clippy`). Formatting isn't up for discussion; the
idioms are.

## Branding

Logos, colors, and banners are in [`brand/`](brand/), with rules in
[BRAND.md](BRAND.md). Please don't redraw the mark. Use the files there.
