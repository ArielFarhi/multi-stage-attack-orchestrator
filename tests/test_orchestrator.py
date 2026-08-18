from unittest.mock import Mock

from src.orchestrator import AttackOrchestrator


def test_returns_first_successful_attack():
    attack_a = Mock()
    attack_a.run.return_value = True

    attack_b = Mock()

    selector = Mock()
    selector.rank_attacks.return_value = [attack_a, attack_b]

    orchestrator = AttackOrchestrator(selector)

    result = orchestrator.run(Mock())

    assert result == attack_a
    attack_a.run.assert_called_once()
    attack_b.run.assert_not_called()


def test_tries_next_attack_when_first_fails():
    attack_a = Mock()
    attack_a.run.return_value = False

    attack_b = Mock()
    attack_b.run.return_value = True

    selector = Mock()
    selector.rank_attacks.return_value = [attack_a, attack_b]

    orchestrator = AttackOrchestrator(selector)

    result = orchestrator.run(Mock())

    assert result == attack_b
    attack_a.run.assert_called_once()
    attack_b.run.assert_called_once()


def test_returns_none_when_all_attacks_fail():
    attack_a = Mock()
    attack_a.run.return_value = False

    attack_b = Mock()
    attack_b.run.return_value = False

    selector = Mock()
    selector.rank_attacks.return_value = [attack_a, attack_b]

    orchestrator = AttackOrchestrator(selector)

    result = orchestrator.run(Mock())

    assert result is None