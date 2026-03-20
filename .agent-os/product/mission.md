# Product Mission

## Pitch

Aston OSINT is a self-hosted intelligence pipeline that helps Aston's luxury brand teams profile Ultra High Net Worth prospects and screen AML/KYC compliance by aggregating five open-source data sources and synthesising results into structured intelligence briefs via Claude, deployed on Hetzner via GitOps.

## Users

### Primary Customers

- Aston Ops Team: Non-technical staff who need to run prospect intelligence checks via a simple web form before or during the booking process
- Aston Sales Advisors: Advisors managing UHNW client relationships who need deep prospect profiles to close high-value transactions and identify new leads

### User Personas

**Operations Manager** (30-45 years old)
- **Role:** Booking Operations
- **Context:** Processes villa and chalet bookings ranging from EUR 20K to EUR 500K+, needs to verify client identity and risk before confirming
- **Pain Points:** No systematic screening process, manual ad-hoc research, exposure to sanctions and PEP risk, no audit trail
- **Goals:** Run a name through a single form and get a compliance-ready intelligence brief in under 90 seconds

**Senior Sales Advisor** (35-50 years old)
- **Role:** UHNW Client Advisor
- **Context:** Manages a portfolio of UHNW clients across multiple luxury brands, needs to identify direct contacts and network connections
- **Pain Points:** Cannot find reliable contact information, relies on intermediaries who erode margins, no visibility into prospect wealth structures
- **Goals:** Identify connected individuals, offshore structures, and liquidity event signals to time outreach and bypass intermediaries

## The Problem

### No Systematic Prospect Profiling

Intel is gathered ad hoc by ops team members manually. There is no structured, reproducible process for profiling UHNW prospects. Standard CRM enrichment tools return nothing useful for this segment.

**Our Solution:** An automated pipeline that fans out to 5 data sources in parallel and synthesises results via Claude into a structured intelligence brief.

### No AML/KYC Screening Process

Aston handles transactions of EUR 20K-500K+ with no systematic screening against sanctions lists, PEP databases, or adverse media. This creates regulatory exposure.

**Our Solution:** Every scan automatically checks OpenSanctions for PEP and sanctions flags, and OCCRP Aleph for adverse media and investigation links.

### Per-Report Intelligence Costs Are Prohibitive

Third-party intelligence firms charge EUR 2K-5K per report. At current prospect volume, this is not viable for systematic screening.

**Our Solution:** The pipeline costs effectively zero per query beyond fixed infrastructure costs (Hetzner VPS + Claude API tokens).

## Differentiators

### Five Free Data Sources, One Unified Brief

Unlike paid intelligence platforms, Aston OSINT aggregates five high-quality free sources (OCCRP Aleph, OpenSanctions, ICIJ OffshoreLeaks, Pappers, GDELT) into a single AI-synthesised brief. No per-query fees, no subscriptions.

### AI-Synthesised Intelligence, Not Raw Data Dumps

Unlike OSINT tools that return raw search results, Aston OSINT uses Claude to produce a structured brief with identity verification, risk scoring, and actionable recommendations — readable by non-technical ops staff.

### Compliance-Ready Audit Trail

Unlike manual research, every scan produces a timestamped, structured output (PDF + JSON) that serves as a defensible compliance record if a transaction is ever questioned.

## Key Features

### Core Intelligence Features

- **Multi-Source OSINT Scan:** Parallel queries across OCCRP Aleph, OpenSanctions, ICIJ OffshoreLeaks, Pappers, and GDELT
- **AI-Synthesised Brief:** Claude produces a structured intelligence report with identity, entities, sanctions flags, offshore links, press signals, and risk score
- **PDF Report Generation:** WeasyPrint renders a downloadable, well-formatted PDF from an HTML template
- **JSON API Output:** Structured JSON response for programmatic integration
- **Risk Scoring:** Automated risk assessment (LOW/MEDIUM/HIGH/CRITICAL) with rationale

### User Interface Features

- **Ops Web Form:** Minimal single-page HTML form for non-technical users — enter a name, get a PDF
- **REST API Endpoint:** POST /api/v1/scan for programmatic access from Aston or scripts

### Infrastructure Features

- **Docker Deployment:** Single Docker container on Hetzner VPS
- **GitOps Pipeline:** GitHub Actions deploy on manual trigger
- **API Key Authentication:** Secure access to the scan endpoint
- **30-Second Source Timeout:** No silent failures — each adapter returns results or a clean timeout
