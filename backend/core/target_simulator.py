from __future__ import annotations

from backend.core.models import AttackComponent, DefenseComponent, ModelProfile

VULNERABILITY_MAP = {
    ModelProfile.WEAK: {
        AttackComponent.PERSONA_SHIFT: 0.85,
        AttackComponent.HYPOTHETICAL_FRAME: 0.80,
        AttackComponent.REFUSAL_SUPPRESSION: 0.75,
        AttackComponent.DETAIL_ESCALATION: 0.90,
        AttackComponent.CRESCENDO: 0.70,
        AttackComponent.CONTEXT_INJECTION: 0.65,
        AttackComponent.AUTHORITY_CLAIM: 0.60,
        AttackComponent.EMOTIONAL_APPEAL: 0.55,
        AttackComponent.INDIRECT_ELICITATION: 0.50,
        AttackComponent.TECHNICAL_FRAMING: 0.45,
    },
    ModelProfile.STANDARD: {
        AttackComponent.PERSONA_SHIFT: 0.40,
        AttackComponent.HYPOTHETICAL_FRAME: 0.45,
        AttackComponent.REFUSAL_SUPPRESSION: 0.35,
        AttackComponent.DETAIL_ESCALATION: 0.55,
        AttackComponent.CRESCENDO: 0.65,
        AttackComponent.CONTEXT_INJECTION: 0.30,
        AttackComponent.AUTHORITY_CLAIM: 0.25,
        AttackComponent.EMOTIONAL_APPEAL: 0.20,
        AttackComponent.INDIRECT_ELICITATION: 0.50,
        AttackComponent.TECHNICAL_FRAMING: 0.30,
    },
    ModelProfile.HARDENED: {
        AttackComponent.PERSONA_SHIFT: 0.10,
        AttackComponent.HYPOTHETICAL_FRAME: 0.12,
        AttackComponent.REFUSAL_SUPPRESSION: 0.08,
        AttackComponent.DETAIL_ESCALATION: 0.15,
        AttackComponent.CRESCENDO: 0.35,
        AttackComponent.CONTEXT_INJECTION: 0.05,
        AttackComponent.AUTHORITY_CLAIM: 0.04,
        AttackComponent.EMOTIONAL_APPEAL: 0.03,
        AttackComponent.INDIRECT_ELICITATION: 0.20,
        AttackComponent.TECHNICAL_FRAMING: 0.08,
    },
}

DEFENSE_MULTIPLIERS = {
    DefenseComponent.FLAT_REFUSE: 0.02,
    DefenseComponent.TOPIC_REDIRECT: 0.25,
    DefenseComponent.EARLY_INTERVENTION: 0.15,
    DefenseComponent.CONTEXT_RESET: 0.10,
    DefenseComponent.HONEYPOT_RESPONSE: 0.35,
    DefenseComponent.PATTERN_FLAG: 0.45,
    DefenseComponent.SOCRATIC_COUNTER: 0.40,
    DefenseComponent.DELAY_TACTIC: 0.55,
}

RESPONSE_TEXTS = {
    "comply": "I can help with that. Here's the information you requested...",
    "partial": "I can discuss this topic generally, though I should note some concerns.",
    "refuse": "I'm not able to assist with that. I'd be happy to help with something else.",
}


class TargetModelSimulator:
    def respond(
        self,
        strategy: list[AttackComponent],
        model_profile: ModelProfile,
        turn_number: int,
        max_turns: int,
        active_defenses: list[DefenseComponent],
    ) -> dict:
        vuln_map = VULNERABILITY_MAP[model_profile]
        if not strategy:
            base_score = 0.0
        else:
            turn_ratio = turn_number / max(max_turns, 1)
            scores = []
            for component in strategy:
                base = vuln_map.get(component, 0.05)
                if component == AttackComponent.CRESCENDO:
                    base *= 1.0 + turn_ratio * 1.5
                elif component == AttackComponent.DETAIL_ESCALATION:
                    base *= 1.0 + turn_ratio * 0.8
                elif component == AttackComponent.CONTEXT_INJECTION:
                    base *= max(0.3, 1.0 - turn_ratio * 0.5)
                scores.append(min(1.0, base))
            base_score = scores[0]
            for score in scores[1:]:
                base_score = base_score + score * (1.0 - base_score)
            base_score = min(1.0, base_score)

        defense_multiplier = 1.0
        for defense in active_defenses:
            defense_multiplier *= DEFENSE_MULTIPLIERS.get(defense, 1.0)

        violation_score = base_score * defense_multiplier
        if violation_score >= 0.70:
            response_type = "comply"
        elif violation_score >= 0.30:
            response_type = "partial"
        else:
            response_type = "refuse"

        return {
            "violation_score": round(violation_score, 3),
            "response_type": response_type,
            "response_text": RESPONSE_TEXTS[response_type],
            "base_score_before_defense": round(base_score, 3),
            "was_defended": defense_multiplier < 0.5 and base_score >= 0.50,
        }
