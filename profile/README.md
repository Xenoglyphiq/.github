<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/Xenoglyphiq/.github/main/brand/banners/png/github-banner-dark.png">
  <img alt="Xenoglyphiq: Lost nothing in translation" src="https://raw.githubusercontent.com/Xenoglyphiq/.github/main/brand/banners/png/github-banner-light.png">
</picture>

# Xenoglyphiq

**Lost nothing in translation.**

Useful libraries, each ported to the languages it's needed in: **Swift**, **Go**, **Python**,
**Kotlin**, **Rust**, **Nim**, **Zig** and **Julia**. The first ports are in Swift, Nim, Zig
and Julia, with Go and Python next.

The goal is to take on a whole project in one language, or try the same one in a different
language just for fun.

Each library is written down once, as a spec with shared test cases, and every port passes
the same cases. Each port aims to read like it was written natively in its language, not
translated word for word, and credits the format or project it implements.

## Ports

| Library | Swift | Kotlin | Rust | Nim | Zig | Julia |
|---|---| --- | --- |---|---|---|
| [Polyline](https://github.com/Xenoglyphiq/polyline-spec): Google's encoded polyline format | | | | [`polyline-nim`](https://github.com/Xenoglyphiq/polyline-nim) v0.1.0 | [`polyline-zig`](https://github.com/Xenoglyphiq/polyline-zig) v0.1.0 | [`EncodedPolyline.jl`](https://github.com/Xenoglyphiq/EncodedPolyline.jl) (registering) |
| [PMTiles](https://github.com/Xenoglyphiq/pmtiles-spec): read PMTiles v3 tile archives | [`pmtiles-swift`](https://github.com/Xenoglyphiq/pmtiles-swift) 0.2.0 | | | [`pmtiles-nim`](https://github.com/Xenoglyphiq/pmtiles-nim) v0.2.0 | [`pmtiles-zig`](https://github.com/Xenoglyphiq/pmtiles-zig) v0.2.0 | |
| [robots.txt](https://github.com/Xenoglyphiq/robotstxt-spec): RFC 9309 parsing and matching | [`robotstxt-swift`](https://github.com/Xenoglyphiq/robotstxt-swift) 0.1.0 | | | | [`robotstxt-zig`](https://github.com/Xenoglyphiq/robotstxt-zig) v0.1.0 | [`RobotsTxt.jl`](https://github.com/Xenoglyphiq/RobotsTxt.jl) (registering) |

Install instructions and examples for every port are at **[docs.xenoglyphiq.dev](https://docs.xenoglyphiq.dev)**.

## Finding a port

Each library has a spec repo, `<lib>-spec`, and one repo per language, `<lib>-<language>`
(Julia: `<Lib>.jl`). For example, PMTiles is `pmtiles-spec`, `pmtiles-swift`, `pmtiles-nim`
and `pmtiles-zig`. Package names follow each language's own conventions; see
[NAMING.md](https://github.com/Xenoglyphiq/.github/blob/main/NAMING.md).

## Contributing

Want to fix something or add a port? Start with
[CONTRIBUTING.md](https://github.com/Xenoglyphiq/.github/blob/main/CONTRIBUTING.md).
