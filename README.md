# R+AI 2025 Website

Quarto site for the R+AI 2025 event.

## Local preview

1) Install Quarto: https://quarto.org/docs/get-started/  
2) In this folder:
```bash
quarto preview
```

## Publish with GitHub Pages

1) Create a repo named `RplusAI_website` under the `RConsortium` org.
2) Push this folder to the `main` branch.
3) In the repo: Settings → Actions → General → Workflow permissions → **Read and write**.
4) Settings → Pages → Source: **Deploy from a branch**, Branch: `gh-pages`, Folder: `/`.
5) Push to `main`. The workflow builds and pushes the rendered site to `gh-pages`.

Site URL will be: `https://rconsortium.github.io/RplusAI_website/`.