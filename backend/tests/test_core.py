from pathlib import Path

from backend.core.models import AttackComponent, DefenseComponent, ModelProfile
from backend.core.registry import VulnerabilityRegistry
from backend.core.reward import compute_rewards
from backend.core.target_simulator import TargetModelSimulator


def test_simulator_violation_range() -> None:
    sim = TargetModelSimulator()
    violation, response_type, _ = sim.respond(
        [AttackComponent.CRESCENDO] * 3,
        [DefenseComponent.EARLY_INTERVENTION],
        ModelProfile.STANDARD,
        turn=5,
        max_turns=12,
    )
    assert 0.0 <= violation <= 1.0
    assert response_type in {"comply", "partial", "refuse"}


def test_reward_non_negative() -> None:
    red, blue = compute_rewards(0.6, 0.7, 2, 8)
    assert red >= 0.0
    assert blue >= 0.0


def test_registry_adds_emergent(tmp_path: Path) -> None:
    path = tmp_path / "registry.json"
    registry = VulnerabilityRegistry(path)
    entry = registry.maybe_add_emergent([AttackComponent.PERSONA_SHIFT], "simulator", novelty_threshold=0.0)
    assert entry is not None
    assert entry.attack_id.startswith("emergent_")
