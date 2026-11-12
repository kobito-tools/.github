# kobito-tools

**English** | [日本語](https://github.com/kobito-tools/.github/blob/main/profile/README.ja.md)

Small tools that make everyday work a little easier.

kobito-tools is a series of small desktop apps that lend you a hand, like the little helpers (*kobito*) of folk tales.

## Ideas

- **Every app works on its own.** Install only the apps you want, and open them like any other app.
- **Line them up in [kobito-workspace](https://github.com/kobito-tools/kobito-workspace) to use them in one window.** The apps you install appear side by side in the workspace, where you can switch between them and search across them.
- **Every app is a repository of the same shape.** It keeps its manifest `kobito-app.json` at the root, its icon in `kobito/`, and its introduction image at `assets/social-preview.png` (`social-preview.ja.png` for Japanese), all under fixed names. Public repositories with a `kobito-app.json` appear in the list below automatically. The rules are in kobito-workspace's [APP_PACKAGE.md](https://github.com/kobito-tools/kobito-workspace/blob/main/kobito_workspace/kit/docs/APP_PACKAGE.md).

## Install

To install apps from the series together, run this in Terminal. You can pick the apps you want from a list.

```bash
zsh -c "$(curl -fsSL https://raw.githubusercontent.com/kobito-tools/kobito-workspace/main/install.sh)"
```

To install a single app, get its source (`git clone`, or "Code → Download ZIP") and run `./setup.sh` in its folder. See each app's README for details. No installers (such as dmg files) are provided.

## Apps

<!-- TOOLS:START -->
### <img src="https://raw.githubusercontent.com/kobito-tools/CrokClip/main/kobito/icon-1024.png" width="32" height="32" alt=""> [CorkClip](https://github.com/kobito-tools/CrokClip)

Pin what you copy to a corkboard

<a href="https://github.com/kobito-tools/CrokClip"><img src="https://raw.githubusercontent.com/kobito-tools/CrokClip/main/assets/social-preview.png" width="640" alt="CorkClip"></a>

**Type:** Native &nbsp;·&nbsp; **Platforms:** macOS &nbsp;·&nbsp; **Latest:** [v0.2.0](https://github.com/kobito-tools/CrokClip/tree/v0.2.0)

### <img src="https://raw.githubusercontent.com/kobito-tools/OpenSesame/main/kobito/icon-1024.png" width="32" height="32" alt=""> [OpenSesame!](https://github.com/kobito-tools/OpenSesame)

Hold a key and the door to your apps and files opens

<a href="https://github.com/kobito-tools/OpenSesame"><img src="https://repository-images.githubusercontent.com/1382855232/03a62c13-b261-42ac-898c-e7c8617d9ca8" width="640" alt="OpenSesame!"></a>

**Type:** Native &nbsp;·&nbsp; **Platforms:** macOS · Windows &nbsp;·&nbsp; **Latest:** [v1.0.0](https://github.com/kobito-tools/OpenSesame/tree/v1.0.0)

### <img src="https://raw.githubusercontent.com/kobito-tools/PopNote/main/kobito/icon-1024.png" width="32" height="32" alt=""> [PopNote!](https://github.com/kobito-tools/PopNote)

Pop it open and start writing notes and a diary

<a href="https://github.com/kobito-tools/PopNote"><img src="https://repository-images.githubusercontent.com/1385164626/c451f484-88a4-4d0b-9806-b493c2dc53e4" width="640" alt="PopNote!"></a>

**Type:** Python &nbsp;·&nbsp; **Platforms:** macOS · Windows &nbsp;·&nbsp; **Latest:** [v0.3.0](https://github.com/kobito-tools/PopNote/tree/v0.3.0)
<!-- TOOLS:END -->

---

<sub>The app list is generated automatically by GitHub Actions from the cards of public repositories that have a `kobito-app.json` (`kobito-app.json`, the icon in `kobito/`, and `assets/social-preview.png`).</sub>
