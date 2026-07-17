# Godot 4 adapter

Target: Godot 4.x `Control` and `Theme` system.

## Install

1. Copy `addons/rainport_ui` into the target project's `addons` directory.
2. Set `res://addons/rainport_ui/rainport_theme.tres` as `gui/theme/custom` in Project Settings, or assign it to a root `Control.theme` property.
3. Use standard Controls and select one of the provided `theme_type_variation` values.
4. Open `demo/rainport_showcase.tscn` after copying it into the target project to inspect the minimal composition.

Godot applies a Theme set on a parent Control to its descendants, so one root assignment is normally enough.

## Theme variations

- `RainportDisplayLabel`
- `RainportKickerLabel`
- `RainportDangerButton`
- `RainportNightButton`
- `RainportPaperPanel`
- `RainportNightPanel`
- `RainportAlertPanel`

`rainport_tokens.gd` exposes matching colors and metrics for custom drawing or procedural Controls.

## Texture-backed components

The default Theme uses `StyleBoxFlat` so it scales cleanly at every resolution. When exact printed edges are more important, replace a local style with `StyleBoxTexture` and use a PNG from `assets/1x` or `2x`. Slice borders live in `assets/asset-slices.json`; double them for 2× files.

Do not edit generated token or Theme files directly. Keep project-specific overrides in a separate Theme that merges or overrides the Rainport base.
