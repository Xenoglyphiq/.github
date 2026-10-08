# Naming

Every Xenoglyphiq library has **one spec repo** and **one repo per language**, with the
package at the repo root. Repo names follow one pattern across languages, so a library's
ports sit next to each other in the org. The name people actually type (module, package,
crate, import) follows the language's own rules.

## Repos

| Repo | Name | Example (library `pmtiles`) |
|---|---|---|
| Spec | `<lib>-spec` | `pmtiles-spec` |
| Port | `<lib>-<language>` | `pmtiles-swift`, `pmtiles-zig` |
| Julia port | `<Lib>.jl` (Julia's General registry expects the suffix) | `RobotsTxt.jl` |

`<lib>` is the library's short id, lowercase with no separators (`pmtiles`, `robotstxt`).
`<Lib>` is its display name in Julia's style (`RobotsTxt`).

## Packages

| Language | Repo | Package | Import |
|---|---|---|---|
| Swift | `<lib>-swift` | products `<Lib>` (core) and `<Lib>IO` | `import <Lib>` |
| Go | `<lib>-go` | module `github.com/xenoglyphiq/<lib>-go` | `<lib>`, `<lib>io` |
| Python | `<lib>-python` | PyPI `xenoglyphiq-<lib>` | `import xenoglyphiq_<lib>` |
| Kotlin | `<lib>-kotlin` | Maven `com.xenoglyphiq:<lib>-core`, `:<lib>-io` | `com.xenoglyphiq.<lib>` |
| Rust | `<lib>-rust` | crate `xenoglyphiq-<lib>` (features `io`, `async`) | `use xenoglyphiq_<lib>` |
| Nim | `<lib>-nim` | Nimble `<lib>` | `import <lib>`, `<lib>/io` |
| Zig | `<lib>-zig` | module `<lib>` in `build.zig.zon` | `@import("<lib>")` |
| Julia | `<Lib>.jl` | `<Lib>` | `using <Lib>` |

### Rules by language

- **Swift:** no org prefix in the package name; the repo URL carries the org.
- **Go:** module paths are lowercase (`github.com/xenoglyphiq/...`). Go treats them
  case-sensitively, so never mix cases.
- **Python:** the PyPI name carries a `xenoglyphiq-` prefix, which leaves generic names
  like `pmtiles` free for the format's own projects.
- **Kotlin:** the Maven group ID is `com.xenoglyphiq`.
- **Rust:** the crate name carries a `xenoglyphiq-` prefix, for the same reason as Python.
- **Nim:** no org prefix in the Nimble name; the repo URL carries the org.
- **Zig:** no org prefix in the module name; the repo URL carries the org.
- **Julia:** no org prefix in the package name; the repo URL carries the org, and the repo
  name ends in `.jl`.

### Rules for every language

- **When a name is taken** in a registry, pick the closest name that passes that
  registry's checks, never a near-copy like `Name2`, and say so in the spec repo's port
  table. Example: `Polyline` is taken in Julia's General registry, so the Julia port is
  `EncodedPolyline.jl`.
- **Check the registry first** (Swift Package Index, pkg.go.dev, PyPI, Maven Central,
  crates.io, Nimble, Julia's General).
- **Add GitHub topics:** the language, the library's subject (for example `pmtiles`,
  `robots-txt`) and, for Zig, `zig-package` so zigistry lists it.

## Why one repo per language

Swift Package Manager needs `Package.swift` at the repo root, and Zig packages are
fetched from the repo root. Each registry also has its own tags and release flow. One rule
for every language keeps the tooling simple.
