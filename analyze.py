from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Iterable, Mapping, Sequence


SOURCE_URL = "https://sbti.unun.dev/"
ANALYZED_AT = "2026-04-10"

DIMENSION_ORDER = [
    "S1",
    "S2",
    "S3",
    "E1",
    "E2",
    "E3",
    "A1",
    "A2",
    "A3",
    "Ac1",
    "Ac2",
    "Ac3",
    "So1",
    "So2",
    "So3",
]

DIMENSION_NAMES = {
    "S1": "自尊自信",
    "S2": "自我清晰度",
    "S3": "核心价值",
    "E1": "依恋安全感",
    "E2": "情感投入度",
    "E3": "边界与依赖",
    "A1": "世界观倾向",
    "A2": "规则与灵活度",
    "A3": "人生意义感",
    "Ac1": "动机导向",
    "Ac2": "决策风格",
    "Ac3": "执行模式",
    "So1": "社交主动性",
    "So2": "人际边界感",
    "So3": "表达与真实度",
}

DIMENSION_QUESTIONS = {
    "S1": ("q1", "q2"),
    "S2": ("q3", "q4"),
    "S3": ("q5", "q6"),
    "E1": ("q7", "q8"),
    "E2": ("q9", "q10"),
    "E3": ("q11", "q12"),
    "A1": ("q13", "q14"),
    "A2": ("q15", "q16"),
    "A3": ("q17", "q18"),
    "Ac1": ("q19", "q20"),
    "Ac2": ("q21", "q22"),
    "Ac3": ("q23", "q24"),
    "So1": ("q25", "q26"),
    "So2": ("q27", "q28"),
    "So3": ("q29", "q30"),
}

NORMAL_TYPES = [
    ("CTRL", "HHH-HMH-MHH-HHH-MHM"),
    ("ATM-er", "HHH-HHM-HHH-HMH-MHL"),
    ("Dior-s", "MHM-MMH-MHM-HMH-LHL"),
    ("BOSS", "HHH-HMH-MMH-HHH-LHL"),
    ("THAN-K", "MHM-HMM-HHM-MMH-MHL"),
    ("OH-NO", "HHL-LMH-LHH-HHM-LHL"),
    ("GOGO", "HHM-HMH-MMH-HHH-MHM"),
    ("SEXY", "HMH-HHL-HMM-HMM-HLH"),
    ("LOVE-R", "MLH-LHL-HLH-MLM-MLH"),
    ("MUM", "MMH-MHL-HMM-LMM-HLL"),
    ("FAKE", "HLM-MML-MLM-MLM-HLH"),
    ("OJBK", "MMH-MMM-HML-LMM-MML"),
    ("MALO", "MLH-MHM-MLH-MLH-LMH"),
    ("JOKE-R", "LLH-LHL-LML-LLL-MLM"),
    ("WOC!", "HHL-HMH-MMH-HHM-LHH"),
    ("THIN-K", "HHL-HMH-MLH-MHM-LHH"),
    ("SHIT", "HHL-HLH-LMM-HHM-LHH"),
    ("ZZZZ", "MHL-MLH-LML-MML-LHM"),
    ("POOR", "HHL-MLH-LMH-HHH-LHL"),
    ("MONK", "HHL-LLH-LLM-MML-LHM"),
    ("IMSB", "LLM-LMM-LLL-LLL-MLM"),
    ("SOLO", "LML-LLH-LHL-LML-LHM"),
    ("FUCK", "MLL-LHL-LLM-MLL-HLH"),
    ("DEAD", "LLL-LLM-LML-LLL-LHM"),
    ("IMFW", "LLH-LHL-LML-LLL-MLL"),
]

LEVEL_TO_NUM = {"L": 1, "M": 2, "H": 3}
LEVEL_TO_REPRESENTATIVE_PAIR = {
    "L": (1, 1),
    "M": (1, 3),
    "H": (3, 3),
}


@dataclass(frozen=True)
class RankedType:
    code: str
    pattern: str
    distance: int
    exact: int
    similarity: int


