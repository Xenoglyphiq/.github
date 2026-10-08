# Contributing to Xenoglyphiq

Thanks for helping. Every Xenoglyphiq library is built the same way: **one spec, many
ports**. The behavior is written down once, in the library's spec repo, together with
conformance cases that every port must pass. Each port then implements it the way its own
language would. The motto is translation, not transliteration.

## How a library is organized

- **The spec repo** (`<lib>-spec`) holds:
  - `spec/SPEC.md`, the behavior, readable;
  - `spec/capability.yaml`, the same contract in machine-readable form (types, operations,
    errors, limits);
  - `conformance/`, test cases generated from a pinned reference implementation and
    checked against the spec;
  - `DECISIONS.md`, why the spec is the way it is, including where it differs from other
    implementations;
  - `bench/`, a shared benchmark input and a reference to measure against.
- **Each port** (`<lib>-<language>`, see [NAMING.md](NAMING.md)) vendors a tagged release of
  the spec into `.spec/` and runs every case in CI.
- **`.kit/`**, in every repo, holds the shared conventions (data types, error model,
  layers), the JSON schemas and the validator. It's updated from upstream; don't edit it
  in place.

## Making a change

| You want to… | Do this |
|---|---|
| Fix a bug in one port | Open the PR in that port's repo. If the bug shows a missing test, add a conformance case to the spec repo too. |
| Change behavior | Open an issue in the spec repo first. A behavior change needs a `DECISIONS.md` entry, regenerated cases, a new spec version and tag; then each port updates. |
| Port a library to a new language | Open an issue in the spec repo. Check the language's registry first: if a good library already exists, contributing to it may be better. |
| Report ports that disagree | Open an issue in the spec repo with the input. It becomes a conformance case. |

## What a port includes

- **All conformance cases passing**, for the spec version in `.spec/SPEC_VERSION`.
- **An idiomatic API**: the language's own naming, error handling, iteration and memory
  patterns. Error kinds and codes match the spec; tests check kind and code, never message
  text.
- **Layers** as separate modules: `core` (pure, no I/O), then `io`. Only `io` may touch
  files or the network.
- **Fuzzing** of every decoder that reads untrusted input, and **limits** checked before
  allocating.
- **A benchmark** using the spec's method, reported in the README against the spec's
  reference.
- **The spec's three canonical examples**, run in CI.
- **A README** with install, a quick start, the examples, an API table mapping each
  function to its spec operation, limits and errors, and performance.
- **CI** on the language's current stable toolchain. Public repos use GitHub-hosted
  runners only.

## Releases

A version tag (`vA.B.C`; Swift uses `A.B.C`) creates the GitHub release automatically.
Julia packages are registered in General, and TagBot tags them. A port's release is listed
in its spec repo's port table, on [docs.xenoglyphiq.dev](https://docs.xenoglyphiq.dev), and
in the [org profile](profile/README.md).

## Style

Use the language's standard formatter and linter. Formatting isn't up for discussion;
idioms are.

| Language | Formatter and linter |
|---|---|
| Swift | `swift-format` |
| Go | `gofmt`, `go vet` |
| Python | `ruff` |
| Kotlin | `ktlint` |
| Rust | `rustfmt`, `clippy` |
| Nim | `nimpretty` |
| Zig | `zig fmt` |
| Julia | `JuliaFormatter` |

## License

Every spec and port is **MIT OR Apache-2.0**, with both license files. By contributing, you
agree your contribution is licensed the same way. If a spec includes test cases translated
from another project, its `NOTICE` says so, and ports carry that `NOTICE` in `.spec/`.

## Branding

Logos, colors and banners are in [`brand/`](brand/), with rules in [BRAND.md](BRAND.md).
Please don't redraw the mark. Use the files there.
