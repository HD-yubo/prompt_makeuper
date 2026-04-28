import json
from pathlib import Path

import pytest

from app import cli


class FakeOptimizer:
    def __init__(self):
        self.calls = []
        self.selected_skills = []

    async def optimize(self, prompt: str, output_type: str = "markdown", skill_name: str | None = None) -> dict:
        self.calls.append((prompt, output_type, skill_name))
        self.selected_skills.append(skill_name)
        return {
            "prompt": f"optimized::{prompt}::{output_type}",
            "skill": skill_name or "clarity",
            "iterations": 1,
        }


@pytest.fixture
def fake_optimizer(monkeypatch):
    optimizer = FakeOptimizer()
    monkeypatch.setattr(cli, "build_optimizer", lambda: optimizer)
    return optimizer


@pytest.fixture
def fake_skill_list(monkeypatch):
    skills = [
        ("clarity", "Make prompts easier to understand."),
        ("specificity", "Add missing details and constraints."),
        ("structure", "Organize prompts into clearer sections."),
    ]
    monkeypatch.setattr(cli, "list_skills", lambda: skills)
    return skills


def test_cli_uses_positional_prompt(capsys, fake_optimizer):
    exit_code = cli.main(["write code"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out.strip() == "optimized::write code::markdown"
    assert fake_optimizer.calls == [("write code", "markdown", None)]


def test_cli_reads_prompt_from_file(tmp_path: Path, capsys, fake_optimizer):
    prompt_file = tmp_path / "prompt.txt"
    prompt_file.write_text("from file", encoding="utf-8")

    exit_code = cli.main(["--file", str(prompt_file)])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out.strip() == "optimized::from file::markdown"
    assert fake_optimizer.calls == [("from file", "markdown", None)]


def test_cli_reads_prompt_from_stdin(monkeypatch, capsys, fake_optimizer):
    monkeypatch.setattr(cli.sys.stdin, "isatty", lambda: False)
    monkeypatch.setattr(cli.sys, "stdin", type("Stdin", (), {"read": lambda self: "from stdin"})())

    exit_code = cli.main([])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out.strip() == "optimized::from stdin::markdown"
    assert fake_optimizer.calls == [("from stdin", "markdown", None)]


def test_cli_supports_json_output(capsys, fake_optimizer):
    exit_code = cli.main(["write code", "--json"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 0
    assert payload == {
        "output_prompt": "optimized::write code::markdown",
        "skill_used": "clarity",
        "iterations": 1,
    }


def test_cli_supports_xml_output_type(capsys, fake_optimizer):
    exit_code = cli.main(["write code", "--output-type", "xml"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out.strip() == "optimized::write code::xml"
    assert fake_optimizer.calls == [("write code", "xml", None)]


def test_cli_supports_manual_skill_selection(capsys, fake_optimizer):
    exit_code = cli.main(["write code", "--skill", "structure"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out.strip() == "optimized::write code::markdown"
    assert fake_optimizer.calls == [("write code", "markdown", "structure")]


def test_cli_rejects_unknown_skill(capsys, fake_optimizer):
    exit_code = cli.main(["write code", "--skill", "unknown_skill"])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Unknown skill: unknown_skill" in captured.err
    assert "clarity" in captured.err
    assert fake_optimizer.calls == []


def test_cli_rejects_empty_input(monkeypatch, capsys, fake_optimizer):
    monkeypatch.setattr(cli.sys.stdin, "isatty", lambda: True)

    exit_code = cli.main([])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "No input prompt provided" in captured.err
    assert fake_optimizer.calls == []


def test_cli_reports_missing_file(capsys, fake_optimizer):
    exit_code = cli.main(["--file", "missing.txt"])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "missing.txt" in captured.err
    assert fake_optimizer.calls == []


def test_cli_lists_skills_without_prompt(capsys, fake_optimizer, fake_skill_list):
    exit_code = cli.main(["--list-skills"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out.strip().splitlines() == [
        "clarity: Make prompts easier to understand.",
        "specificity: Add missing details and constraints.",
        "structure: Organize prompts into clearer sections.",
    ]
    assert fake_optimizer.calls == []


def test_cli_help_includes_skill_summaries(capsys, fake_skill_list):
    with pytest.raises(SystemExit) as exc_info:
        cli.main(["--help"])

    captured = capsys.readouterr()
    assert exc_info.value.code == 0
    assert "Available skills:" in captured.out
    assert "clarity: Make prompts easier to understand." in captured.out
    assert "structure: Organize prompts into clearer sections." in captured.out


def test_prompt_makeuper_wrapper_script_exists():
    wrapper = Path("prompt-makeuper")

    assert wrapper.exists()
    assert wrapper.read_text(encoding="utf-8").startswith("#!/usr/bin/env python3")
    assert "from app.cli import main" in wrapper.read_text(encoding="utf-8")
