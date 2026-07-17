import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const errors = [];
let assertions = 0;

function absolute(relativePath) {
  return path.join(ROOT, ...relativePath.split("/"));
}

function check(condition, message) {
  assertions += 1;
  if (!condition) {
    errors.push(message);
  }
}

function readText(relativePath) {
  return fs.readFileSync(absolute(relativePath), "utf8");
}

function readJson(relativePath) {
  return JSON.parse(readText(relativePath));
}

function sha256(relativePath) {
  return crypto.createHash("sha256").update(fs.readFileSync(absolute(relativePath))).digest("hex");
}

function pngDimensions(relativePath) {
  const data = fs.readFileSync(absolute(relativePath));
  check(data.length >= 24, relativePath + " is too small to be a PNG");
  check(data.subarray(0, 8).equals(Buffer.from([137, 80, 78, 71, 13, 10, 26, 10])), relativePath + " has an invalid PNG signature");
  check(data.toString("ascii", 12, 16) === "IHDR", relativePath + " is missing an IHDR chunk");
  return [data.readUInt32BE(16), data.readUInt32BE(20)];
}

function sameDimensions(actual, expected) {
  return actual[0] === expected[0] && actual[1] === expected[1];
}

function kebabCase(value) {
  return value.replace(/([a-z0-9])([A-Z])/g, "$1-$2").toLowerCase();
}

function balanced(source, opener, closer) {
  let depth = 0;
  for (const character of source) {
    if (character === opener) depth += 1;
    if (character === closer) depth -= 1;
    if (depth < 0) return false;
  }
  return depth === 0;
}

function validateCore() {
  const manifest = readJson("manifest.json");
  const tokens = readJson("tokens/rainport.tokens.json");
  const slices = readJson("generated/asset-slices.json");
  const entries = { ...slices.assets, ...slices.icons };

  check(manifest.version === tokens.version, "manifest and token versions differ");
  check(manifest.prefix === tokens.prefix, "manifest and token prefixes differ");
  check(slices.version === tokens.version, "slice manifest and token versions differ");
  check(slices.referenceScale === 1, "slice manifest referenceScale must be 1");
  check(Object.keys(entries).length === 26, "the core kit must contain 26 authored UI assets");
  check(Object.keys(slices.icons).length === 11, "the core kit must contain 11 interface icons");
  check(manifest.status === "internal-proprietary", "manifest status must match the current license policy");
  for (const excluded of ["characters", "roads", "vehicles", "level art", "gameplay rendering"]) {
    check(manifest.excludedScope.includes(excluded), "manifest must keep gameplay art out of the UI package: " + excluded);
  }

  for (const [name, metadata] of Object.entries(entries)) {
    const oneX = "assets/png/1x/" + name + ".png";
    const twoX = "assets/png/2x/" + name + ".png";
    const source = "assets/source/" + name + ".svg";

    check(metadata.file === oneX, name + " points to an unexpected 1x file");
    check(fs.existsSync(absolute(oneX)), oneX + " is missing");
    check(fs.existsSync(absolute(twoX)), twoX + " is missing");
    check(fs.existsSync(absolute(source)), source + " is missing");
    check(sameDimensions(pngDimensions(oneX), metadata.size), oneX + " dimensions do not match metadata");
    check(sameDimensions(pngDimensions(twoX), metadata.size.map((value) => value * 2)), twoX + " must be exactly 2x");
    check(readText(source).includes("<svg"), source + " is not an SVG source file");

    if (metadata.mode === "sliced") {
      const border = metadata.slice;
      check(Boolean(border), name + " is sliced but has no border metadata");
      check(border.left + border.right < metadata.size[0], name + " horizontal slice borders overlap");
      check(border.top + border.bottom < metadata.size[1], name + " vertical slice borders overlap");
      check(metadata.minSize[0] >= border.left + border.right, name + " minimum width is smaller than its fixed borders");
      check(metadata.minSize[1] >= border.top + border.bottom, name + " minimum height is smaller than its fixed borders");
    }
  }

  const fontFiles = [
    "assets/fonts/ZCOOLKuaiLe-Regular.ttf",
    "assets/fonts/NotoSansSC-Variable.ttf",
  ];
  for (const font of fontFiles) {
    const signature = fs.readFileSync(absolute(font)).subarray(0, 4).toString("hex");
    check(signature === "00010000" || signature === "4f54544f", font + " has an invalid OpenType signature");
    check(fs.statSync(absolute(font)).size > 100000, font + " appears truncated");
  }

  check(fs.existsSync(absolute("LICENSE-POLICY.md")), "root license policy is missing");
  check(fs.existsSync(absolute("THIRD_PARTY_NOTICES.md")), "third-party notices are missing");
  check(fs.existsSync(absolute("third-party/ZCOOL-KuaiLe-OFL.txt")), "ZCOOL KuaiLe OFL text is missing");
  check(fs.existsSync(absolute("third-party/Noto-Sans-SC-OFL.txt")), "Noto Sans SC OFL text is missing");

  const webTokens = readText("generated/web/rainport.tokens.css");
  for (const [name, data] of Object.entries(tokens.color)) {
    check(webTokens.includes("--rp-" + kebabCase(name) + ": " + data.value), "web token is missing: " + name);
  }

  check(sameDimensions(pngDimensions("preview/rainport-ui-kit-sheet.png"), [1600, 1120]), "contact sheet must be 1600x1120");
  const readme = readText("README.md");
  for (const preview of [
    "preview/rainport-ui-loadout.png",
    "preview/rainport-ui-result.png",
    "preview/rainport-ui-engines.png",
  ]) {
    check(sameDimensions(pngDimensions(preview), [1440, 900]), preview + " must be 1440x900");
    check(readme.includes("(" + preview + ")"), "README does not reference " + preview);
  }
  return { manifest, tokens, slices, entries, fontFiles };
}

