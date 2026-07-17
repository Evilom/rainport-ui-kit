import { _decorator, Component, Node, Vec3 } from "cc";
import { RAINPORT_METRICS } from "./rainport-tokens";

const { ccclass, property } = _decorator;

@ccclass("RainportButton")
export class RainportButton extends Component {
  @property({ type: Node, tooltip: "The visible surface that moves while the shadow remains fixed." })
  public surface: Node | null = null;

  @property({ tooltip: "Override the shared pressed offset. Set to zero to use the token value." })
  public pressedOffset = 0;

  private readonly restPosition = new Vec3();

  protected onEnable(): void {
    const target = this.surface ?? this.node;
    this.restPosition.set(target.position);
    this.node.on(Node.EventType.TOUCH_START, this.handlePress, this);
    this.node.on(Node.EventType.TOUCH_END, this.handleRelease, this);
    this.node.on(Node.EventType.TOUCH_CANCEL, this.handleRelease, this);
    this.node.on(Node.EventType.MOUSE_LEAVE, this.handleRelease, this);
  }

  protected onDisable(): void {
    this.node.off(Node.EventType.TOUCH_START, this.handlePress, this);
    this.node.off(Node.EventType.TOUCH_END, this.handleRelease, this);
    this.node.off(Node.EventType.TOUCH_CANCEL, this.handleRelease, this);
    this.node.off(Node.EventType.MOUSE_LEAVE, this.handleRelease, this);
    this.restoreSurface();
  }

  private handlePress(): void {
    const target = this.surface ?? this.node;
    const amount = this.pressedOffset || RAINPORT_METRICS.pressTranslate.x;
    target.setPosition(this.restPosition.x + amount, this.restPosition.y - amount, this.restPosition.z);
  }

  private handleRelease(): void {
    this.restoreSurface();
  }

  private restoreSurface(): void {
    const target = this.surface ?? this.node;
    target.setPosition(this.restPosition);
  }
}
