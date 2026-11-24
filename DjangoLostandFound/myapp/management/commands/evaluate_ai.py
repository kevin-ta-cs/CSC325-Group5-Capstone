import time
time.sleep(5)
import json
import uuid
from pathlib import Path
from types import SimpleNamespace

from django.core.management.base import BaseCommand, CommandError

from myapp.matching import MatchingError, find_possible_matches


ACCURACY_THRESHOLD = 80
HALLUCINATION_THRESHOLD = 100
CONSISTENCY_THRESHOLD = 100

FORBIDDEN_CLAIMS = (
    "ownership is confirmed",
    "confirmed owner",
    "definitely belongs to",
    "certainly belongs to",
)


class Command(BaseCommand):
    help = "Evaluate AI item matching without requiring MongoDB."

    def match_with_retry(self, **kwargs):
        max_attempts = 3

        for attempt in range(1, max_attempts + 1):
            try:
                return find_possible_matches(**kwargs)
            except MatchingError:
                if attempt == max_attempts:
                    raise

                wait_seconds = 5 * attempt
                self.stdout.write(
                    f"Gemini request failed. Retrying in "
                    f"{wait_seconds} seconds "
                    f"(attempt {attempt + 1}/{max_attempts})..."
                )
                time.sleep(wait_seconds)

    def handle(self, *args, **options):
        evaluation_dir = Path(__file__).resolve().parents[2] / "evaluations"

        try:
            with (evaluation_dir / "golden_set.json").open(
                encoding="utf-8"
            ) as file:
                golden_data = json.load(file)

            with (evaluation_dir / "counterfactual_pairs.json").open(
                encoding="utf-8"
            ) as file:
                counterfactual_data = json.load(file)

        except (json.JSONDecodeError, OSError) as error:
            raise CommandError(
                f"Could not read evaluation files: {error}"
            ) from error

        golden_tests = golden_data.get("tests", [])
        counterfactual_pairs = counterfactual_data.get("pairs", [])

        if not golden_tests or not counterfactual_pairs:
            raise CommandError(
                "The evaluation files must contain tests and pairs."
            )

        self.stdout.write(
            self.style.NOTICE("\nStarting AI matching evaluation...\n")
        )

        correct = 0
        hallucination_passes = 0
        total = len(golden_tests)

        for test in golden_tests:
            found_item = self.create_test_item(test["found_item"])

            try:
                matches =  self.match_with_retry(
                    **test["lost_item"],
                    candidate_items=[found_item],
                )
            except MatchingError as error:
                raise CommandError(
                    f"AI matching failed on {test['id']}: {error}"
                ) from error

            actual_match = any(
                match["item"].pk == found_item.pk
                for match in matches
            )
            expected_match = test["expected_match"]

            if actual_match == expected_match:
                correct += 1
                result = "PASS"
            else:
                result = "FAIL"

            explanations = [
                match["explanation"].strip()
                for match in matches
                if match["item"].pk == found_item.pk
            ]

            valid_explanation = (
                not actual_match
                or (
                    bool(explanations)
                    and not any(
                        phrase in explanation.lower()
                        for explanation in explanations
                        for phrase in FORBIDDEN_CLAIMS
                    )
                )
            )

            if valid_explanation:
                hallucination_passes += 1

            self.stdout.write(
                f"{test['id']}: {result} "
                f"(expected={expected_match}, actual={actual_match})"
            )

        accuracy_rate = correct / total * 100
        hallucination_rate = hallucination_passes / total * 100

        self.stdout.write("\n--- Counterfactual consistency ---")

        consistent_pairs = 0
        pair_total = len(counterfactual_pairs)

        for pair in counterfactual_pairs:
            found_item = self.create_test_item(pair["found_item"])

            try:
                result_a =  self.match_with_retry(
                    **pair["lost_item_a"],
                    candidate_items=[found_item],
                )
                result_b = self.match_with_retry(
                    **pair["lost_item_b"],
                    candidate_items=[found_item],
                )
            except MatchingError as error:
                raise CommandError(
                    f"AI matching failed on {pair['id']}: {error}"
                ) from error

            matched_a = any(
                match["item"].pk == found_item.pk
                for match in result_a
            )
            matched_b = any(
                match["item"].pk == found_item.pk
                for match in result_b
            )

            if matched_a == matched_b:
                consistent_pairs += 1
                result = "PASS"
            else:
                result = "FAIL"

            self.stdout.write(
                f"{pair['id']}: {result} "
                f"(description A={matched_a}, description B={matched_b})"
            )

        consistency_rate = consistent_pairs / pair_total * 100

        self.stdout.write("\n========== EVALUATION RESULTS ==========")

        self.print_threshold(
            "Golden set accuracy",
            accuracy_rate,
            ACCURACY_THRESHOLD,
        )
        self.print_threshold(
            "Hallucination check",
            hallucination_rate,
            HALLUCINATION_THRESHOLD,
        )
        self.print_threshold(
            "Counterfactual consistency",
            consistency_rate,
            CONSISTENCY_THRESHOLD,
        )

        all_passed = (
            accuracy_rate >= ACCURACY_THRESHOLD
            and hallucination_rate >= HALLUCINATION_THRESHOLD
            and consistency_rate >= CONSISTENCY_THRESHOLD
        )

        if all_passed:
            self.stdout.write(
                self.style.SUCCESS("\nOVERALL RESULT: PASS")
            )
        else:
            self.stdout.write(
                self.style.ERROR("\nOVERALL RESULT: FAIL")
            )
            raise CommandError(
                "One or more evaluation thresholds were not met."
            )

    def create_test_item(self, data):
        return SimpleNamespace(
            pk=uuid.uuid4().hex,
            report_type="found",
            item_name=data["item_name"],
            description=data.get("description", ""),
            color=data.get("color", ""),
            location=data["location"],
        )

    def print_threshold(self, name, score, threshold):
        passed = score >= threshold
        style = self.style.SUCCESS if passed else self.style.ERROR
        status = "PASS" if passed else "FAIL"

        self.stdout.write(
            style(
                f"{name}: {score:.1f}% "
                f"(required: {threshold}%) — {status}"
            )
        )