function validateAdapterCopies(entries, fontFiles) {
  const adapters = [
    { name: "unity", assetRoot: "adapters/unity/Runtime/Assets", fontRoot: "adapters/unity/Runtime/Fonts" },
    { name: "godot", assetRoot: "adapters/godot/addons/rainport_ui/assets", fontRoot: "adapters/godot/addons/rainport_ui/fonts" },
    { name: "cocos", assetRoot: "adapters/cocos/assets/rainport-ui/textures", fontRoot: "adapters/cocos/assets/rainport-ui/fonts" },
  ];

  for (const adapter of adapters) {
    check(sha256(adapter.assetRoot + "/asset-slices.json") === sha256("generated/asset-slices.json"), adapter.name + " slice manifest drifted");
    for (const name of Object.keys(entries)) {
      for (const scale of ["1x", "2x"]) {
        const canonical = "assets/png/" + scale + "/" + name + ".png";
        const copy = adapter.assetRoot + "/" + scale + "/" + name + ".png";
        check(fs.existsSync(absolute(copy)), adapter.name + " is missing " + copy);
        check(sha256(copy) === sha256(canonical), adapter.name + " asset copy drifted: " + name + " " + scale);
      }
    }
    for (const font of fontFiles) {
      const name = path.basename(font);
      const copy = adapter.fontRoot + "/" + name;
      check(fs.existsSync(absolute(copy)), adapter.name + " is missing font " + name);
      check(sha256(copy) === sha256(font), adapter.name + " font copy drifted: " + name);
    }
    check(sha256("adapters/" + adapter.name + "/LICENSE-POLICY.md") === sha256("LICENSE-POLICY.md"), adapter.name + " license policy drifted");
    check(sha256("adapters/" + adapter.name + "/THIRD_PARTY_NOTICES.md") === sha256("THIRD_PARTY_NOTICES.md"), adapter.name + " third-party notices drifted");
    for (const license of ["ZCOOL-KuaiLe-OFL.txt", "Noto-Sans-SC-OFL.txt"]) {
      check(sha256("adapters/" + adapter.name + "/third-party/" + license) === sha256("third-party/" + license), adapter.name + " OFL copy drifted: " + license);
    }
  }
}

