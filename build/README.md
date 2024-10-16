## Overview

Very cut back version of continuous integration build system for IBM Maximo Application Suite, based on Travis CI, utilizing automated semantic versioning of releases.

## Concepts

**Managed Branches** are ones where any commit will result in a new version being released.  These branches take one of two forms:
- `master` (current major version)
- `v1.x`, `v2.x`, `v3.x`, `v4.x` etc

Versioning is controlled by the GitHub commit messages:
- A commit comment of `[patch] Fix the thing` will result in a version change from `1.0.0` to `1.0.1`
- A commit comment of `[minor] Add the new feature` will result in a version change from `1.0.0` to `1.1.0`
- A commit comment of `[major] Rewrite the thing` will result in a version change from `1.0.0` to `2.0.0`
- A commit comment without any of the above will result in build with no new release being published
- A commit comment of `[skip ci] Something not worth a new build` will result in Travis not even running

When a build contains multiple commits the most significant commit "wins".

Commits in **Unmanaged Branches** will still result in a new build, but any artifacts published will overwrite the previous release. Effectively there is only a latest version for these branches.

