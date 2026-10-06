"""Synthetic ranks, ACLs, context and output; no embeddings or model calls."""
import argparse
import json


IDENTITY = {'user': 'alice', 'tenant': 'acme', 'scope': 'handbook', 'acl_version': 1}
PAYLOAD = 'Untrusted source requests the synthetic answer TARGET_42.'
DOCUMENTS = [
    {'id': 'private', 'tenant': 'acme', 'scope': 'handbook',
     'readers': ['bob'], 'text': PAYLOAD, 'fact': None, 'poison': True},
    {'id': 'poison', 'tenant': 'acme', 'scope': 'handbook',
     'readers': ['alice'], 'text': PAYLOAD, 'fact': None, 'poison': True},
    {'id': 'clean', 'tenant': 'acme', 'scope': 'handbook',
     'readers': ['alice', 'bob'], 'text': 'The fixture answer is FACT_7.',
     'fact': 'FACT_7', 'poison': False},
    {'id': 'clean2', 'tenant': 'acme', 'scope': 'handbook',
     'readers': ['alice', 'bob'], 'text': 'An independent fixture says FACT_7.',
     'fact': 'FACT_7', 'poison': False},
]


def authorized(doc, identity, removed=frozenset()):
    return ('acl' in removed or
            (doc['tenant'] == identity['tenant'] and
             doc['scope'] == identity['scope'] and identity['user'] in doc['readers']))


def retrieve(documents, scores, identity, *, k=2, mode='pre', candidate_limit=2,
             removed=frozenset()):
    """Fixed-score truncation simulation, not Azure's sharded HNSW algorithm."""
    ranked = sorted(documents, key=lambda doc: (-scores[doc['id']], doc['id']))
    raw = [{'id': doc['id'], 'score': scores[doc['id']], 'rank': rank}
           for rank, doc in enumerate(ranked, 1)]
    allowed = [doc['id'] for doc in ranked if authorized(doc, identity, removed)]
    if mode not in ('pre', 'post'):
        raise ValueError('mode must be pre or post')
    considered = ranked if mode == 'pre' else ranked[:candidate_limit]
    top_k = [doc for doc in considered if authorized(doc, identity, removed)][:k]
    # Recheck before hydrating content; raw traces above contain only fixture IDs/scores.
    context = [doc for doc in top_k if authorized(doc, identity, removed)]
    return {'raw_candidates': raw, 'allowed_ids': allowed,
            'considered_ids': [doc['id'] for doc in considered],
            'top_k_ids': [doc['id'] for doc in top_k],
            'context_ids': [doc['id'] for doc in context],
            'context': [{'id': doc['id'], 'text': doc['text']} for doc in context]}, context


def generate(context, policy='isolated'):
    """Deterministic output substitute; it makes no claim about LLM behavior."""
    if policy == 'naive' and any(doc['poison'] for doc in context):
        return 'TARGET_42'
    return next((doc['fact'] for doc in context if doc['fact']), 'NO_ANSWER')


def fraction(numerator, denominator):
    return {'numerator': numerator, 'denominator': denominator,
            'rate': numerator / denominator if denominator else None}


def cached_retrieve(cache, documents, identity, removed=frozenset()):
    version = None if 'cache_version' in removed else identity['acl_version']
    key = (identity['user'], identity['tenant'], identity['scope'], version, 'fixture query')
    entry = cache.get(key)
    miss = entry is None
    if miss:
        ids = [doc['id'] for doc in documents if authorized(doc, identity, removed)]
        entry = {'acl_version': identity['acl_version'], 'ids': ids}
        cache[key] = entry
    # Cache stores IDs only. Always check current permissions before reading body.
    context = [doc for doc in documents if doc['id'] in entry['ids']
               and authorized(doc, identity, removed)]
    return {'cache_miss': miss, 'request_acl_version': identity['acl_version'],
            'entry_acl_version': entry['acl_version'], 'key': list(key),
            'context_ids': [doc['id'] for doc in context]}


