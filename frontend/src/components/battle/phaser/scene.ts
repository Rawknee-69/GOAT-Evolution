import * as Phaser from "phaser";
import { battleAssetManifest } from "./assets";
import type { BattleAction } from "./events";

interface UnitState {
  id: string;
  team: "red" | "blue";
  lane: number;
  sprite: Phaser.GameObjects.Image;
  hp: number;
  shield: number;
  cooldown: number;
  alive: boolean;
  anchorX: number;
  anchorY: number;
}

interface CoverState {
  lane: number;
  team: "red" | "blue";
  dynamic: boolean;
  hp: number;
  sprite: Phaser.GameObjects.Image;
}

export interface EndSceneData {
  winner: "red" | "blue";
  loser: "red" | "blue";
  turns: number;
  redHp: number;
  blueHp: number;
  redShield: number;
  blueShield: number;
  registrySize: number;
  emergentCount: number;
  violationAvg: number;
  noveltyAvg: number;
}

export interface BattleSceneSnapshot {
  redHp: number;
  blueHp: number;
  redShield: number;
  blueShield: number;
  turn: number;
  winner?: "red" | "blue";
}

export class GoatBattleScene extends Phaser.Scene {
  private redUnits: UnitState[] = [];
  private blueUnits: UnitState[] = [];
  private covers: CoverState[] = [];
  private turn = 0;
  private speed = 1;
  private winner?: "red" | "blue";
  private onSnapshot?: (snapshot: BattleSceneSnapshot) => void;
  private ready = false;
  private violationSamples: number[] = [];
  private noveltySamples: number[] = [];
  private registrySize = 0;
  private emergentCount = 0;

  constructor() {
    super("goat-battle-scene");
  }

  preload() {
    for (const asset of battleAssetManifest) {
      this.load.image(asset.key, asset.url);
    }
  }

  create() {
    this.ready = true;
    this.createBackground();
    this.createCovers();
    this.createUnits();
    this.setSpeed(this.speed);
    this.emitSnapshot();
  }

  setSpeed(speed: number) {
    this.speed = Math.max(0.5, Math.min(2.5, speed));
    if (!this.ready) return;
    if (this.time) this.time.timeScale = this.speed;
    if (this.tweens) this.tweens.timeScale = this.speed;
  }

  setSnapshotHandler(handler: (snapshot: BattleSceneSnapshot) => void) {
    this.onSnapshot = handler;
    this.emitSnapshot();
  }

  setBattleMeta(meta: { registrySize?: number; emergentCount?: number }) {
    if (typeof meta.registrySize === "number") this.registrySize = meta.registrySize;
    if (typeof meta.emergentCount === "number") this.emergentCount = meta.emergentCount;
  }

  resetBattle() {
    if (!this.ready) return;
    this.turn = 0;
    this.winner = undefined;
    this.violationSamples = [];
    this.noveltySamples = [];
    [...this.redUnits, ...this.blueUnits].forEach((unit) => {
      unit.hp = 100;
      unit.shield = 25;
      unit.cooldown = 0;
      unit.alive = true;
      unit.sprite.setX(unit.anchorX).setY(unit.anchorY);
      unit.sprite.setScale(1.4);
      unit.sprite.setAlpha(1);
      unit.sprite.clearTint();
    });
    this.covers.forEach((cover) => {
      cover.hp = cover.dynamic ? 80 : 999;
      cover.sprite.setAlpha(1).clearTint();
    });
    this.emitSnapshot();
  }

  applyAction(action: BattleAction) {
    if (!this.ready) return;
    if (this.winner) return;

    const actorSet = action.actorTeam === "red" ? this.redUnits : this.blueUnits;
    const targetSet = action.targetTeam === "red" ? this.redUnits : this.blueUnits;
    const actor = actorSet[action.lane % actorSet.length];
    const target = targetSet[action.lane % targetSet.length];
    if (!actor || !target) return;
    if (!actor.alive || !target.alive) return;

    this.turn += 1;
    actor.cooldown = Math.max(0, 2 - action.strength * 1.2);
    this.violationSamples.push(action.strength);

    switch (action.type) {
      case "attack":
      case "impact":
        this.playProjectile(actor, target);
        break;
      case "defend":
        this.noveltySamples.push(action.strength);
        this.raiseShield(target, action.strength * 16);
        break;
      case "ko":
        this.damageTarget(target, 80);
        break;
      default:
        break;
    }

    this.emitSnapshot();
  }

  forceWinner(team: "red" | "blue") {
    if (!this.ready) return;
    if (this.winner) return;
    this.winner = team;
    const losers = team === "red" ? this.blueUnits : this.redUnits;
    losers.forEach((unit) => {
      unit.hp = 0;
      unit.alive = false;
      unit.sprite.setTint(0x111111);
      unit.sprite.setAlpha(0.45);
    });
    this.emitSnapshot();
    this.transitionToEndScene();
  }

