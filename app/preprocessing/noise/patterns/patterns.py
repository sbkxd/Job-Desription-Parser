"""Configurable regular expression patterns for job description noise filtering."""

import re

# Contact Information
EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
PHONE_PATTERN = re.compile(r"(?:\+?\d{1,3}[ -]?)?\(?\d{3}\)?[ -]?\d{3}[ -]?\d{4}")
URL_PATTERN = re.compile(
    r"https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*)"
)

# Social Media Links / Handles
SOCIAL_MEDIA_PATTERN = re.compile(
    r"(?:linkedin|github|facebook|twitter|instagram|youtube|slack)\.com/\S+",
    re.IGNORECASE,
)

# ATS Labels & Form Artifacts
ATS_FORM_PATTERNS = [
    re.compile(r"^this section auto-populates", re.IGNORECASE),
    re.compile(r"^select one of the following", re.IGNORECASE),
    re.compile(r"^internal use only", re.IGNORECASE),
    re.compile(r"^choose an option", re.IGNORECASE),
]

# Employment Metadata Labels
METADATA_LABELS = [
    re.compile(r"^employment type$", re.IGNORECASE),
    re.compile(r"^job function$", re.IGNORECASE),
    re.compile(r"^industries$", re.IGNORECASE),
    re.compile(r"^job category$", re.IGNORECASE),
    re.compile(r"^posting date$", re.IGNORECASE),
]

# LinkedIn Specific Board Artifacts
LINKEDIN_PATTERNS = [
    re.compile(r"people also viewed", re.IGNORECASE),
    re.compile(r"see who you know", re.IGNORECASE),
    re.compile(r"referrals increase your chances", re.IGNORECASE),
    re.compile(r"apply now", re.IGNORECASE),
    re.compile(r"easy apply", re.IGNORECASE),
]

# Naukri Specific Board Artifacts
NAUKRI_PATTERNS = [
    re.compile(r"recommended jobs", re.IGNORECASE),
    re.compile(r"similar jobs", re.IGNORECASE),
    re.compile(r"sponsored listing", re.IGNORECASE),
    re.compile(r"view more jobs", re.IGNORECASE),
]

# Navigation & Call to Action text
NAVIGATION_PATTERNS = [
    re.compile(r"^back to search$", re.IGNORECASE),
    re.compile(r"^click here$", re.IGNORECASE),
    re.compile(r"^learn more$", re.IGNORECASE),
    re.compile(r"^show more$", re.IGNORECASE),
    re.compile(r"^read more$", re.IGNORECASE),
]

# Company Legal / Boilerplate patterns
LEGAL_PATTERNS = [
    re.compile(r"equal opportunity employer", re.IGNORECASE),
    re.compile(r"reasonable accommodation", re.IGNORECASE),
    re.compile(r"privacy policy", re.IGNORECASE),
    re.compile(r"cookie policy", re.IGNORECASE),
    re.compile(r"terms of use", re.IGNORECASE),
]
