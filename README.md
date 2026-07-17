# 雨港印刷街机 UI Kit

`Rainport Print-Arcade UI` 是一套面向游戏项目的跨引擎界面设计系统。它把项目里反响最好的 UI 语言整理为一个可版本化、可生成、可移植的内部资产包。

## 核心原则

- `tokens/rainport.tokens.json` 是唯一可手工修改的设计令牌源。
- `tools/generate_kit.py` 负责生成平台令牌、SVG、1×/2× PNG、九宫格数据和预览图。
- Unity、Godot、Cocos 适配层只翻译核心系统，不建立自己的颜色和尺寸分支。
- 包内只包含界面资产，不包含当前游戏的角色、道路、车辆、关卡或局内渲染素材。

## 目录

```text
rainport-ui-kit/
├─ tokens/                 # 唯一设计令牌源
├─ assets/
│  ├─ source/              # 可编辑 SVG
│  ├─ png/1x/              # 标准分辨率
│  ├─ png/2x/              # 高分辨率
│  └─ fonts/               # 跨引擎 TTF
├─ generated/              # 平台令牌和九宫格数据
├─ adapters/
│  ├─ unity/               # UPM / UI Toolkit / uGUI 素材
│  ├─ godot/               # Godot 4 addon
│  └─ cocos/               # Cocos Creator 3.8 assets
├─ preview/                # 接触表预览
└─ tools/                  # 生成与验证脚本
```

## 生成与验证

在仓库根目录运行：

```powershell
npm run ui-kit:generate
npm run ui-kit:validate
npm run ui-kit:package
```

生成脚本是确定性的：同一份令牌和字体应生成相同的文件哈希。

ui-kit:package 会在仓库的 output/rainport-ui-kit 下生成源码、Unity、Godot、Cocos Creator 四个独立压缩包，并写出 SHA256SUMS.txt。结构校验会检查 PNG 尺寸、九宫格边界、字体签名、令牌同步、引擎资源引用和许可文件；首次接入具体项目时，仍应在目标引擎编辑器中打开对应示例，完成该项目的原生导入与平台预览。

## 在项目中使用

- Unity：把 `adapters/unity` 作为本地 UPM 包安装，或将其 `Runtime/Assets` 中的 PNG 设置为 9-slice Sprite 后供 uGUI 使用。
- Godot：将 `adapters/godot/addons/rainport_ui` 复制到项目的 `addons`，把 `rainport_theme.tres` 设置为项目 Theme。
- Cocos：将 `adapters/cocos/assets/rainport-ui` 复制进 Creator 项目的 `assets`，等待编辑器生成 `.meta`，再按切片表设置 Sliced Sprite。

每套适配层都有更具体的说明和最小示例。

## 版本治理

- 修复导入说明或不改变画面的代码：补丁版本。
- 新增兼容组件或可选令牌：次版本。
- 修改核心色、描边、阴影方向、字体角色或组件结构：主版本。

任何项目特化都应该放到项目自己的 override 层，不能直接改生成文件。

## 许可

Rainport 自有部分暂按内部专有资产管理，不附加公开开源授权。字体分别遵循 SIL Open Font License 1.1，详情见 `THIRD_PARTY_NOTICES.md` 与 `third-party/`。