  private createBackground() {
    const width = this.scale.width;
    const height = this.scale.height;
    const horizon = height * 0.5;

    const leftSky = this.add.graphics();
    leftSky.fillGradientStyle(0x6ba6f6, 0x6ba6f6, 0x8ab8ff, 0x8ab8ff, 1);
    leftSky.fillRect(0, 0, width * 0.5, horizon);

    const rightSky = this.add.graphics();
    rightSky.fillGradientStyle(0xc8ecff, 0xc8ecff, 0xb8f0d0, 0xb8f0d0, 1);
    rightSky.fillRect(width * 0.5, 0, width * 0.5, horizon);

    this.add.image(width * 0.18, 70, "weather-cloud").setScale(0.85);
    this.add.image(width * 0.36, 110, "weather-cloud").setScale(0.65);
    const sunGlow = this.add.graphics();
    sunGlow.fillStyle(0xffef9a, 0.28);
    sunGlow.fillCircle(width * 0.82, 90, 110);
    this.add.image(width * 0.82, 90, "weather-sun").setScale(0.7);

    const ground = this.add.graphics();
    ground.fillGradientStyle(0xa9e2a3, 0xa9e2a3, 0x69b87a, 0x69b87a, 1);
    ground.fillRect(0, horizon, width, height - horizon);
    ground.fillStyle(0x2f6f3e, 0.35);
    ground.fillRect(0, horizon, width, 5);
    for (let i = 0; i < 60; i += 1) {
      const tx = (i / 60) * width;
      ground.fillStyle(0x4f9658, 0.28);
      ground.fillRect(tx, horizon + 14 + (i % 3) * 6, 10, 3);
    }
  }

  private createCovers() {
    const width = this.scale.width;
    const lanes = this.getLaneYs();
    lanes.forEach((laneY, idx) => {
      const leftCover = this.add.image(width * 0.28, laneY + 6, idx % 2 === 0 ? "obstacle-crate" : "obstacle-rock").setScale(0.85);
      const rightCover = this.add.image(width * 0.72, laneY + 6, idx % 2 === 0 ? "obstacle-rock" : "obstacle-crate").setScale(0.85);
      this.covers.push({ lane: idx, team: "red", dynamic: idx !== 1, hp: idx !== 1 ? 80 : 999, sprite: leftCover });
      this.covers.push({ lane: idx, team: "blue", dynamic: idx === 1, hp: idx === 1 ? 80 : 999, sprite: rightCover });
    });
  }

  private createUnits() {
    const width = this.scale.width;
    const redX = width * 0.12;
    const blueX = width * 0.88;
    const lanes = this.getLaneYs();

    lanes.forEach((y, lane) => {
      const redSprite = this.add.image(redX, y, "unit-red").setScale(1.4);
      const blueSprite = this.add.image(blueX, y, "unit-blue").setScale(1.4).setFlipX(true);

      this.redUnits.push({ id: `red-${lane}`, team: "red", lane, sprite: redSprite, hp: 100, shield: 25, cooldown: 0, alive: true, anchorX: redX, anchorY: y });
      this.blueUnits.push({ id: `blue-${lane}`, team: "blue", lane, sprite: blueSprite, hp: 100, shield: 25, cooldown: 0, alive: true, anchorX: blueX, anchorY: y });
    });
  }

  private getLaneYs(): number[] {
    const height = this.scale.height;
    const top = height * 0.6;
    const bottom = height * 0.9;
    const span = bottom - top;
    return [top + span * 0, top + span * 0.5, top + span * 1];
  }

  private playProjectile(from: UnitState, to: UnitState) {
    const dodgeCover = this.getCover(to.team, to.lane);
    const fromCover = this.getCover(from.team, from.lane);
    if (fromCover) this.hideBehindCover(from, fromCover, false);
    if (dodgeCover) this.hideBehindCover(to, dodgeCover, true);

    const shot = this.add.image(from.sprite.x, from.sprite.y - 8, "proj-knife").setScale(0.9);
    if (from.team === "blue") shot.setFlipX(true);
    this.tweens.add({
      targets: shot,
      x: to.sprite.x + (to.team === "red" ? -14 : 14),
      y: to.sprite.y - 8,
      duration: 260,
      ease: "Cubic.Out",
      onComplete: () => {
        shot.destroy();
        this.playImpact(to.sprite.x, to.sprite.y);
        const blocked = dodgeCover && dodgeCover.hp > 0 && Math.random() > 0.45;
        if (blocked) {
          this.damageCover(dodgeCover, 26);
        } else {
          this.damageTarget(to, 22 + Math.random() * 10);
        }
      },
    });
    this.tweens.add({
      targets: from.sprite,
      x: from.sprite.x + (from.team === "red" ? 20 : -20),
      yoyo: true,
      duration: 150,
      repeat: 0,
    });
  }

