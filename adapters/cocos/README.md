# Cocos Creator adapter

Target: Cocos Creator 3.8 LTS and compatible later 3.x versions.

## Install

1. Copy `assets/rainport-ui` into the target Creator project's `assets` directory.
2. Wait for Creator to import the TTF and PNG files and create its own `.meta` files.
3. Add a Sprite to each scalable background and set its Type to **Sliced**.
4. Read 1× borders from `textures/asset-slices.json`; multiply by two for files under `textures/2x`.
5. Use `RainportButton` on a button root when the visible face and hard shadow are separate child nodes.

Cocos Creator's Sliced mode uses a 9-slice grid and is the recommended representation for Rainport panels and buttons.

## Script API

- `RAINPORT_COLORS` and `RAINPORT_METRICS`: immutable generated tokens.
- `rainportColor`: converts a token hex value to `Color`.
- `applyRainportLabel`: sets role-based size, leading, outline, and wrapping.
- `applyRainportButton`: maps signal/night/danger state colors.
- `configureRainportSlicedSprite`: applies the required Sprite settings.
- `RainportButton`: moves the visible surface down-right on press while the shadow stays in place.

## Recommended node structure

```text
ButtonRoot [Button, RainportButton]
├─ Shadow [Sprite]
└─ Surface [Sprite]
   └─ Label [Label]
```

Assign `Surface` to `RainportButton.surface`. Keep the Shadow at the token offset and do not animate it with the Surface.

## Fonts

Assign `fonts/ZCOOLKuaiLe-Regular.ttf` only to short display text. Use `fonts/NotoSansSC-Variable.ttf` for body copy, buttons, and changing data. Retain the bundled OFL notices when redistributing the fonts.

Do not directly edit `rainport-tokens.ts`. Project-specific color or layout changes belong in a separate module that imports and extends the Rainport constants.