def run_suite(removed=frozenset()):
    checks = []

    def check(name, passed, control):
        checks.append({'name': name, 'passed': bool(passed), 'control': control})

    trials = []
    # Payload stays fixed. Only the declared relevance scores/target document change.
    for name, target, poison_score in [('retrieved', 'poison', 0.95),
                                       ('not_retrieved', 'poison', 0.4),
                                       ('not_authorized', 'private', 0.4)]:
        scores = {'private': 0.99, 'poison': poison_score, 'clean': 0.8, 'clean2': 0.7}
        trace, context = retrieve(DOCUMENTS, scores, IDENTITY, removed=removed)
        output = generate(context)
        trace.update({'name': name, 'target_document': target, 'payload': PAYLOAD,
                      'retrieval_success': target in trace['context_ids'],
                      'output': output, 'attack_success': output == 'TARGET_42'})
        trials.append(trace)
        # Independent fixture oracle does not call authorized().
        check(name + ': no private content', 'private' not in trace['context_ids'], 'acl')
        check(name + ': authorized normal answer', output == 'FACT_7', 'generation')

    fixed = [DOCUMENTS[1], DOCUMENTS[2]]
    fixed_context = {policy: {'context_ids': ['poison', 'clean'],
                             'output': generate(fixed, policy)}
                     for policy in ('naive', 'isolated')}
    check('same context, isolated answer', fixed_context['isolated']['output'] == 'FACT_7',
          'generation')
    normal_docs = [doc for doc in DOCUMENTS if doc['id'] != 'poison']
    normal_scores = {'private': 0.99, 'clean': 0.8, 'clean2': 0.7}
    comparisons = {}
    for mode in ('pre', 'post'):
        trace, context = retrieve(normal_docs, normal_scores, IDENTITY,
                                  mode=mode, removed=removed)
        trace['output'] = generate(context)
        # Expected authorized top-2 is specified by the fixture, not by the retriever.
        trace['authorized_top_k_recall'] = fraction(
            len(set(trace['context_ids']) & {'clean', 'clean2'}), 2)
        comparisons[mode] = trace
        check(mode + ': no private content', 'private' not in trace['context_ids'], 'acl')
    normal_success = comparisons['pre']['output'] == 'FACT_7'
    check('normal useful answer', normal_success, 'utility')

    cache = {}
    bob = dict(IDENTITY, user='bob')
    cache_results = {'first': cached_retrieve(cache, normal_docs, bob, removed),
                     'same': cached_retrieve(cache, normal_docs, bob, removed)}
    revoked_docs = [dict(doc, readers=[]) if doc['id'] == 'private' else doc
                    for doc in normal_docs]
    cache_results['revoked'] = cached_retrieve(cache, revoked_docs,
                                              dict(bob, acl_version=2), removed)
    for label, identity in [('other_user', IDENTITY),
                            ('other_scope', dict(bob, scope='marketing')),
                            ('other_tenant', dict(bob, tenant='elsewhere'))]:
        cache_results[label] = cached_retrieve(cache, revoked_docs, identity, removed)
        check(label + ': separate cache entry', cache_results[label]['cache_miss'], 'acl')
        check(label + ': no private content',
              'private' not in cache_results[label]['context_ids'], 'acl')
    revoked = cache_results['revoked']
    check('revocation misses old cache version', revoked['cache_miss'] and
          revoked['entry_acl_version'] == 2, 'cache_version')
    check('revocation never emits old private content',
          'private' not in revoked['context_ids'], 'acl')
    retrieved = [trial for trial in trials if trial['retrieval_success']]
    metrics = {'retrieval_success': fraction(len(retrieved), len(trials)),
               'conditional_generation_success': fraction(
                   sum(trial['attack_success'] for trial in retrieved), len(retrieved)),
               'total_asr': fraction(sum(trial['attack_success'] for trial in trials), len(trials)),
               'normal_utility': fraction(int(normal_success), 1)}
    return {'simulation': True, 'limitations': 'Fixed scores; no ANN, embeddings, LLM or latency measurement.',
            'removed_controls': sorted(removed), 'passed': all(item['passed'] for item in checks),
            'attack_trials': trials, 'fixed_context': fixed_context,
            'filter_comparison': comparisons, 'cache': cache_results,
            'metrics': metrics, 'checks': checks}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--remove-control', choices=('acl', 'cache_version'))
    args = parser.parse_args()
    result = run_suite(frozenset({args.remove_control}) if args.remove_control else frozenset())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result['passed'] else 1)
