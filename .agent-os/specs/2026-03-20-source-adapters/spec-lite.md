# Spec Summary (Lite)

Build 5 async OSINT source adapters (OCCRP Aleph, OpenSanctions, ICIJ OffshoreLeaks, Pappers, GDELT) with a parallel orchestrator. Each adapter queries its API with a name, returns normalised results within 30s. Partial failures are handled gracefully — one source timing out never blocks the others.