  private playImpact(x: number, y: number) {
    const ring = this.add.image(x, y, "fx-impact").setScale(0.2).setAlpha(0.9);
    this.tweens.add({
      targets: ring,
      scale: 0.8,
      alpha: 0,
      duration: 240,
      ease: "Sine.Out",
      onComplete: () => ring.destroy(),
    });
  }

  private raiseShield(target: UnitState, amount: number) {
    target.shield = Math.min(75, target.shield + amount);
    const bubble = this.add.image(target.sprite.x, target.sprite.y, "fx-shield").setScale(0.12).setAlpha(0.7);
    this.tweens.add({
      targets: bubble,
      scale: 0.42,
      alpha: 0,
      duration: 260,
      onComplete: () => bubble.destroy(),
    });
  }

  private damageTarget(target: UnitState, amount: number) {
    const shieldAbsorb = Math.min(target.shield, amount * 0.5);
    target.shield = Math.max(0, target.shield - shieldAbsorb);
    target.hp = Math.max(0, target.hp - (amount - shieldAbsorb));

    this.tweens.add({
      targets: target.sprite,
      alpha: 0.4,
      duration: 80,
      yoyo: true,
      repeat: 1,
    });

    if (target.hp <= 0) {
      target.alive = false;
      target.sprite.setTint(0x222222).setAlpha(0.5);
      const redAlive = this.redUnits.some((unit) => unit.alive);
      const blueAlive = this.blueUnits.some((unit) => unit.alive);
      if (!redAlive || !blueAlive) {
        this.winner = redAlive ? "red" : "blue";
        this.transitionToEndScene();
      }
    }
  }

  private getCover(team: "red" | "blue", lane: number) {
    return this.covers.find((cover) => cover.team === team && cover.lane === lane);
  }

  private hideBehindCover(unit: UnitState, cover: CoverState, dodge: boolean) {
    if (cover.hp <= 0) return;
    const dir = unit.team === "red" ? 1 : -1;
    const hideX = cover.sprite.x - dir * 24;
    this.tweens.add({
      targets: unit.sprite,
      x: hideX,
      y: unit.anchorY + (dodge ? 8 : 0),
      duration: 100,
      yoyo: true,
      ease: "Quad.Out",
    });
  }

  private damageCover(cover: CoverState, amount: number) {
    if (!cover.dynamic) return;
    cover.hp = Math.max(0, cover.hp - amount);
    this.tweens.add({
      targets: cover.sprite,
      alpha: 0.45,
      duration: 70,
      yoyo: true,
      repeat: 1,
    });
    if (cover.hp <= 0) {
      cover.sprite.setTint(0x2b2b2b).setAlpha(0.25);
    }
  }

  private transitionToEndScene() {
    if (!this.winner) return;
    const redHp = this.redUnits.reduce((sum, unit) => sum + unit.hp, 0);
    const blueHp = this.blueUnits.reduce((sum, unit) => sum + unit.hp, 0);
    const redShield = this.redUnits.reduce((sum, unit) => sum + unit.shield, 0);
    const blueShield = this.blueUnits.reduce((sum, unit) => sum + unit.shield, 0);
    const violationAvg = this.violationSamples.length ? this.violationSamples.reduce((sum, value) => sum + value, 0) / this.violationSamples.length : 0;
    const noveltyAvg = this.noveltySamples.length ? this.noveltySamples.reduce((sum, value) => sum + value, 0) / this.noveltySamples.length : 0;
    const payload: EndSceneData = {
      winner: this.winner,
      loser: this.winner === "red" ? "blue" : "red",
      turns: this.turn,
      redHp: Math.round(redHp),
      blueHp: Math.round(blueHp),
      redShield: Math.round(redShield),
      blueShield: Math.round(blueShield),
      registrySize: this.registrySize,
      emergentCount: this.emergentCount,
      violationAvg,
      noveltyAvg,
    };
    this.scene.start("end-scene", payload);
  }

  private emitSnapshot() {
    if (!this.onSnapshot) return;
    const redHp = this.redUnits.reduce((sum, unit) => sum + unit.hp, 0);
    const blueHp = this.blueUnits.reduce((sum, unit) => sum + unit.hp, 0);
    const redShield = this.redUnits.reduce((sum, unit) => sum + unit.shield, 0);
    const blueShield = this.blueUnits.reduce((sum, unit) => sum + unit.shield, 0);
    this.onSnapshot({
      redHp: Math.round(redHp),
      blueHp: Math.round(blueHp),
      redShield: Math.round(redShield),
      blueShield: Math.round(blueShield),
      turn: this.turn,
      winner: this.winner,
    });
  }
}
