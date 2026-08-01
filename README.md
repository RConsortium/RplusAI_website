# R+AI 2026 Website

Quarto site for the R+AI 2026 event.

The previous conference site is archived at [RConsortium/RplusAI_2025](https://github.com/RConsortium/RplusAI_2025) (`https://rconsortium.github.io/RplusAI_2025/`).

## Local preview

1) Install Quarto: https://quarto.org/docs/get-started/  
2) In this folder:
```bash
quarto preview
```

## Publish with GitHub Pages

1) Repo: `RConsortium/RplusAI_website`
2) In the repo: Settings → Actions → General → Workflow permissions → **Read and write**.
3) Settings → Pages → Source: **Deploy from a branch**, Branch: `gh-pages`, Folder: `/`.
4) Push to `main`. The workflow builds and pushes the rendered site to `gh-pages`.

Site URL: `https://rconsortium.github.io/RplusAI_website/`.
