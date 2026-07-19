# Local Grid Health & Civic Advocacy Platform: Data & Competitor Architecture

This document serves as the foundational data map and landscape analysis for building a consumer-facing web application. The platform's goal is to allow users to look up local grid age/health, track upcoming modernization projects, and directly advocate for renewable-ready grid infrastructure.

---

## 1. Where to Source "Local Grid Age" Data
Because utilities do not publish an exact asset-age database for national security reasons, the platform must use public "proxy data" to estimate and communicate the health and capacity of a user's local grid:

*   **ASCE Infrastructure Report Cards:** The American Society of Civil Engineers (ASCE) evaluates and grades energy infrastructure at both national and state levels. These reports provide localized contextual grades (e.g., a "D+" rating) and qualitative analysis on regional grid vulnerabilities.
*   **LBNL Interconnection Queues:** The Lawrence Berkeley National Laboratory (LBNL) tracks the backlog of clean energy projects waiting to connect to the regional grid. High wait times and backlogs serve as a primary indicator that local transmission lines lack the capacity to handle new renewable energy.
*   **EIA Reliability Metrics (Form EIA-861):** The U.S. Energy Information Administration (EIA) collects annual data on SAIDI (System Average Interruption Duration Index) and SAIFI (System Average Interruption Frequency Index) for almost every utility. This allows the platform to calculate and display the average duration and frequency of local power outages compared to the national average.

---

## 2. Similar Projects & Competitive Landscape
While no single platform currently unifies local grid data with direct public utility commission (PUC) advocacy tools, several existing projects handle specific elements of accountability, modernization tracking, and community action:

*   **The Utility Disconnections Dashboard (Energy Justice Lab):** Hosted by Indiana University, this platform aggregates highly fragmented local utility reports into a clean, searchable nationwide map. It serves as an excellent user interface template for visualizing disparate utility-level data for the public.
*   **The Brockovich Data Center Tracker:** This crowdsourced mapping project tracks heavy infrastructure pressure and rising utility costs driven by AI data centers. It demonstrates a high public demand for visual tools that connect massive grid strain directly to local consumer energy bills.
*   **ACEEE Utility Scorecards:** Published by the American Council for an Energy-Efficient Economy, this framework ranks the nation's largest utilities on equity, renewable deployment, and grid efficiency. It provides a proven model for translating complex utility policies into user-friendly letter grades.
*   **DOE GRIP Award Map:** The Department of Energy maintains an interactive dashboard displaying where billions of dollars in Grid Resilience and Innovation Partnerships (GRIP) grants are flowing. The raw data provides a structured pipeline of utility names, grant amounts, and project descriptions that can be mapped to consumer zip codes.
*   **IREC Grid Playbooks:** The Interstate Renewable Energy Council (IREC) hosts toolkits tracking utility "hosting capacity"—the technical limit of how much local solar or storage a distribution system can handle before requiring upgrades.
*   **Solar@Scale Guidebook:** Developed by the American Planning Association, this project offers comprehensive toolkits and regulatory templates for local officials and citizens attempting to navigate grid integration hurdles.

---

## 3. Platform Value Proposition
The primary value of this website is **integration**. Existing tools are fragmented across academic databases, government dashboards, and policy PDFs. By linking a user's zip code directly to their local utility's reliability metrics, active federal grants, and state Public Utility Commission (PUC) dockets, this platform will serve as the first unified civic action hub for the American power grid.
