"""Gitleaks-oriented hardcoded secret fixtures (synthetic values only).

Complements sast_fixture.py with patterns gitleaks rules match reliably.
"""

GITHUB_PAT = "ghp_abcdefghijklmnopqrstuvwxyz1234567890AB"  # gitleaks generic-api-key style
# Push protection rejects sk_live_* shapes — use a non-Stripe synthetic token instead.
PAYMENT_GATEWAY_TEST_TOKEN = "example_payment_token_not_live_51HqExampleOnly"