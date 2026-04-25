import redUnitUrl from "../../../assets/battle/sprites/red/stick-figure-red.svg";
import blueUnitUrl from "../../../assets/battle/sprites/blue/stick-figure-blue.svg";
import knifeProjectileUrl from "../../../assets/battle/effects/knife-projectile.svg";
import shieldBurstUrl from "../../../assets/battle/effects/shield-burst.svg";
import impactRingUrl from "../../../assets/battle/effects/impact-ring.svg";
import crateUrl from "../../../assets/battle/obstacles/obstacle-crate.svg";
import rockUrl from "../../../assets/battle/obstacles/obstacle-rock.svg";
import sunUrl from "../../../assets/battle/weather/weather-sun.svg";
import cloudUrl from "../../../assets/battle/weather/weather-cloud.svg";
import armorIconUrl from "../../../assets/battle/ui/icon-armor.svg";
import cooldownIconUrl from "../../../assets/battle/ui/icon-cooldown.svg";
import powerIconUrl from "../../../assets/battle/ui/icon-power.svg";
import warningIconUrl from "../../../assets/battle/ui/icon-warning.svg";
import victoryIconUrl from "../../../assets/battle/ui/icon-victory.svg";

export const battleAssetManifest = [
  { key: "unit-red", url: redUnitUrl },
  { key: "unit-blue", url: blueUnitUrl },
  { key: "proj-knife", url: knifeProjectileUrl },
  { key: "fx-shield", url: shieldBurstUrl },
  { key: "fx-impact", url: impactRingUrl },
  { key: "obstacle-crate", url: crateUrl },
  { key: "obstacle-rock", url: rockUrl },
  { key: "weather-sun", url: sunUrl },
  { key: "weather-cloud", url: cloudUrl },
  { key: "icon-armor", url: armorIconUrl },
  { key: "icon-cooldown", url: cooldownIconUrl },
  { key: "icon-power", url: powerIconUrl },
  { key: "icon-warning", url: warningIconUrl },
  { key: "icon-victory", url: victoryIconUrl },
] as const;

export type BattleTextureKey = (typeof battleAssetManifest)[number]["key"];
