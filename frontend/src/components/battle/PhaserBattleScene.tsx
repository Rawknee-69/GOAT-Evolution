import { useEffect, useRef } from "react";
import * as Phaser from "phaser";
import { GoatBattleScene, type BattleSceneSnapshot } from "./phaser/scene";
import { EndScene } from "./phaser/endScene";
import { eventToBattleAction } from "./phaser/events";

interface PhaserBattleSceneProps {
  events: any[];
  speed: number;
  stateWinner?: "red" | "blue";
  registrySize?: number;
  emergentCount?: number;
  resetVersion?: number;
  onSnapshot: (snapshot: BattleSceneSnapshot) => void;
}

export function PhaserBattleScene({ events, speed, stateWinner, registrySize, emergentCount, resetVersion, onSnapshot }: PhaserBattleSceneProps) {
  const mountRef = useRef<HTMLDivElement | null>(null);
  const gameRef = useRef<Phaser.Game | null>(null);
  const sceneRef = useRef<GoatBattleScene | null>(null);
  const processedEventsRef = useRef(0);

  useEffect(() => {
    if (!mountRef.current || gameRef.current) return;

    const scene = new GoatBattleScene();
    const game = new Phaser.Game({
      type: Phaser.AUTO,
      width: mountRef.current.clientWidth || 1200,
      height: mountRef.current.clientHeight || 760,
      backgroundColor: "#0b1f15",
      parent: mountRef.current,
      scene: [scene, new EndScene()],
      scale: {
        mode: Phaser.Scale.RESIZE,
        autoCenter: Phaser.Scale.CENTER_BOTH,
      },
      render: {
        antialias: true,
        pixelArt: true,
      },
      audio: {
        noAudio: true,
      },
    });

    gameRef.current = game;
    sceneRef.current = scene;
    scene.setSnapshotHandler(onSnapshot);
    scene.setSpeed(speed);
    scene.resetBattle();

    const observer = new ResizeObserver(() => {
      if (!gameRef.current || !mountRef.current) return;
      gameRef.current.scale.resize(mountRef.current.clientWidth, mountRef.current.clientHeight);
    });
    observer.observe(mountRef.current);

    return () => {
      observer.disconnect();
      processedEventsRef.current = 0;
      sceneRef.current = null;
      gameRef.current?.destroy(true);
      gameRef.current = null;
    };
  }, [onSnapshot, speed]);

  useEffect(() => {
    sceneRef.current?.setSpeed(speed);
  }, [speed]);

  useEffect(() => {
    sceneRef.current?.setBattleMeta({ registrySize, emergentCount });
  }, [registrySize, emergentCount]);

  useEffect(() => {
    const scene = sceneRef.current;
    if (!scene) return;
    const incoming = events.slice(processedEventsRef.current);
    processedEventsRef.current = events.length;
    for (const event of incoming) {
      const action = eventToBattleAction(event);
      if (action) scene.applyAction(action);
    }
  }, [events]);

  useEffect(() => {
    if (!stateWinner) return;
    sceneRef.current?.forceWinner(stateWinner);
  }, [stateWinner]);

  useEffect(() => {
    if (resetVersion === undefined) return;
    const game = gameRef.current;
    const scene = sceneRef.current;
    if (!game || !scene) return;
    processedEventsRef.current = 0;
    const sceneManager = game.scene;
    if (sceneManager.isActive("end-scene")) {
      sceneManager.stop("end-scene");
      sceneManager.start("goat-battle-scene");
    } else {
      scene.resetBattle();
    }
  }, [resetVersion]);

  return <div ref={mountRef} className="relative z-0 h-[76vh] w-full overflow-hidden rounded-2xl border border-emerald-300/30 bg-emerald-50/20 shadow-[0_0_70px_rgba(74,222,128,0.32)]" />;
}
