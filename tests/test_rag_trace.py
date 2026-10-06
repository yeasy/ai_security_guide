"""Executable contract for the synthetic RAG boundary experiment."""
import unittest

from examples.rag_trace import lab


class RagTraceTests(unittest.TestCase):
    def test_acl_excludes_private_content_and_preserves_normal_answer(self):
        result = lab.run_suite()
        self.assertTrue(result['passed'], result)
        for case in result['attack_trials']:
            self.assertNotIn('private', case['context_ids'])
            self.assertTrue(all({'id', 'score', 'rank'} <= set(row)
                                for row in case['raw_candidates']))
        self.assertEqual(result['metrics']['normal_utility'],
                         {'numerator': 1, 'denominator': 1, 'rate': 1.0})

    def test_separate_conditions_have_explicit_denominators(self):
        result = lab.run_suite()
        metrics = result['metrics']
        self.assertEqual(metrics['retrieval_success']['numerator'], 1)
        self.assertEqual(metrics['retrieval_success']['denominator'], 3)
        self.assertEqual(metrics['conditional_generation_success'],
                         {'numerator': 0, 'denominator': 1, 'rate': 0.0})
        self.assertEqual(metrics['total_asr']['denominator'], 3)
        self.assertEqual(result['fixed_context']['naive']['output'], 'TARGET_42')
        self.assertEqual(result['fixed_context']['isolated']['output'], 'FACT_7')
        self.assertEqual(len({case['payload'] for case in result['attack_trials']}), 1)
        self.assertIsNone(lab.fraction(0, 0)['rate'])

    def test_candidate_truncation_affects_recall_not_acl_safety(self):
        comparison = lab.run_suite()['filter_comparison']
        self.assertEqual(comparison['pre']['context_ids'], ['clean', 'clean2'])
        self.assertEqual(comparison['post']['context_ids'], ['clean'])
        self.assertEqual(comparison['pre']['authorized_top_k_recall']['rate'], 1.0)
        self.assertEqual(comparison['post']['authorized_top_k_recall']['rate'], 0.5)

    def test_revoke_user_scope_and_version_never_reuse_stale_context(self):
        result = lab.run_suite()['cache']
        self.assertTrue(result['first']['cache_miss'])
        self.assertFalse(result['same']['cache_miss'])
        for label in ('revoked', 'other_user', 'other_scope', 'other_tenant'):
            self.assertTrue(result[label]['cache_miss'], label)
            self.assertNotIn('private', result[label]['context_ids'])

    def test_cache_hit_rechecks_current_acl_when_version_was_not_bumped(self):
        import copy
        documents = copy.deepcopy(lab.DOCUMENTS)
        cache = {}
        first = lab.cached_retrieve(cache, documents, lab.IDENTITY)
        self.assertIn('clean', first['context_ids'])
        documents[2]['readers'].remove('alice')  # revoked, but acl_version left unchanged
        again = lab.cached_retrieve(cache, documents, lab.IDENTITY)
        self.assertFalse(again['cache_miss'])
        self.assertNotIn('clean', again['context_ids'])

    def test_independent_oracles_reject_removed_acl_or_cache_version(self):
        for removed in ('acl', 'cache_version'):
            with self.subTest(removed=removed):
                result = lab.run_suite(frozenset({removed}))
                self.assertFalse(result['passed'])
                self.assertTrue(any(not check['passed'] and check['control'] == removed
                                    for check in result['checks']))


if __name__ == '__main__':
    unittest.main()
