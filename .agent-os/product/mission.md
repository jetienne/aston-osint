# Product Mission

## Pitch

Aston OSINT is a self-hosted intelligence platform that helps Aston's luxury brand teams profile Ultra High Net Worth prospects, verify AML/KYC compliance, and generate sales intelligence through a chat-based query and report workflow, powered by SpiderFoot on dedicated EU infrastructure.

## Users

### Primary Customers

- Aston Sales Teams: Advisors managing UHNW client relationships across luxury brands (hospitality, real estate, concierge) who need deep prospect intelligence to close high-value transactions
- Aston Compliance Officers: Staff responsible for AML/KYC due diligence on transactions ranging from EUR 20K to EUR 500K+

### User Personas

**Luxury Sales Advisor** (30-50 years old)
- **Role:** Senior Client Advisor
- **Context:** Manages a portfolio of UHNW clients across multiple luxury brands, handles bookings and transactions in the EUR 20K-500K+ range
- **Pain Points:** Cannot find reliable contact information for UHNW prospects, relies on intermediaries who erode margins, no visibility into prospect wealth structures or networks
- **Goals:** Bypass intermediaries to reach UHNW individuals directly, identify new qualified prospects through network mapping, time outreach to liquidity events

**Compliance Manager** (35-55 years old)
- **Role:** AML/KYC Compliance Officer
- **Context:** Must verify the identity, beneficial ownership, and risk profile of high-value transaction counterparties under EU AML regulations
- **Pain Points:** Third-party intelligence reports cost EUR 5K+ each, turnaround is slow, international profiles (Chinese, Russian, Middle Eastern, Central Asian nationals) are difficult to screen with standard tools
- **Goals:** Build defensible compliance paper trails efficiently, screen against PEP lists and sanctions databases, verify beneficial ownership across opaque corporate structures

## The Problem

### UHNW Profiles Are Invisible to Standard Tools

Ultra High Net Worth individuals do not maintain LinkedIn profiles or appear in standard CRM enrichment databases. Their wealth is distributed across holding companies, family offices, and trusts spanning multiple jurisdictions. Standard sales intelligence tools return nothing useful.

**Our Solution:** SpiderFoot aggregates public fragments from company registries, property records, press mentions, and legal filings to reconstruct comprehensive UHNW profiles.

### International Profiles Are Deliberately Opaque

A significant share of Aston's prospects are Chinese, Russian, Middle Eastern, or Central Asian nationals whose digital footprint is either minimal in Western sources or deliberately structured for opacity through nominees, BVI shells, and Liechtenstein foundations.

**Our Solution:** Cross-jurisdictional registry lookups and multi-source correlation map opaque profiles without requiring a dedicated intelligence firm at EUR 5K+ per report.

### AML/KYC Compliance Is Increasingly Regulated

Transactions of EUR 20K-500K+ create legitimate regulatory obligations to know who you are doing business with. Manual compliance checks do not scale and leave gaps in the audit trail.

**Our Solution:** Automated PEP screening, sanctions list cross-referencing, adverse media checks, and beneficial ownership verification produce a defensible paper trail for every transaction.

## Differentiators

### In-House Intelligence at Marginal Cost

Unlike third-party intelligence firms charging EUR 5K+ per report, Aston OSINT runs on dedicated infrastructure at fixed monthly cost. Each additional prospect profile costs only compute time, making deep intelligence viable at scale rather than reserved for the highest-value prospects only.

### Compliance and Sales Intelligence in One Platform

Unlike standalone compliance tools (World-Check, Dow Jones) that only flag risk, Aston OSINT simultaneously produces sales-relevant intelligence: direct contact recovery, network mapping of connected UHNW individuals, and timing signals from liquidity events. One scan serves both compliance and commercial teams.

### GitOps-Managed, Zero-Touch Operations

Unlike manually maintained OSINT tools that degrade over time, Aston OSINT is deployed and updated via a single git push to main. GitHub Actions handles deployment, configuration, and service verification automatically, ensuring the platform is always current without dedicated DevOps effort.

## Key Features

### Core OSINT Features

- **UHNW Prospect Profiling:** Reconstruct wealth structures, corporate holdings, and asset positions from public registry data, press mentions, and legal filings
- **PEP Screening:** Automatically check prospects against politically exposed persons databases across jurisdictions
- **Sanctions Cross-Referencing:** Screen against OFAC, EU consolidated list, and other sanctions databases in a single scan
- **Adverse Media Detection:** Surface fraud, money laundering, and corruption signals from news and legal sources
- **Beneficial Ownership Verification:** Trace through nominees, shell companies, and trust structures to identify ultimate beneficial owners

### Sales Intelligence Features

- **Direct Contact Recovery:** Find personal emails, PA contacts, and family office numbers to bypass intermediaries and protect margin
- **Network Mapping:** Surface connected individuals (co-directors, co-investors, family members) who are qualified prospects by association
- **Timing Signal Detection:** Identify liquidity events (IPOs, acquisitions, asset sales) that indicate near-term luxury spending appetite

### Infrastructure Features

- **GitOps Deployment:** Single git push to main triggers automated deployment to Hetzner VPS via GitHub Actions
- **HTTPS with Auto-Renewal:** Nginx reverse proxy with Let's Encrypt certificates, auto-renewing without intervention