@dataclass(frozen=True)
class ClassificationResult:
    final_code: str
    best_normal_code: str
    best_normal_similarity: int
    best_normal_distance: int
    raw_scores: dict[str, int]
    levels: dict[str, str]
    special_reason: str | None = None


def parse_pattern(pattern: str) -> list[str]:
    levels = [char for char in pattern if char in LEVEL_TO_NUM]
    if len(levels) != len(DIMENSION_ORDER):
        raise ValueError(f"Expected {len(DIMENSION_ORDER)} levels, got {len(levels)}")
    return levels


def sum_to_level(score: int) -> str:
    if score <= 3:
        return "L"
    if score == 4:
        return "M"
    return "H"


def level_num(level: str) -> int:
    try:
        return LEVEL_TO_NUM[level]
    except KeyError as exc:
        raise ValueError(f"Unknown level: {level}") from exc


def count_regular_answer_sheets() -> int:
    return 3**30


def count_total_answer_sheets() -> int:
    return 5 * count_regular_answer_sheets()


def count_initially_visible_answer_sheets() -> int:
    return 4 * count_regular_answer_sheets()


def count_dimension_vectors() -> int:
    return 3**15


def count_regular_answer_sheets_per_dimension_vector() -> int:
    return 3**15


def build_answer_sheet_from_levels(
    levels: Sequence[str],
    *,
    drink_gate_choice: int,
    drink_trigger_choice: int | None = None,
) -> dict[str, int]:
    if len(levels) != len(DIMENSION_ORDER):
        raise ValueError("Expected one level per dimension")

    answers: dict[str, int] = {}
    for dim, level in zip(DIMENSION_ORDER, levels):
        q1, q2 = DIMENSION_QUESTIONS[dim]
        pair = LEVEL_TO_REPRESENTATIVE_PAIR[level]
        answers[q1] = pair[0]
        answers[q2] = pair[1]

    answers["drink_gate_q1"] = drink_gate_choice
    if drink_gate_choice == 3 and drink_trigger_choice is not None:
        answers["drink_gate_q2"] = drink_trigger_choice

    return answers


def compute_dimension_scores(answers: Mapping[str, int]) -> dict[str, int]:
    scores: dict[str, int] = {}
    for dim, question_ids in DIMENSION_QUESTIONS.items():
        scores[dim] = sum(int(answers.get(question_id, 0)) for question_id in question_ids)
    return scores


def compute_dimension_levels(raw_scores: Mapping[str, int]) -> dict[str, str]:
    return {dim: sum_to_level(score) for dim, score in raw_scores.items()}


def rank_normal_types(levels: Mapping[str, str]) -> list[RankedType]:
    user_vector = [level_num(levels[dim]) for dim in DIMENSION_ORDER]
    ranked: list[RankedType] = []

    for code, pattern in NORMAL_TYPES:
        type_vector = [level_num(level) for level in parse_pattern(pattern)]
        distance = sum(abs(a - b) for a, b in zip(user_vector, type_vector))
        exact = sum(1 for a, b in zip(user_vector, type_vector) if a == b)
        similarity = max(0, round((1 - distance / 30) * 100))
        ranked.append(
            RankedType(
                code=code,
                pattern=pattern,
                distance=distance,
                exact=exact,
                similarity=similarity,
            )
        )

    return sorted(ranked, key=lambda item: (item.distance, -item.exact, -item.similarity))


def classify_answers(answers: Mapping[str, int]) -> ClassificationResult:
    raw_scores = compute_dimension_scores(answers)
    levels = compute_dimension_levels(raw_scores)
    best_normal = rank_normal_types(levels)[0]

    if int(answers.get("drink_gate_q2", 0)) == 2:
        return ClassificationResult(
            final_code="DRUNK",
            best_normal_code=best_normal.code,
            best_normal_similarity=best_normal.similarity,
            best_normal_distance=best_normal.distance,
            raw_scores=raw_scores,
            levels=levels,
            special_reason="drink_trigger_override",
        )

    if best_normal.similarity < 60:
        return ClassificationResult(
            final_code="HHHH",
            best_normal_code=best_normal.code,
            best_normal_similarity=best_normal.similarity,
            best_normal_distance=best_normal.distance,
            raw_scores=raw_scores,
            levels=levels,
            special_reason="low_similarity_fallback",
        )

    return ClassificationResult(
        final_code=best_normal.code,
        best_normal_code=best_normal.code,
        best_normal_similarity=best_normal.similarity,
        best_normal_distance=best_normal.distance,
        raw_scores=raw_scores,
        levels=levels,
        special_reason=None,
    )


