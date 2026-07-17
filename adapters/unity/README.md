# Unity adapter

Target: Unity 2022.3 LTS and Unity 6.

Unity UI Toolkit uses USS/UXML and supports USS custom properties. Rainport therefore keeps platform tokens in `Runtime/Styles/RainportTokens.uss` and component classes in `RainportTheme.uss`.

## Install as a local UPM package

1. Open Package Manager.
2. Choose **Add package from disk**.
3. Select this folder's `package.json`.
4. Add `Runtime/Templates/RainportShowcase.uxml` to a `UIDocument`, or import `RainportTheme.uss` into your own UXML.
5. Use the public classes prefixed with `rp-`.

Generated token files should not be edited. Put project changes in a separate USS loaded after `RainportTheme.uss`.

## uGUI fallback

The PNGs under `Runtime/Assets/1x` and `2x` also work with Unity UI (`Image.Type.Sliced`):

1. Set Texture Type to **Sprite (2D and UI)**.
2. Use **Full Rect** mesh and disable destructive trimming.
3. Read borders from `Runtime/Assets/asset-slices.json`.
4. Multiply every border value by two when using a `2x` file.
5. Set the Image Type to **Sliced** and preserve the original hard-shadow padding.

For dynamic Chinese text, import the TTF files into TextMesh Pro font assets if the project uses TMP. Keep the original OFL notices when redistributing fonts.

## Public classes

- `rp-root`, `rp-toolbar`, `rp-brand`
- `rp-kicker`, `rp-display`, `rp-copy`
- `rp-card`, `rp-card--selected`, `rp-card--night`
- `rp-button`, `rp-button--night`, `rp-button--danger`
- `rp-alert`, `rp-tag`, `rp-tag--danger`
- `rp-stat`, `rp-meter`, `rp-receipt`

The package uses 9-slice PNGs for hard shadows because UI Toolkit does not provide a cross-version CSS box-shadow equivalent with the required crisp result.
