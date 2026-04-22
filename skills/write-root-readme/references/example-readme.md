<div align="center" markdown>

<!-- project image includes logo, description, stars badge, forks badge, issues badge, pull requests badge -->
<!-- project image without logo -->
![Grapes](https://socialify.git.ci/liblaf/grapes/image?description=1&forks=1&issues=1&language=1&name=1&owner=1&pattern=Transparent&pulls=1&stargazers=1&theme=Auto)
<!-- project image with fluent emoji -->
![Grapes](https://socialify.git.ci/liblaf/grapes/image?description=1&forks=1&issues=1&language=1&logo=https%3A%2F%2Fraw.githubusercontent.com%2Fmicrosoft%2Ffluentui-emoji%2Frefs%2Fheads%2Fmain%2Fassets%2FGrapes%2F3D%2Fgrapes_3d.png&name=1&owner=1&pattern=Transparent&pulls=1&stargazers=1&theme=Auto)
<!-- project image with custom logo -->
![Copier Python](https://socialify.git.ci/liblaf/copier-python/image?description=1&forks=1&issues=1&language=1&logo=https%3A%2F%2Fraw.githubusercontent.com%2Fcopier-org%2Fcopier%2Frefs%2Fheads%2Fmaster%2Fimg%2Flogo.svg&name=1&owner=1&pattern=Transparent&pulls=1&stargazers=1&theme=Auto)

**[Explore the docs »](https://liblaf.github.io/grapes/)**

<!-- large badge -->
[![Built with Cloudflare](https://workers.cloudflare.com/built-with-cloudflare.svg)](https://cloudflare.com)
[![Deploy to Cloudflare](https://deploy.workers.cloudflare.com/button)](https://deploy.workers.cloudflare.com/?url=https://github.com/liblaf/grapes)
[![Made with Copier](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/copier-org/copier/master/img/badge/badge-black.json)](https://github.com/copier-org/copier)

<!-- normal badges -->
[![Bun](https://img.shields.io/badge/Bun-000000?logo=bun)](https://bun.sh)
[![Checked with Biome](https://img.shields.io/badge/Checked_with-Biome-60a5fa?style=flat&logo=biome)](https://biomejs.dev)
[![Codecov](https://codecov.io/gh/liblaf/grapes/graph/badge.svg)](https://codecov.io/gh/liblaf/grapes)
[![CodSpeed Badge](https://img.shields.io/endpoint?url=https://codspeed.io/badge.json)](https://codspeed.io/liblaf/grapes)
[![MegaLinter](https://github.com/liblaf/grapes/actions/workflows/mega-linter.yaml/badge.svg)](https://github.com/liblaf/grapes/actions/workflows/mega-linter.yaml)
[![NPM Downloads](https://img.shields.io/npm/dy/typescript?logo=npm)](https://www.npmjs.com/package/typescript)
[![NPM Version](https://img.shields.io/npm/v/typescript?logo=npm)](https://www.npmjs.com/package/typescript)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/liblaf/grapes/main.svg)](https://results.pre-commit.ci/latest/github/liblaf/grapes/main)
[![prek](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/j178/prek/master/docs/assets/badge-v0.json)](https://github.com/j178/prek)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/liblaf-grapes?logo=PyPI)](https://pypi.org/project/liblaf-grapes)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/liblaf-grapes?logo=Python)](https://pypi.org/project/liblaf-grapes)
[![PyPI - Types](https://img.shields.io/pypi/types/liblaf-grapes?logo=PyPI)](https://pypi.org/project/liblaf-grapes)
[![PyPI - Version](https://img.shields.io/pypi/v/liblaf-grapes?logo=PyPI)](https://pypi.org/project/liblaf-grapes)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Test](https://github.com/liblaf/grapes/actions/workflows/test.yaml/badge.svg)](https://github.com/liblaf/grapes/actions/workflows/test.yaml)
[![ty](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ty/main/assets/badge/v0.json)](https://github.com/astral-sh/ty)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

[Changelog](https://github.com/liblaf/grapes/blob/main/CHANGELOG.md) · [Report Bug](https://github.com/liblaf/grapes/issues) · [Request Feature](https://github.com/liblaf/grapes/issues)

![Rule](https://cdn.jsdelivr.net/gh/andreasbm/readme/assets/lines/rainbow.png)

</div>

## ✨ Features

- 💨 **Quick Deployment**: Using the Vercel platform, you can deploy with just one click and complete the process within 1 minute, without any complex configuration;
- 💎 **Exquisite UI Design**: With a carefully designed interface, it offers an elegant appearance and smooth interaction. It supports light and dark themes and is mobile-friendly. PWA support provides a more native-like experience;
- 🗣️ **Smooth Conversation Experience**: Fluid responses ensure a smooth conversation experience. It fully supports Markdown rendering, including code highlighting, LaTex formulas, Mermaid flowcharts, and more;

## 📦 Installation

> [!IMPORTANT]
> This package is [ESM only](https://gist.github.com/sindresorhus/a39789f98801d908bbc7ff3ecc99d99c).

To install `@lobehub/ui`, run the following command:

[![speedup with bun](https://img.shields.io/badge/-speedup%20with%20bun-black?logo=bun&style=for-the-badge)](https://bun.sh)

```bash
bun add @lobehub/ui
```

### Compile with Next.js

> [!NOTE]
> By work correct with Next.js SSR, add `transpilePackages: ['@lobehub/ui']` to `next.config.js`. For example:

```js
const nextConfig = {
  transpilePackages: ['@lobehub/ui'],
};
```

## ⌨️ Local Development

You can use Github Codespaces for online development:

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lobehub/lobe-chat)

Or clone it for local development:

[![speedup with bun](https://img.shields.io/badge/-speedup%20with%20bun-black?logo=bun&style=for-the-badge)](https://bun.sh)

```bash
git clone https://github.com/lobehub/lobe-chat.git
cd lobe-chat
bun install
bun dev
```

## 🤝 Contributing

Contributions of all types are more than welcome, if you are interested in contributing code, feel free to check out our GitHub [Issues](https://github.com/lobehub/lobe-chat/issues) to get stuck in to show us what you're made of.

[![PR WELCOME](https://img.shields.io/badge/%F0%9F%A4%AF%20PR%20WELCOME-%E2%86%92-ffcb47?labelColor=black&style=for-the-badge)](https://github.com/lobehub/lobe-chat/pulls)

[![Contributors](https://contrib.nn.ci/api?repo=lobehub/lobe-chat)](https://github.com/lobehub/lobe-chat/graphs/contributors)

## 🔗 Links

### More Projects

- [**🤖 Lobe Chat**](https://github.com/lobehub/lobe-chat) - An open-source, extensible (Function Calling), high-performance chatbot framework. It supports one-click free deployment of your private ChatGPT/LLM web application.
- [**🤯 Lobe theme**](https://github.com/lobehub/sd-webui-lobe-theme) - The modern theme for stable diffusion webui, exquisite interface design, highly customizable UI, and efficiency boosting features.

### Credits

- **remark** - <https://github.com/remarkjs/remark>
- **shikiji** - <https://github.com/antfu/shikiji>

---

#### 📝 License

Copyright © 2026 [liblaf](https://github.com/liblaf). <br />
This project is [MIT](https://github.com/liblaf/grapes/blob/main/LICENSE) licensed.
