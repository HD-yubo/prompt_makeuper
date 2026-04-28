import argparse
import asyncio
import json
import sys
from pathlib import Path

from app.services.llm_client import LLMClient
from app.services.optimizer import PromptOptimizer
from app.services.skill_manager import SkillManager


def build_optimizer() -> PromptOptimizer:
    return PromptOptimizer(LLMClient(), SkillManager(Path("app/skills")))


def list_skills() -> list[tuple[str, str]]:
    manager = SkillManager(Path("app/skills"))
    return [
        (skill.name, skill.description)
        for skill in manager.metadata.values()
    ]


def format_skill_list(skills: list[tuple[str, str]]) -> list[str]:
    return [f"{name}: {description}" for name, description in skills]


def build_help_description() -> str:
    skills_text = "\n".join(format_skill_list(list_skills()))
    return f"Optimize prompts from the command line\n\nAvailable skills:\n{skills_text}"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=build_help_description(),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("prompt", nargs="?", help="Prompt text to optimize")
    parser.add_argument("--file", dest="file_path", help="Read the prompt from a file")
    parser.add_argument(
        "--output-type",
        choices=["markdown", "xml"],
        default="markdown",
        help="Output format for the optimized prompt",
    )
    parser.add_argument("--list-skills", action="store_true", help="List available skills and exit")
    parser.add_argument("--skill", help="Manually select a skill and skip automatic skill selection")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Print full JSON result")
    return parser.parse_args(argv)


def read_prompt(args: argparse.Namespace) -> str:
    if args.prompt:
        return args.prompt.strip()

    if args.file_path:
        return Path(args.file_path).read_text(encoding="utf-8").strip()

    stdin_isatty = getattr(sys.stdin, "isatty", None)
    if stdin_isatty is None or not stdin_isatty():
        return sys.stdin.read().strip()

    return ""


async def run(args: argparse.Namespace) -> int:
    if args.list_skills:
        for skill in format_skill_list(list_skills()):
            print(skill)
        return 0

    try:
        prompt = read_prompt(args)
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if not prompt:
        print("No input prompt provided", file=sys.stderr)
        return 1

    if args.skill:
        available_skills = [name for name, _ in list_skills()]
        if args.skill not in available_skills:
            print(
                f"Unknown skill: {args.skill}. Available skills: {', '.join(available_skills)}",
                file=sys.stderr,
            )
            return 1

    try:
        result = await build_optimizer().optimize(
            prompt,
            output_type=args.output_type,
            skill_name=args.skill,
        )
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if args.json_output:
        print(
            json.dumps(
                {
                    "output_prompt": result["prompt"],
                    "skill_used": result["skill"],
                    "iterations": result["iterations"],
                },
                ensure_ascii=False,
            )
        )
    else:
        print(result["prompt"])

    return 0


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    return asyncio.run(run(args))


if __name__ == "__main__":
    raise SystemExit(main())
