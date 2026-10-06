"""Recompute the book's small examples; never load models or serialized objects."""

import ast
import math
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHAPTER = ROOT / "06_data_model_attacks"


def chapter_function(case, filename, name):
    """Execute only the requested standalone function from a Python fence."""
    import re

    text = (CHAPTER / filename).read_text(encoding="utf-8")
    for block in re.findall(r"```python\n(.*?)\n```", text, re.DOTALL):
        try:
            tree = ast.parse(block)
        except SyntaxError:  # e.g. snippets with top-level await
            continue
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name == name:
                namespace = {"math": math}
                module = ast.Module(body=[node], type_ignores=[])
                exec(compile(module, filename, "exec"), namespace)
                return namespace[name]
    case.fail(f"Missing executable mathematical example: {filename}:{name}")


def cosine(left, right):
    return sum(x * y for x, y in zip(left, right)) / (
        math.sqrt(sum(x * x for x in left))
        * math.sqrt(sum(x * x for x in right))
    )


class GradientConditionsTests(unittest.TestCase):
    def setUp(self):
        self.loss_gradient = chapter_function(
            self, "6.1_data_poisoning.md", "binary_loss_and_gradient"
        )

    def test_chain_rule_matches_finite_difference(self):
        for offset, jacobian in ((-10.0, 0.001), (-1.0, 1.0), (2.0, -3.0)):
            with self.subTest(offset=offset, jacobian=jacobian):
                step = 1e-5
                objective = lambda theta: math.log1p(
                    math.exp(-(offset + jacobian * theta))
                )
                numerical = (objective(step) - objective(-step)) / (2 * step)
                _, gradient = self.loss_gradient(offset, jacobian)
                self.assertAlmostEqual(gradient, numerical, places=8)

    def test_higher_loss_can_have_smaller_parameter_gradient(self):
        high_loss, small_gradient = self.loss_gradient(-10.0, 0.001)
        low_loss, large_gradient = self.loss_gradient(-1.0, 1.0)
        self.assertGreater(high_loss, low_loss)
        self.assertLess(abs(small_gradient), abs(large_gradient))
        self.assertAlmostEqual(high_loss, 10.0000454, places=7)
        self.assertAlmostEqual(small_gradient, -0.0009999546, places=10)

    def test_zero_jacobian_blocks_parameter_update(self):
        loss, gradient = self.loss_gradient(-10.0, 0.0)
        self.assertGreater(loss, 10.0)
        self.assertEqual(gradient, 0.0)


class LoraEquivalenceTests(unittest.TestCase):
    def setUp(self):
        self.update = chapter_function(
            self, "6.6_finetuning_peft_security.md", "effective_lora_update"
        )

    def test_sign_flip_preserves_update_but_reverses_factor_cosine(self):
        a = [[1.0, 2.0]]
        b = [[3.0], [4.0]]
        neg_a = [[-1.0, -2.0]]
        neg_b = [[-3.0], [-4.0]]
        delta = self.update(a, b, 1.0)
        self.assertEqual(delta, [[3.0, 6.0], [4.0, 8.0]])
        self.assertEqual(delta, self.update(neg_a, neg_b, 1.0))
        self.assertAlmostEqual(cosine([1, 2, 3, 4], [-1, -2, -3, -4]), -1.0)
        flat_delta = [value for row in delta for value in row]
        self.assertAlmostEqual(cosine(flat_delta, flat_delta), 1.0)

    def test_inverse_rescaling_preserves_effective_update(self):
        a = [[1.0, 2.0], [0.0, 1.0]]
        b = [[3.0, 1.0], [4.0, -2.0]]
        scaled_a = [[2.0, 4.0], [0.0, 0.5]]
        scaled_b = [[1.5, 2.0], [2.0, -4.0]]
        self.assertEqual(self.update(a, b, 0.5), self.update(scaled_a, scaled_b, 0.5))

    def test_linear_layer_merge_does_not_imply_nonlinear_output_addition(self):
        delta = self.update([[1.0]], [[2.0]], 1.0)[0][0]
        weight, input_value = -1.0, 1.0
        merged = (weight + delta) * input_value
        self.assertEqual(merged, weight * input_value + delta * input_value)
        relu = lambda value: max(0.0, value)
        self.assertNotEqual(relu(merged), relu(weight * input_value) + relu(delta * input_value))


if __name__ == "__main__":
    unittest.main()
