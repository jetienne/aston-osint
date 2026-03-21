# Spec Summary (Lite)

Build an entity resolution layer with two passes: a fast local name matcher (normalisation + token overlap) drops obvious non-matches, then Claude assesses ambiguous cases using contextual signals (birth year, nationality, company). Replaces hardcoded score thresholds in adapters. Each match gets a confidence level (HIGH/MEDIUM/LOW).
