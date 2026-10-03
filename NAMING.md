# Naming ports

Every Xenoglyphiq port is named the way **its own ecosystem** names things, not by one
org-wide pattern. A Go developer should find a Go port where they expect a Go library to
be, under a name that looks native to them.

The repo name is for browsing. The name people actually type (module, package, crate,
import) follows the language's own rules, listed below.

## Always

- **Keep the upstream name.** People search for the library they already know. `toml`
  stays `toml`; do not rename it.
- **Credit the original** in the repo description and README: `Go port of <upstream>
  (<link>)`.
- **Add GitHub topics**: `port`, the language (`go`, `swift`, `nim`, `zig`, `rust`), and
  the upstream name.
- **Check the registry first** (pkg.go.dev, Swift Package Index, Nimble, crates.io). If
  the name is taken, choose a distinctive name instead of bolting on an org prefix like
  `xg-`.

## Per language

| Language | Repo name | Name people type | Example (upstream `toml`) |
|---|---|---|---|
| Go | `go-<name>` | Module `github.com/Xenoglyphiq/go-<name>`, package `<name>` | repo `go-toml`, `import "github.com/Xenoglyphiq/go-toml"`, used as `toml.Parse(...)` |
| Swift | `swift-<name>` | Package and product in UpperCamelCase | repo `swift-toml`, `import TOML` |
| Nim | `nim-<name>` | Nimble package `<name>`, module `<name>.nim` | repo `nim-toml`, `nimble install toml`, `import toml` |
| Zig | `zig-<name>` | Package and module in snake_case | repo `zig-toml`, `.name = .toml` in `build.zig.zon`, `@import("toml")` |
| Rust | `<name>-rs` | Crate `<name>` (kebab-case on crates.io, snake_case in code) | repo `toml-rs`, `cargo add toml`, `use toml;` |

### Notes by language

**Go**
- Package names are short, lowercase, with no underscores or mixed caps.
- Never put `go` in the package name. The `go-` prefix lives only in the repo and
  module path.
- From v2 on, the module path ends in `/v2` (Go's major-version suffix rule).

**Swift**
- The `swift-` repo prefix follows Apple's own packages (`swift-nio`,
  `swift-argument-parser`).
- Use a `Kit` suffix on the module (`TOMLKit`) only when the plain name would clash with
  another common module.

**Nim**
- Nimble package names must be unique across the whole registry, and module names
  can't contain hyphens.
- If `<name>` is taken on Nimble, the package name and the import must change together.
  Keep the repo as `nim-<name>`.

**Zig**
- Recent Zig versions declare the package name in `build.zig.zon` as an
  identifier-style enum literal (`.name = .toml`), so use snake_case.
- `zig-<name>` is the most common repo pattern. A `<name>.zig` repo name is also
  common in the Zig world; pick one and stay consistent.

**Rust**
- The `-rs` repo suffix is a convention. The crate name should be the plain name when
  it's available on crates.io.

## Repo layout

Use **one repo per language per library**. Avoid a single repo with a folder per language,
because Swift Package Manager expects `Package.swift` at the repo root and Go
modules get awkward in subfolders.
