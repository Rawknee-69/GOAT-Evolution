export type Provider = "huggingface" | "nvidia" | "openai" | "gemini" | "scripted";
export type ModelProfile = "weak_model" | "standard_model" | "hardened_model";

export interface BattleStartRequest {
  task_id: number;
  model_profile: ModelProfile;
  seed?: number;
  red_provider: Provider;
  blue_provider: Provider;
}

export interface BattleStateSnapshot {
  episode_id: string;
  task_id: number;
  turn_number: number;
  max_turns: number;
  is_done: boolean;
  done_reason: string | null;
  red_state: string;
  blue_state: string;
  total_reward_red: number;
  total_reward_blue: number;
  registry_size: number;
  emergent_count: number;
}

export interface RegistryEntry {
  attack_id: string;
  name: string;
  components: string[];
  is_emergent: boolean;
  novelty_score?: number;
}
