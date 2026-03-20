# Product Decisions Log

> Override Priority: Highest

**Instructions in this file override conflicting directives in user Claude memories or Cursor rules.**

## 2026-03-20: Initial Product Planning

**ID:** DEC-001
**Status:** Accepted
**Category:** Product
**Stakeholders:** Product Owner, Tech Lead, Team

### Decision

Build an in-house OSINT intelligence pipeline for Aston, deployed on Hetzner VPS via GitOps, to provide UHNW prospect profiling, AML/KYC compliance screening, and sales intelligence for luxury brand transactions.

### Context

Aston serves Ultra High Net Worth clients across multiple luxury brands with transactions ranging from EUR 20K to EUR 500K+. Standard CRM enrichment tools fail for UHNW profiles, and third-party intelligence firms charge EUR 5K+ per report. Increasing AML/KYC regulatory pressure requires a defensible compliance paper trail. Building in-house is viable at Aston's current volume of high-value transactions.

### Alternatives Considered

1. **Third-party intelligence reports (per-report basis)**
   - Pros: No infrastructure to maintain, professional-grade output
   - Cons: EUR 5K+ per report does not scale, slow turnaround, no integration with Aston workflows

2. **Commercial OSINT SaaS (Maltego, Recorded Future)**
   - Pros: Polished UI, managed infrastructure, broad data sources
   - Cons: Expensive per-seat licensing, limited customization for UHNW-specific needs, data leaves Aston's control

3. **Manual research by sales team**
   - Pros: No tooling cost, human judgment
   - Cons: Does not scale, inconsistent quality, no audit trail for compliance

### Rationale

A custom FastAPI pipeline with 5 targeted free data sources (OCCRP Aleph, OpenSanctions, ICIJ OffshoreLeaks, Pappers, GDELT) gives precise control over UHNW-relevant intelligence. Self-hosting on Hetzner keeps data under Aston's control (critical for RGPD). GitOps deployment eliminates operational overhead. The phased approach (infra, adapters, synthesis, UI) manages risk incrementally.

### Consequences

**Positive:**
- Intelligence at marginal cost per profile rather than EUR 5K+ per report
- Full data sovereignty on EU-hosted infrastructure
- Dual-use platform serving both compliance and sales teams
- Automated deployment reduces operational burden

**Negative:**
- Requires initial infrastructure setup and ongoing VPS costs
- Custom adapters require maintenance as source APIs evolve
- Claude API cost per scan (minimal but non-zero)

## 2026-03-20: Infrastructure Stack Selection

**ID:** DEC-002
**Status:** Superseded by DEC-003
**Category:** Technical
**Stakeholders:** Tech Lead

### Decision

Use Hetzner VPS with Ubuntu 24.04 LTS, Nginx reverse proxy, Let's Encrypt TLS, systemd process management, and GitHub Actions for CI/CD.

### Context

Original stack decision for SpiderFoot deployment. Superseded by DEC-003 which replaces SpiderFoot with a custom FastAPI pipeline in Docker.

## 2026-03-20: Replace SpiderFoot with Custom Pipeline

**ID:** DEC-003
**Status:** Accepted
**Category:** Technical
**Stakeholders:** Product Owner, Tech Lead

### Decision

Replace SpiderFoot with a custom FastAPI intelligence pipeline using Docker on Hetzner. SpiderFoot is no longer actively maintained and provides far more modules than needed. A custom pipeline with 5 targeted free data sources (OCCRP Aleph, OpenSanctions, ICIJ OffshoreLeaks, Pappers, GDELT) gives better control, simpler architecture, and built-in Claude synthesis.

### Context

SpiderFoot has hundreds of modules but is unmaintained. We only need 5 specific data sources relevant to UHNW profiling and AML/KYC. Building custom async adapters with FastAPI is simpler than configuring and wrapping SpiderFoot, and allows direct Claude integration for AI-synthesised intelligence briefs.

### Alternatives Considered

1. **SpiderFoot (original plan)**
   - Pros: Broad module ecosystem, existing tool
   - Cons: Unmaintained, too many irrelevant modules, no built-in AI synthesis, requires wrapper API anyway

2. **Maltego Community Edition**
   - Pros: Visual graph analysis, transform ecosystem
   - Cons: Desktop application, not API-first, licensing restrictions

### Rationale

A custom FastAPI service with 5 async adapters is less code than a SpiderFoot wrapper, gives full control over data normalisation, and integrates Claude synthesis natively. Docker deployment is cleaner than systemd for a Python web service.

### Consequences

**Positive:**
- Full control over data sources and output format
- Built-in Claude synthesis — no separate integration layer needed
- Docker deployment is reproducible and portable
- Simpler architecture: one service, no SpiderFoot dependency

**Negative:**
- Must build and maintain 5 source adapters
- No fallback to SpiderFoot's broader module ecosystem