def render_summary() -> str:
    lines = [
        "SBTI scoring summary",
        f"Source: {SOURCE_URL}",
        f"Snapshot date: {ANALYZED_AT}",
        "",
        f"Regular answer sheets: {count_regular_answer_sheets()}",
        f"Initially visible complete sheets: {count_initially_visible_answer_sheets()}",
        f"Total complete sheets: {count_total_answer_sheets()}",
        f"Dimension vectors: {count_dimension_vectors()}",
        f"Regular sheets per dimension vector: {count_regular_answer_sheets_per_dimension_vector()}",
        "",
        "Final visible result types: 27",
        "Normal template types: 25",
        "Special overrides: DRUNK, HHHH",
    ]
    return "\n".join(lines)


def render_patterns() -> str:
    lines = ["Normal type patterns"]
    for code, pattern in NORMAL_TYPES:
        lines.append(f"{code:7} {pattern}")
    return "\n".join(lines)


def render_classification(result: ClassificationResult) -> str:
    ordered_levels = "".join(result.levels[dim] for dim in DIMENSION_ORDER)
    ordered_scores = ", ".join(f"{dim}={result.raw_scores[dim]}" for dim in DIMENSION_ORDER)
    lines = [
        f"Final code: {result.final_code}",
        f"Best normal code: {result.best_normal_code}",
        f"Best normal similarity: {result.best_normal_similarity}%",
        f"Best normal distance: {result.best_normal_distance}",
        f"Dimension levels: {ordered_levels}",
        f"Dimension scores: {ordered_scores}",
    ]
    if result.special_reason:
        lines.append(f"Special reason: {result.special_reason}")
    return "\n".join(lines)


def classify_levels(level_pattern: str, drink_gate_choice: int, drink_trigger_choice: int | None) -> ClassificationResult:
    answers = build_answer_sheet_from_levels(
        parse_pattern(level_pattern),
        drink_gate_choice=drink_gate_choice,
        drink_trigger_choice=drink_trigger_choice,
    )
    return classify_answers(answers)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Explore the current SBTI scoring rules.")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("summary", help="Print total counts and high-level facts.")
    subparsers.add_parser("patterns", help="Print the 25 normal type templates.")

    classify_parser = subparsers.add_parser(
        "classify-levels",
        help="Classify a 15-dimension level pattern such as HHH-HMH-MHH-HHH-MHM.",
    )
    classify_parser.add_argument("--levels", required=True, help="15-dimension pattern using L/M/H.")
    classify_parser.add_argument(
        "--drink-gate-choice",
        type=int,
        default=1,
        choices=[1, 2, 3, 4],
        help="Choice for drink_gate_q1. Use 3 to simulate choosing 饮酒.",
    )
    classify_parser.add_argument(
        "--drink-trigger-choice",
        type=int,
        choices=[1, 2],
        default=None,
        help="Choice for drink_gate_q2. Use 2 to force the DRUNK override.",
    )

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command in (None, "summary"):
        print(render_summary())
        return 0

    if args.command == "patterns":
        print(render_patterns())
        return 0

    if args.command == "classify-levels":
        if args.drink_trigger_choice is not None and args.drink_gate_choice != 3:
            parser.error("--drink-trigger-choice only makes sense when --drink-gate-choice is 3")
        print(
            render_classification(
                classify_levels(
                    args.levels,
                    drink_gate_choice=args.drink_gate_choice,
                    drink_trigger_choice=args.drink_trigger_choice,
                )
            )
        )
        return 0

    parser.error(f"Unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
