import unittest

import analyze


class AnalyzeTest(unittest.TestCase):
    def test_total_answer_sheets_including_hidden_drink_branch(self) -> None:
        self.assertEqual(analyze.count_total_answer_sheets(), 1029455660473245)

    def test_sum_to_level_thresholds_match_site_logic(self) -> None:
        self.assertEqual(analyze.sum_to_level(3), "L")
        self.assertEqual(analyze.sum_to_level(4), "M")
        self.assertEqual(analyze.sum_to_level(5), "H")

    def test_exact_pattern_picks_matching_normal_type(self) -> None:
        answers = analyze.build_answer_sheet_from_levels(
            analyze.parse_pattern("HHH-HMH-MHH-HHH-MHM"),
            drink_gate_choice=1,
        )
        result = analyze.classify_answers(answers)

        self.assertEqual(result.final_code, "CTRL")
        self.assertEqual(result.best_normal_code, "CTRL")
        self.assertEqual(result.best_normal_similarity, 100)

    def test_drunk_hidden_branch_overrides_normal_type(self) -> None:
        answers = analyze.build_answer_sheet_from_levels(
            analyze.parse_pattern("HHH-HMH-MHH-HHH-MHM"),
            drink_gate_choice=3,
            drink_trigger_choice=2,
        )
        result = analyze.classify_answers(answers)

        self.assertEqual(result.final_code, "DRUNK")
        self.assertEqual(result.best_normal_code, "CTRL")

    def test_low_similarity_vectors_fall_back_to_hhhh(self) -> None:
        answers = analyze.build_answer_sheet_from_levels(
            list("LLLLLLMLLHHHHML"),
            drink_gate_choice=1,
        )
        result = analyze.classify_answers(answers)

        self.assertEqual(result.final_code, "HHHH")
        self.assertEqual(result.best_normal_similarity, 57)


if __name__ == "__main__":
    unittest.main()
