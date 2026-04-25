import * as Phaser from "phaser";
import type { EndSceneData } from "./scene";

export class EndScene extends Phaser.Scene {
  constructor() {
    super("end-scene");
  }

  create(data: EndSceneData) {
    const width = this.scale.width;
    const height = this.scale.height;

    const bg = this.add.graphics();
    bg.fillGradientStyle(0x0c1f13, 0x0c1f13, 0x04150a, 0x04150a, 1);
    bg.fillRect(0, 0, width, height);

    this.add
      .text(width * 0.5, 60, `${data.winner.toUpperCase()} TEAM WINS`, {
        fontFamily: "Orbitron, sans-serif",
        fontSize: "34px",
        color: data.winner === "blue" ? "#7de2ff" : "#ff7c97",
      })
      .setOrigin(0.5);

    const panel = this.add.rectangle(width * 0.5, height * 0.5, Math.min(760, width * 0.88), Math.min(420, height * 0.74), 0x081811, 0.88).setStrokeStyle(2, 0x7ad9a1, 0.45);
    panel.setOrigin(0.5);

    const rows = [
      `Turns: ${data.turns}`,
      `Red HP / Shield: ${data.redHp} / ${data.redShield}`,
      `Blue HP / Shield: ${data.blueHp} / ${data.blueShield}`,
      `Grader Violation Avg: ${data.violationAvg.toFixed(3)}`,
      `Grader Novelty Avg: ${data.noveltyAvg.toFixed(3)}`,
      `Registry Size: ${data.registrySize}`,
      `Emergent Attacks: ${data.emergentCount}`,
    ];

    this.add
      .text(width * 0.5, height * 0.5 - 120, "Final Stats & Grader Metrics", {
        fontFamily: "Orbitron, sans-serif",
        fontSize: "20px",
        color: "#d9ffea",
      })
      .setOrigin(0.5);

    rows.forEach((line, idx) => {
      this.add
        .text(width * 0.5, height * 0.5 - 74 + idx * 36, line, {
          fontFamily: "Exo 2, sans-serif",
          fontSize: "18px",
          color: "#d8fce8",
        })
        .setOrigin(0.5);
    });

    const replay = this.add.rectangle(width * 0.5, height * 0.5 + 162, 200, 42, 0x2cab75, 0.95).setStrokeStyle(2, 0xa8ffd3, 0.9).setInteractive({ useHandCursor: true });
    this.add
      .text(replay.x, replay.y, "Play Again", {
        fontFamily: "Orbitron, sans-serif",
        fontSize: "18px",
        color: "#052312",
      })
      .setOrigin(0.5);

    replay.on("pointerup", () => {
      this.scene.start("goat-battle-scene");
    });
  }
}
