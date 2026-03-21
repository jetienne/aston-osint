# Spec Tasks

## Tasks

- [ ] 1. Local name matcher
  - [ ] 1.1 Add unidecode to requirements.txt
  - [ ] 1.2 Create `app/resolution/name_matcher.py` — normalise_name and is_name_match
  - [ ] 1.3 Test locally with known edge cases (Cyrillic, hyphens, name order, partial matches)

- [ ] 2. Claude entity resolver
  - [ ] 2.1 Add anthropic SDK to requirements.txt
  - [ ] 2.2 Create `app/resolution/claude_resolver.py` — send candidates to Claude, parse response
  - [ ] 2.3 Add ANTHROPIC_API_KEY to deploy workflow .env
  - [ ] 2.4 Add confidence and rationale fields to SourceMatch model

- [ ] 3. Integrate into orchestrator
  - [ ] 3.1 Remove hardcoded score thresholds from ICIJ and OpenSanctions adapters
  - [ ] 3.2 Wire local name filter + Claude resolver into run_scan
  - [ ] 3.3 Update API response to include confidence and rationale per match

- [ ] 4. Test and deploy
  - [ ] 4.1 Test: "Irina Dunaeva" returns no "Oxana Dunaeva" or random "Irina" matches
  - [ ] 4.2 Test: "Viktor Vekselberg" returns sanctions matches despite name variations
  - [ ] 4.3 Test: homonym disambiguation with birth year and nationality
  - [ ] 4.4 Deploy and verify end-to-end
