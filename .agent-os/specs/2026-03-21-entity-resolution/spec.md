# Spec Requirements Document

> Spec: Entity Resolution
> Created: 2026-03-21
> Status: Planning

## Overview

Build an entity resolution layer that filters raw OSINT source results to determine which matches actually refer to the queried person. This replaces naive score thresholds with intelligent matching that handles name variations, transliterations, and disambiguation using contextual signals (birth year, nationality, company).

## User Stories

### Filter Out Wrong People

As an ops team member, I want the scan results to only show matches that are actually about the person I searched for, so that I don't waste time reviewing unrelated people who happen to share a first name or surname.

Today, searching "Irina Dunaeva" returns "Oxana Dunaeva" (same surname, different person) and various "Irina" matches (same first name, different surname). These are noise. The entity resolution layer should eliminate them.

### Match Despite Name Variations

As an ops team member, I want the system to find matches even when the name is written differently, so that I don't miss critical intelligence because of transliteration differences or name ordering conventions.

Examples of variations that should match:
- "Viktor Vekselberg" = "Виктор Вексельберг" (Cyrillic/Latin)
- "Mohammed bin Salman" = "Mohammad bin Salman" = "MBS" (transliteration variants)
- "Dunaeva Irina" = "Irina Dunaeva" (name order)
- "Jean-Pierre" = "Jean Pierre" (hyphenation)

### Disambiguate Homonyms

As a compliance officer, I want the system to use contextual signals to distinguish between people with the same name, so that I don't flag the wrong "Vladimir Ivanov" as sanctioned.

When multiple results share the same name, use birth year, nationality, company affiliations, and other contextual signals from the query to decide which match is the right person. If ambiguity remains, keep the match but flag it as uncertain.

## Spec Scope

1. **Two-pass filtering architecture** — First pass: fast local name matching to drop obvious non-matches. Second pass: Claude-based entity resolution for ambiguous cases.
2. **Local name matcher** — Compare query name against result names using normalisation (lowercase, diacritics, transliteration) and token overlap (both first and last name tokens must appear)
3. **Claude entity resolution** — For matches that pass the local filter, ask Claude to assess whether each result refers to the queried person, using all available context (name, birth year, nationality, company, source data)
4. **Confidence scoring** — Each match gets a confidence level: HIGH (definitely this person), MEDIUM (likely but ambiguous), LOW (uncertain, kept for review)
5. **Drop score thresholds from adapters** — Remove hardcoded score cutoffs from ICIJ and OpenSanctions adapters; let entity resolution handle filtering

## Out of Scope

- Building a persistent entity database or knowledge graph
- Cross-source entity linking (merging the same person across sources)
- Automated learning from user feedback on match quality
- Full synthesis report generation (Phase 3)

## Expected Deliverable

1. Searching "Irina Dunaeva" returns zero results for "Oxana Dunaeva" or random "Irina" matches
2. Searching "Viktor Vekselberg" returns sanctions matches despite Cyrillic/Latin variations
3. Each match includes a confidence level (HIGH/MEDIUM/LOW) with rationale
4. The orchestrator applies entity resolution before returning results
