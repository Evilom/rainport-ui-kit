import { Button, Color, Label, Sprite, Vec3 } from "cc";
import { RAINPORT_COLORS, RAINPORT_METRICS } from "./rainport-tokens";

export type RainportButtonVariant = "signal" | "night" | "danger";
export type RainportLabelRole = "body" | "button" | "cardTitle" | "display" | "caption";

export function rainportColor(hex: string): Color {
  return Color.fromHEX(new Color(), hex);
}

export function applyRainportLabel(label: Label, role: RainportLabelRole): void {
  const sizes: Record<RainportLabelRole, number> = {
    caption: 12,
    body: 16,
    button: 16,
    cardTitle: 28,
    display: 52,
  };

  label.fontSize = sizes[role];
  label.lineHeight = Math.round(sizes[role] * (role === "body" ? 1.65 : 1.12));
  label.enableWrapText = role !== "button";
  label.isBold = role === "button" || role === "caption";
  label.color = rainportColor(RAINPORT_COLORS.ink);
  label.enableOutline = role === "display";
  label.outlineColor = rainportColor(RAINPORT_COLORS.white);
  label.outlineWidth = role === "display" ? 2 : 0;
}

export function applyRainportButton(button: Button, variant: RainportButtonVariant): void {
  const base = variant === "signal" ? RAINPORT_COLORS.signal : variant === "night" ? RAINPORT_COLORS.night : RAINPORT_COLORS.danger;
  button.transition = Button.Transition.COLOR;
  button.normalColor = rainportColor(base);
  button.hoverColor = rainportColor(variant === "signal" ? RAINPORT_COLORS.white : RAINPORT_COLORS.rain);
  button.pressedColor = rainportColor(variant === "danger" ? RAINPORT_COLORS.danger : RAINPORT_COLORS.signal);
  button.disabledColor = rainportColor(RAINPORT_COLORS.disabled);
  button.duration = RAINPORT_METRICS.pressTranslate.x / 25;
}

export function configureRainportSlicedSprite(sprite: Sprite): void {
  sprite.type = Sprite.Type.SLICED;
  sprite.sizeMode = Sprite.SizeMode.CUSTOM;
  sprite.trim = false;
}

export function rainportShadowOffset(size: "small" | "medium" = "small"): Vec3 {
  const offset = size === "medium" ? RAINPORT_METRICS.shadowMedium : RAINPORT_METRICS.shadowSmall;
  return new Vec3(offset.x, -offset.y, 0);
}
