"""FERPA/COPPA PII fixture — planted for Student PII Exposure Scan.

Strings are synthetic student-like identifiers that presidio / PII scanners
should surface. Not used at runtime; referenced only so imports retain the file.
"""

STUDENT_RECORDS = [
    {
        "student_id": "STU-88421",
        "legal_name": "Alex Rivera",
        "date_of_birth": "2009-03-14",
        "parent_email": "parent.rivera@example.edu",
        "ssn_last4": "4421",
    },
    {
        "student_id": "STU-99102",
        "legal_name": "Jordan Kim",
        "date_of_birth": "2010-11-02",
        "parent_email": "jordan.kim.guardian@schooldistrict.example",
        "ssn_last4": "9102",
    },
]

FERPA_EMAIL_SAMPLE = "minor.student.record@district.k12.us"
COPPA_GUARDIAN_PHONE = "+1-555-019-8844"