function validateUnity(tokens) {
  const unityPackage = readJson("adapters/unity/package.json");
  const assembly = readJson("adapters/unity/Runtime/RainportUI.asmdef");
  const tokenSource = readText("adapters/unity/Runtime/Styles/RainportTokens.uss");
  const themeSource = readText("adapters/unity/Runtime/Styles/RainportTheme.uss");
  const uxmlPath = "adapters/unity/Runtime/Templates/RainportShowcase.uxml";
  const uxml = readText(uxmlPath);

  check(unityPackage.name === "com.rainport.ui", "Unity UPM package id is incorrect");
  check(unityPackage.version === tokens.version, "Unity package version differs from tokens");
  check(unityPackage.unity === "2022.3", "Unity compatibility floor must remain explicit");
  check(unityPackage.license === "SEE LICENSE IN LICENSE-POLICY.md", "Unity package must point to its license policy");
  check(assembly.name === "Rainport.UI", "Unity assembly name is incorrect");
  check(tokenSource.includes("AUTO-GENERATED"), "Unity tokens must identify themselves as generated");
  check(themeSource.includes('@import url("RainportTokens.uss")'), "Unity theme does not import its tokens");
  check(themeSource.includes("-unity-slice-left"), "Unity theme is missing 9-slice declarations");

  for (const [name, data] of Object.entries(tokens.color)) {
    check(tokenSource.includes("--rp-" + kebabCase(name) + ": " + data.value), "Unity token is missing: " + name);
  }

  const projectUrls = [...themeSource.matchAll(/project:\/\/database\/Packages\/com\.rainport\.ui\/([^")]+)/g)].map((match) => match[1]);
  check(projectUrls.length >= 10, "Unity theme has too few package asset references");
  for (const relative of projectUrls) {
    check(fs.existsSync(absolute("adapters/unity/" + relative)), "Unity theme references a missing package file: " + relative);
  }

  const styleReference = uxml.match(/<Style src="([^"]+)"\s*\/>/);
  check(Boolean(styleReference), "Unity showcase has no style reference");
  if (styleReference) {
    const resolved = path.resolve(path.dirname(absolute(uxmlPath)), styleReference[1]);
    check(fs.existsSync(resolved), "Unity showcase style reference is broken");
  }
  check(uxml.startsWith("<ui:UXML"), "Unity showcase must start with a UXML root");
  check(uxml.trimEnd().endsWith("</ui:UXML>"), "Unity showcase has no closing UXML root");

  const classNames = new Set([...uxml.matchAll(/class="([^"]+)"/g)].flatMap((match) => match[1].split(/\s+/)));
  for (const className of classNames) {
    check(themeSource.includes("." + className), "Unity showcase uses an undefined class: " + className);
  }
}

function validateGodot(tokens) {
  const tokenSource = readText("adapters/godot/addons/rainport_ui/rainport_tokens.gd");
  const theme = readText("adapters/godot/addons/rainport_ui/rainport_theme.tres");
  const demo = readText("adapters/godot/demo/rainport_showcase.tscn");

  check(tokenSource.includes("AUTO-GENERATED"), "Godot tokens must identify themselves as generated");
  check(theme.startsWith('[gd_resource type="Theme" load_steps=11 format=3]'), "Godot Theme load_steps must match its resources");
  check((theme.match(/\[sub_resource type="StyleBoxFlat"/g) || []).length === 8, "Godot Theme must contain eight StyleBox resources");
  check((theme.match(/shadow_size = 1/g) || []).length === 8, "Godot hard shadows must remain enabled");
  check(!theme.includes("shadow_size = 0"), "Godot Theme contains a disabled shadow");

  for (const [name, data] of Object.entries(tokens.color)) {
    check(tokenSource.includes("const " + name.toUpperCase() + ' := Color("' + data.value + '")'), "Godot token is missing: " + name);
  }

  const resPaths = [...theme.matchAll(/path="res:\/\/([^"]+)"/g)].map((match) => match[1]);
  check(resPaths.length === 2, "Godot Theme must reference both bundled fonts");
  for (const relative of resPaths) {
    check(fs.existsSync(absolute("adapters/godot/" + relative)), "Godot Theme references a missing resource: " + relative);
  }

  for (const variation of ["RainportDisplayLabel", "RainportKickerLabel", "RainportDangerButton", "RainportNightButton", "RainportPaperPanel", "RainportNightPanel", "RainportAlertPanel"]) {
    check(theme.includes(variation + "/base_type") || theme.includes(variation + "/fonts/"), "Godot Theme is missing variation: " + variation);
    check(demo.includes(variation) || variation === "RainportKickerLabel", "Godot demo does not exercise variation: " + variation);
  }
  check(demo.startsWith("[gd_scene load_steps=2 format=3]"), "Godot demo scene header is invalid");
  check((demo.match(/\[node /g) || []).length >= 15, "Godot demo scene is unexpectedly small");
}

function validateCocos(tokens) {
  const tokenSource = readText("adapters/cocos/assets/rainport-ui/scripts/rainport-tokens.ts");
  const styleSource = readText("adapters/cocos/assets/rainport-ui/scripts/rainport-style.ts");
  const buttonSource = readText("adapters/cocos/assets/rainport-ui/scripts/RainportButton.ts");

  check(tokenSource.includes("AUTO-GENERATED"), "Cocos tokens must identify themselves as generated");
  for (const [name, data] of Object.entries(tokens.color)) {
    check(tokenSource.includes(name + ': "' + data.value + '"'), "Cocos token is missing: " + name);
  }

  for (const [name, source] of [["rainport-style.ts", styleSource], ["RainportButton.ts", buttonSource], ["rainport-tokens.ts", tokenSource]]) {
    check(balanced(source, "{", "}"), "Cocos script has unbalanced braces: " + name);
    check(!/\bany\b/.test(source), "Cocos script uses an untyped any: " + name);
  }

  check(styleSource.includes('from "cc"'), "Cocos style helpers do not import the engine API");
  check(styleSource.includes("Sprite.Type.SLICED"), "Cocos helper does not configure sliced sprites");
  check(styleSource.includes("Color.fromHEX"), "Cocos helper does not convert token colors");
  check(buttonSource.includes('@ccclass("RainportButton")'), "Cocos button component is not registered");
  for (const eventName of ["TOUCH_START", "TOUCH_END", "TOUCH_CANCEL", "MOUSE_LEAVE"]) {
    check(buttonSource.includes("Node.EventType." + eventName), "Cocos button is missing release-safe event: " + eventName);
  }
}

function main() {
  const core = validateCore();
  validateAdapterCopies(core.entries, core.fontFiles);
  validateUnity(core.tokens);
  validateGodot(core.tokens);
  validateCocos(core.tokens);

  const report = {
    status: errors.length === 0 ? "passed" : "failed",
    version: core.tokens.version,
    assertions,
    assets: Object.keys(core.entries).length,
    adapters: ["unity", "godot", "cocos"],
    errors,
  };
  console.log(JSON.stringify(report, null, 2));
  if (errors.length > 0) {
    process.exitCode = 1;
  }
}

try {
  main();
} catch (error) {
  console.error(JSON.stringify({ status: "failed", fatal: error.message, stack: error.stack }, null, 2));
  process.exitCode = 1;
}
