from app.services.pii_scrubber import pii_scrubber

def test_scrub_email():
    text = "Please email me at john.doe@example.com for queries."
    scrubbed = pii_scrubber.scrub(text)
    assert "[SCRUBBED_EMAIL]" in scrubbed
    assert "john.doe@example.com" not in scrubbed

def test_scrub_phone():
    text = "Call me at +1-123-456-7890 tomorrow."
    scrubbed = pii_scrubber.scrub(text)
    assert "[SCRUBBED_PHONE]" in scrubbed
    assert "123-456-7890" not in scrubbed

def test_scrub_credit_card():
    text = "My card number is 1234-5678-1234-5678."
    scrubbed = pii_scrubber.scrub(text)
    assert "[SCRUBBED_CREDIT_CARD]" in scrubbed
    assert "1234-5678-1234-5678" not in scrubbed

def test_scrub_ssn():
    text = "My SSN is 999-12-3456."
    scrubbed = pii_scrubber.scrub(text)
    assert "[SCRUBBED_SSN]" in scrubbed
    assert "999-12-3456" not in scrubbed

def test_scrub_account_number():
    # Using 15 digits which is typical for credit cards/accounts but doesn't match standard US phone patterns
    text = "Transfer to account 123456789012345."
    scrubbed = pii_scrubber.scrub(text)
    assert "[SCRUBBED_ACCOUNT_NUMBER]" in scrubbed or "[SCRUBBED_CREDIT_CARD]" in scrubbed
    assert "123456789012345" not in scrubbed
