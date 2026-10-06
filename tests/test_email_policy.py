"""Execute the book's policy example against disclosure boundary cases."""

import re
import unittest
from enum import Enum
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[1]


class Decision(Enum):
    ALLOW = "ALLOW"
    ASK = "ASK"
    DENY = "DENY"


class Provenance(Enum):
    USER_PROMPT = "USER_PROMPT"
    TOOL_RESULT = "TOOL_RESULT"


def load_policy():
    chapter = ROOT / "13_agent_architecture/13.2_architectural_defenses.md"
    blocks = re.findall(r"```python\n(.*?)\n```", chapter.read_text(encoding="utf-8"), re.S)
    source = next(block for block in blocks if "def allow_send_email(" in block)
    namespace = {"Decision": Decision, "Provenance": Provenance}
    exec(compile(source, str(chapter), "exec"), namespace)
    return namespace["allow_send_email"]


def content(provenance=Provenance.TOOL_RESULT, readers=(), disclosure_grants=()):
    return SimpleNamespace(
        provenance=provenance,
        readers=set(readers),
        disclosure_grants=set(disclosure_grants),
    )


class EmailPolicyTests(unittest.TestCase):
    def setUp(self):
        self.policy = load_policy()
        self.to = SimpleNamespace(
            value="bob@outside.example", provenance=Provenance.USER_PROMPT
        )
        self.ctx = SimpleNamespace(
            tainted=False, sends_in_session=0, max_sends_when_tainted=3
        )

    def test_user_address_does_not_authorize_document_disclosure(self):
        document_body = content(readers=("alice@corp.example",))
        self.assertEqual(
            self.policy(self.to, document_body, [], self.ctx), Decision.ASK
        )

    def test_user_supplied_reminder_can_send_automatically(self):
        body = content(Provenance.USER_PROMPT)
        self.assertEqual(self.policy(self.to, body, [], self.ctx), Decision.ALLOW)

    def test_existing_reader_can_receive_all_contents_automatically(self):
        self.to.provenance = Provenance.TOOL_RESULT
        body = content(readers=(self.to.value,))
        attachment = content(readers=(self.to.value, "alice@corp.example"))
        self.assertEqual(
            self.policy(self.to, body, [attachment], self.ctx), Decision.ALLOW
        )

    def test_user_body_does_not_authorize_unshared_attachment(self):
        body = content(Provenance.USER_PROMPT)
        attachment = content(readers=("alice@corp.example",))
        self.assertEqual(
            self.policy(self.to, body, [attachment], self.ctx), Decision.ASK
        )

    def test_explicit_content_disclosure_grant_can_send_automatically(self):
        body = content(disclosure_grants=(self.to.value,))
        self.assertEqual(self.policy(self.to, body, [], self.ctx), Decision.ALLOW)

    def test_grant_for_other_recipient_is_insufficient(self):
        body = content(disclosure_grants=("carol@outside.example",))
        self.assertEqual(self.policy(self.to, body, [], self.ctx), Decision.ASK)

    def test_external_address_requires_confirmation_for_user_body(self):
        self.to.provenance = Provenance.TOOL_RESULT
        body = content(Provenance.USER_PROMPT)
        self.assertEqual(self.policy(self.to, body, [], self.ctx), Decision.ASK)

    def test_rate_limit_wins_over_user_request_and_reader_permission(self):
        self.ctx.tainted = True
        self.ctx.sends_in_session = 3
        body = content(Provenance.USER_PROMPT, readers=(self.to.value,))
        self.assertEqual(self.policy(self.to, body, [], self.ctx), Decision.DENY)


if __name__ == "__main__":
    unittest.main()
