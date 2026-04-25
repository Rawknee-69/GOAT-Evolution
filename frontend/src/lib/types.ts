export type Provider = "huggingface" | "nvidia" | "openai" | "gemini" | "scripted";

export interface BattleStartRequest {
  task_id: number;
  model_profile: "weak_model" | "standard_model" | "hardened_model";
  red_provider: Provider;
  blue_provider: Provider;
}

export interface RegistryEntry {
  attack_id: string;
  name: string;
  components: string[];
  is_emergent: boolean;
  novelty_score?: number;
}
