# Spec Tasks

## Tasks

- [x] 1. Local name matcher
  - [x] 1.1 Add unidecode to requirements.txt
  - [x] 1.2 Create `app/resolution/name_matcher.py` — normalise_name and is_name_match
  - [x] 1.3 Test locally with known edge cases (Cyrillic, hyphens, name order, partial matches)

- [x] 2. Claude entity resolver
  - [x] 2.1 Add anthropic SDK to requirements.txt
  - [x] 2.2 Create `app/resolution/claude_resolver.py` — send candidates to Claude, parse response
  - [x] 2.3 Add ANTHROPIC_API_KEY to deploy workflow .env
  - [x] 2.4 Add confidence and rationale fields to SourceMatch model

- [x] 3. Integrate into orchestrator
  - [x] 3.1 Remove hardcoded score thresholds from ICIJ and OpenSanctions adapters
  - [x] 3.2 Wire local name filter + Claude resolver into run_scan
  - [x] 3.3 Update API response to include confidence and rationale per match

- [ ] 4. Test and deploy
  - [ ] 4.1 Add ANTHROPIC_API_KEY to production environment secrets
  - [ ] 4.2 Deploy and verify end-to-end
  - [ ] 4.3 Test: "Irina Dunaeva" returns no wrong-person matches
  - [ ] 4.4 Test: matches show confidence level and rationale
