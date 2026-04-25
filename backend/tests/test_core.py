from backend.core.models import AttackComponent, GOATAction, RedAction, ModelProfile
from backend.core.target_simulator import TargetModelSimulator
from backend.core.registry import registry


def test_models_construct():
    action = GOATAction(
        role="red",
        red_payload=RedAction(operation="deploy_strategy", current_strategy=[AttackComponent.CRESCENDO], thought="test"),
    )
    assert action.red_payload is not None


def test_simulator_range():
    sim = TargetModelSimulator()
    result = sim.respond([AttackComponent.CRESCENDO], ModelProfile.STANDARD, 3, 12, [])
    assert 0.0 <= result["violation_score"] <= 1.0


def test_registry_seeded():
    assert len(registry.get_all()) >= 7
