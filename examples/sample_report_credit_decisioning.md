---

# MERIDIAN FINANCIAL GROUP
## AI Risk Assessment Report

**Use Case:** XGBoost credit decisioning model utilizing alternative data (utility payment and rent history) for automated initial credit approval decisions in consumer lending. The model operates autonomously without mandatory human review for each decision, directly affecting consumer access to credit.

**Assessment Date:** February 13, 2026

**Prepared by:** AI Risk Management, Second Line of Defense

**Risk Tier:** Critical

---

## 1. Executive Summary

XGBoost credit decisioning model utilizing alternative data (utility payment and rent history) for automated initial credit approval decisions in consumer lending. The model operates autonomously without mandatory human review for each decision, directly affecting consumer access to credit.

**Risk Tier:** Critical — This use case involves fully automated credit decisioning that directly impacts consumers' access to credit, triggering significant regulatory scrutiny under ECOA, FCRA, and fair lending laws. The use of alternative data features (utility and rent payments) introduces heightened risk as these variables may serve as proxies for protected classes. The autonomous nature of initial approval decisions without mandatory human oversight elevates model risk and compliance risk substantially.

| Metric | Value |
|--------|-------|
| Total gaps identified | 8 |
| Critical gaps | 7 |
| High gaps | 1 |
| Overall coverage score | 51% |
| External citations | 8 |
| Internal citations | 9 |

**Top Recommendation:** Implement mandatory pre-deployment fair lending testing including disparate impact analysis across all protected classes, with formal approval required from Fair Lending Officer before production deployment.

## 2. Risk Tier Determination

**Tier:** Critical

This use case involves fully automated credit decisioning that directly impacts consumers' access to credit, triggering significant regulatory scrutiny under ECOA, FCRA, and fair lending laws. The use of alternative data features (utility and rent payments) introduces heightened risk as these variables may serve as proxies for protected classes. The autonomous nature of initial approval decisions without mandatory human oversight elevates model risk and compliance risk substantially.

**Key Risks:**
- Fair lending and disparate impact risk: Utility payment and rent history data may serve as proxies for protected class characteristics (race, national origin, familial status), potentially creating disparate impact in credit decisions that violates ECOA and fair lending laws.
- Explainability and adverse action compliance risk: XGBoost ensemble methodology creates complex, non-linear decision boundaries that may be difficult to explain in terms satisfying ECOA Regulation B requirements for specific and accurate adverse action reasons.
- Alternative data quality and representativeness risk: Utility and rent payment data may have differential coverage rates across demographic segments, income levels, and geographic regions, potentially creating systematic bias against underserved populations.
- Model uncertainty and autonomous decision risk: Automated credit approval without mandatory human review increases the impact of model errors, prediction uncertainty, and systematic bias, with potential for widespread harm before detection.
- Regulatory compliance and supervision risk: Use of alternative data and complex ML methods in automated credit decisioning attracts heightened regulatory scrutiny from CFPB, OCC, and Federal Reserve, with potential for enforcement actions if fair lending violations are identified.
- Override pattern risk: If loan officers systematically override model denials for certain demographic groups, this may indicate model bias while also creating fair lending risk through inconsistent manual decision-making.
- Data drift and model degradation risk: Alternative data sources (utility, rent payment systems) may undergo changes in data collection, coverage, or provider practices that cause model performance to deteriorate, particularly if changes affect demographic segments differently.
- Third-party data vendor risk: Reliance on external providers for alternative data creates operational risk, data quality risk, and potential compliance risk if vendor practices do not meet fair lending standards or if data supply is disrupted.

## 3. Regulatory Requirements by RMF Function

### 3.1 Govern

**Coverage Score:** 50%

- **Establish regulatory and compliance controls that address AI/ML explainability, interpretability, and transparency in credit decision-making, with revisions to policies, procedures, and standards to ensure compliance with consumer protection and fair lending laws.** (FHFA AB 2022-02, Section III.D) — Applicability: HIGH | *FHFA: FHFA requires specific attention to explainability and interpretability controls for AI/ML credit underwriting models due to consumer protection and fair lending law mandates.*
  - *Recommendation:* Enhance AI governance policy to explicitly address explainability requirements for credit models using alternative data, establish interpretability standards for automated credit decisions, and document transparency requirements for consumer-facing credit decisioning.
- **Design a compliance risk management program that includes analysis of relevant consumer protection, employment discrimination, privacy, and other laws as they apply to the use of personal and alternative data, involving qualified compliance personnel during AI/ML development and implementation.** (FHFA AB 2022-02, Section III.D) — Applicability: HIGH | *FHFA: FHFA specifically requires compliance personnel involvement throughout the AI/ML lifecycle for models using personal and alternative data.*
  - *Recommendation:* Establish a dedicated compliance review process for AI/ML models using alternative data, requiring formal sign-off from compliance officers on data sourcing, feature selection, and model outputs before production deployment.
- **Integrate fair lending reviews and testing through all lifecycle stages of AI/ML models used in credit decision-making.** (FHFA AB 2022-02, Section III.D) — Applicability: HIGH | *FHFA: FHFA requires fair lending testing integrated throughout the entire model lifecycle, not just at validation.*
  - *Recommendation:* Implement mandatory fair lending testing at development, pre-deployment validation, and ongoing monitoring phases. Conduct disparate impact analysis across protected classes using both traditional credit variables and alternative data features.
- **Establish risk monitoring, reporting, and communication processes that convey AI/ML metrics to different stakeholders across the enterprise and escalate to senior management and the board, with granular metrics for first line and aggregated data for second line risk management.** (FHFA AB 2022-02, Section IV) — Applicability: HIGH
  - *Recommendation:* Develop a tiered reporting framework for credit decisioning models that provides model performance metrics, override rates, and fair lending test results to the Model Risk Committee monthly and aggregated risk indicators to the Board quarterly.

### 3.2 Map

**Coverage Score:** 62%

- **Model development must begin with a clear statement of purpose to ensure alignment with intended use. Design, theory, and logic underlying the model should be well documented and supported by published research and sound industry practice.** (SR 11-7, Section IV) — Applicability: HIGH
  - *Recommendation:* Document the specific business purpose for using alternative data features (utility and rent payment history) in credit decisioning. Provide theoretical justification and industry research supporting the predictive relationship between these alternative variables and credit risk.
- **Data used to develop a model requires rigorous assessment of quality and relevance with appropriate documentation. Data proxies must be carefully identified, justified, and documented. If data are not representative or if adjustments are made, these factors should be tracked and analyzed so users are aware of potential limitations.** (SR 11-7, Section IV) — Applicability: HIGH
  - *Recommendation:* Conduct comprehensive data quality assessment for utility payment and rent history data sources. Document any representativeness limitations (e.g., coverage gaps across demographics, geographies, or income levels). If these alternative data features serve as proxies for traditional credit variables, explicitly identify and justify their use.
- **AI/ML risks may become heightened and manifest in unfamiliar ways given complexity and speed of innovation, making risks harder to identify effectively and in a timely manner. Risk identification should involve stakeholders across technology, modeling, and third-party risk management.** (FHFA AB 2022-02, Section II) — Applicability: HIGH | *FHFA: FHFA emphasizes that AI/ML risks manifest in unfamiliar ways requiring broader stakeholder involvement than traditional models.*
  - *Recommendation:* Establish cross-functional risk identification process involving data science, compliance, fair lending, third-party risk, and legal teams to comprehensively map risks associated with alternative data use in automated credit decisions. Document both known and emerging risks specific to XGBoost models and alternative data features.
- **Identify regulatory and compliance risks including consumer protection, fair lending, privacy, and discrimination laws. AI/ML credit underwriting models present compliance risks due to lack of explainability, interpretability of output, and adequacy of controls in decision-making mandated by consumer protection and fair lending laws.** (FHFA AB 2022-02, Section II.D) — Applicability: HIGH
  - *Recommendation:* Conduct detailed legal and regulatory risk assessment mapping specific requirements under ECOA, FCRA, fair lending regulations, and state-level consumer protection laws. Document explainability challenges inherent in XGBoost ensemble methods and their implications for adverse action notice requirements.

### 3.3 Measure

**Coverage Score:** 50%

- **Model validation scope must include conceptual soundness review (theoretical foundation, appropriateness of methodology, quality of design), outcomes analysis (quantitative evaluation using statistical tests and metrics, back-testing, benchmarking), and sensitivity analysis (stability and robustness to input changes).** (SR 11-7 and Meridian MRM Policy, Section 3.2) — Applicability: HIGH
  - *Recommendation:* Ensure independent validation of XGBoost credit model includes: (1) conceptual soundness review of alternative data feature selection and ensemble methodology; (2) outcomes analysis with back-testing on holdout data segmented by protected classes; (3) sensitivity analysis testing model stability when alternative data features are removed or perturbed.
- **Outcomes analysis should involve a range of tests including tests for rank-ordering ability and absolute forecast accuracy. Back-testing involves comparison of actual outcomes with model forecasts using expected ranges or statistical confidence intervals. Discrepancies that are significant in magnitude or frequency should be investigated.** (SR 11-7, Section V) — Applicability: HIGH
  - *Recommendation:* Implement comprehensive outcomes analysis for credit decisioning model including rank-ordering tests (Gini coefficient, KS statistic), accuracy metrics (approval rates, default rates), and back-testing across multiple time periods and customer segments. Investigate any performance discrepancies across protected class subgroups.
- **All AI/ML models are expected to go through model validation by the second line model risk management function or contracted third party. Point-in-time validation approaches may need to be adapted as AI/ML models may not be static between reviews. Model validation frequency and scope must be adequate to address AI/ML models.** (FHFA AB 2022-02, Section III.A) — Applicability: HIGH | *FHFA: FHFA specifically notes that point-in-time validation may be insufficient for AI/ML models that change between review cycles.*
  - *Recommendation:* Establish enhanced validation protocol for XGBoost credit model recognizing potential for more frequent updates than traditional models. Consider quarterly validation reviews rather than annual given automated nature of credit decisions and potential for rapid performance drift with alternative data sources.
- **Benchmarking involves comparison of model inputs and outputs to estimates from alternative internal or external models or data. Discrepancies between model output and benchmarks should trigger investigation. Benchmark models should be rigorous and benchmark data should be accurate and complete.** (SR 11-7, Section V) — Applicability: MEDIUM
  - *Recommendation:* Benchmark XGBoost model performance against traditional credit scoring models (FICO-based logistic regression) to assess incremental value of alternative data features and ensemble methodology. Compare approval rates, default rates, and protected class distributions between models.

### 3.4 Manage

**Coverage Score:** 43%

- **Ongoing monitoring should include sensitivity analysis and checks for robustness and stability repeated periodically. Models should be monitored to identify situations where operational constraints are approached or exceeded.** (SR 11-7, Section V) — Applicability: HIGH
  - *Recommendation:* Implement continuous monitoring of XGBoost credit model including monthly sensitivity checks on alternative data features, stability testing of model coefficients/feature importance, and alerts when input data distributions shift beyond training data ranges. Monitor for data quality degradation in utility payment and rent history feeds.
- **Ongoing monitoring should include analysis of overrides with appropriate documentation. Override rates should be tracked and analyzed. High override rates or consistent override performance improvement indicate the model needs revision or redevelopment.** (SR 11-7, Section V) — Applicability: HIGH
  - *Recommendation:* Establish comprehensive override tracking system for credit decisioning model. Analyze override patterns across protected classes, alternative data feature values, and decision types. Report override rates and performance to Model Risk Committee quarterly with triggers for model review if override rates exceed 15% or if overrides show systematic improvement over model decisions.
- **Model documentation requirements and frequency of update must be adequate to reflect current AI/ML model input and output relationships and model operation. Consideration of ethical principles such as fairness and bias must be adequately addressed throughout all lifecycle stages.** (FHFA AB 2022-02, Section III.A) — Applicability: HIGH | *FHFA: FHFA specifically requires consideration of ethical principles including fairness and bias throughout all lifecycle stages.*
  - *Recommendation:* Establish quarterly documentation review cycle for XGBoost credit model to ensure model documentation reflects current feature relationships, performance characteristics, and fairness metrics. Require ongoing bias testing and documentation of fairness assessments in monitoring reports.
- **Model risk management processes for identification of material model changes may need to be enhanced given the more frequent AI/ML model change management cycle.** (FHFA AB 2022-02, Section III.A) — Applicability: HIGH
  - *Recommendation:* Define materiality thresholds for XGBoost credit model changes that trigger revalidation. Establish change management protocol that assesses whether alternative data source updates, feature engineering modifications, or hyperparameter adjustments constitute material changes requiring validation review before production deployment.
- **Risk monitoring data should be conveyed to different stakeholders across the enterprise and escalated to senior management and the board, with granular metrics for first line and aggregated data for second line risk management.** (FHFA AB 2022-02, Section IV) — Applicability: HIGH
  - *Recommendation:* Develop tiered reporting for credit model: (1) Daily operational metrics for model users (approval rates, score distributions, data quality flags); (2) Monthly detailed analytics for Model Risk Committee (performance metrics, override analysis, fair lending tests); (3) Quarterly executive summary for Board Risk Committee (aggregate risk indicators, material issues, regulatory compliance status).

## 4. Internal Policy Alignment

### Govern

| Policy | Section | Coverage | Adequacy |
|--------|---------|----------|----------|
| Meridian AI Governance Policy | Section 3.1 | Policy defines Critical tier (Tier 1) for models that directly influence custome... | ✅ ADEQUATE |
| Meridian MRM Policy | Section 6.1 | Model Risk Committee (MRC) is established as principal governance body, meeting ... | ✅ ADEQUATE |
| Meridian AI Governance Policy | Section 4.2 | Documentation requirements specify comprehensive Model Development Memorandum co... | ⚠️ PARTIAL |

### Map

| Policy | Section | Coverage | Adequacy |
|--------|---------|----------|----------|
| Meridian MRM Policy | Section 2.1 | Policy requires clear articulation of business problem, documentation of theoret... | ✅ ADEQUATE |
| Meridian AI Governance Policy | Section 4.1 | Policy requires data quality assessment for completeness, accuracy, timeliness, ... | ⚠️ PARTIAL |
| Meridian MRM Policy | Section 4.1 | Policy requires clearly defined approved use cases documented in model inventory... | ✅ ADEQUATE |

### Measure

| Policy | Section | Coverage | Adequacy |
|--------|---------|----------|----------|
| Meridian MRM Policy | Section 3.2 | Policy establishes validation scope including conceptual soundness review (theor... | ✅ ADEQUATE |
| Meridian MRM Policy | Section 5 | Policy recognizes that models may deteriorate over time due to environmental cha... | ⚠️ PARTIAL |
| Meridian AI Governance Policy | Section 4.2 | Documentation must include model performance metrics and known limitations, main... | ✅ ADEQUATE |

### Manage

| Policy | Section | Coverage | Adequacy |
|--------|---------|----------|----------|
| Meridian MRM Policy | Section 5 | Policy establishes ongoing monitoring as essential component of model risk manag... | ⚠️ PARTIAL |
| Meridian MRM Policy | Section 4.3 | Policy requires business users to document override rationale. Override rates mo... | ✅ ADEQUATE |
| Meridian AI Governance Policy | Section 4.2 | Documentation maintained in model repository and updated to reflect material cha... | ⚠️ PARTIAL |
| Meridian MRM Policy | Section 4.1 | Each model has clearly defined approved use cases documented in model inventory.... | ✅ ADEQUATE |

## 5. Gap Analysis

Gaps sorted by severity. CRITICAL gaps represent areas where regulatory requirements are completely unaddressed by internal policy.

| Severity | Gap Category | External Requirement | Internal Status | Remediation |
|----------|-------------|---------------------|-----------------|-------------|
| 🔴 **CRITICAL** | Fair Lending Integration | FHFA AB 2022-02 Section III.D requires integrating fair lend... | NOT ADDRESSED | Amend AI Governance Policy to mandate fair lending testing a... |
| 🔴 **CRITICAL** | Compliance Personnel Involvement | FHFA AB 2022-02 Section III.D requires involving qualified c... | NOT ADDRESSED | Establish mandatory compliance review checkpoints in AI mode... |
| 🔴 **CRITICAL** | Explainability and Interpretability Standards | FHFA AB 2022-02 Section III.D requires revising policies to ... | Meridian AI Governance Policy Section 4.... | Develop and document explicit explainability standards for c... |
| 🔴 **CRITICAL** | Alternative Data Proxy Analysis | SR 11-7 Section IV requires data proxies to be carefully ide... | Meridian AI Governance Policy Section 4.... | Enhance data documentation requirements to mandate explicit ... |
| 🔴 **CRITICAL** | XGBoost Explainability Assessment | FHFA AB 2022-02 Section II.D identifies lack of explainabili... | NOT ADDRESSED | Establish methodology documentation standards for complex ML... |
| 🔴 **CRITICAL** | Fair Lending Validation Testing | FHFA AB 2022-02 Section III.D requires integrating fair lend... | Meridian MRM Policy Section 3.2 establis... | Amend MRM Policy Section 3.2 to mandate fair lending testing... |
| 🔴 **CRITICAL** | Continuous Fair Lending Monitoring | FHFA AB 2022-02 Section III.D requires integrating fair lend... | Meridian MRM Policy Section 5 addresses ... | Enhance ongoing monitoring requirements to mandate monthly f... |
| 🟠 **HIGH** | Alternative Data Risk Assessment | FHFA AB 2022-02 Section III.D requires compliance risk manag... | Meridian AI Governance Policy Section 4.... | Establish alternative data assessment framework that evaluat... |

## 6. Remediation Priorities

**Priority 1 (CRITICAL):** Fair Lending Integration — Amend AI Governance Policy to mandate fair lending testing at development, validation, and monitoring stages for all credit decisioning models. Establish specific disparate impact testing protocols for models using alternative data that may serve as proxies for protected classes. *(Ref: FHFA AB 2022-02, Section III.D)*

**Priority 2 (CRITICAL):** Compliance Personnel Involvement — Establish mandatory compliance review checkpoints in AI model development lifecycle. Require formal sign-off from Fair Lending Officer and Chief Compliance Officer before production deployment of any credit decisioning model using alternative data. *(Ref: FHFA AB 2022-02, Section III.D)*

**Priority 3 (CRITICAL):** Explainability and Interpretability Standards — Develop and document explicit explainability standards for credit decisioning models, including requirements for feature importance analysis, local interpretability methods (e.g., SHAP, LIME), and adverse action reason code generation that meets ECOA/Regulation B requirements. *(Ref: FHFA AB 2022-02, Section III.D)*

**Priority 4 (CRITICAL):** Alternative Data Proxy Analysis — Enhance data documentation requirements to mandate explicit proxy variable analysis for alternative data features. Require assessment of whether utility payment or rent history data correlates with protected class membership and document potential disparate impact risks before model development proceeds. *(Ref: SR 11-7, Section IV)*

**Priority 5 (CRITICAL):** XGBoost Explainability Assessment — Establish methodology documentation standards for complex ML models (XGBoost, ensemble methods) that explicitly address explainability limitations. Require developers to document approach for generating adverse action reasons compliant with ECOA Regulation B and assess whether model complexity prevents legally sufficient explanations. *(Ref: FHFA AB 2022-02, Section II.D)*

**Priority 6 (CRITICAL):** Fair Lending Validation Testing — Amend MRM Policy Section 3.2 to mandate fair lending testing as a required validation component for all credit decisioning models. Specify required analyses including disparate impact testing across protected classes, segmented performance analysis, and testing for proxy discrimination via alternative data features. *(Ref: FHFA AB 2022-02, Section III.D)*

**Priority 7 (CRITICAL):** Continuous Fair Lending Monitoring — Enhance ongoing monitoring requirements to mandate monthly fair lending testing for automated credit decisioning models. Establish monitoring metrics including approval rates by protected class, adverse action rates by demographic segment, and statistical tests for disparate impact. Set triggers requiring immediate model suspension if disparate impact thresholds are exceeded. *(Ref: FHFA AB 2022-02, Section III.D)*

**Priority 8 (HIGH):** Alternative Data Risk Assessment — Establish alternative data assessment framework that evaluates legal and regulatory implications of using non-traditional credit data (utility payments, rent history). Require legal review of data sourcing agreements and proxy variable analysis before model development. *(Ref: FHFA AB 2022-02, Section III.D)*


## 7. SR 11-7 Alignment

- **Section IV: Model Development, Implementation, And Use** — Data proxies must be carefully identified, justified, and documented. If data are not representative of the bank's portfolio or if assumptions are made to adjust data, these factors should be properly tracked and analyzed so that users are aware of potential limitations. This is particularly important for external data from vendors or outside parties.
  - *Recommendation:* Conduct comprehensive proxy variable analysis for utility payment and rent history features to assess whether they serve as proxies for protected class characteristics. Document any representativeness limitations of alternative data sources across demographic segments, geographic regions, and income levels. Establish data quality monitoring to track coverage rates and missing data patterns that may create disparate impact.

- **Section V: Model Validation** — Model validation should include outcomes analysis with a range of tests, back-testing comparing actual outcomes to model forecasts, and investigation of discrepancies that are significant in magnitude or frequency to determine whether differences stem from omission of material factors or errors in model specification.
  - *Recommendation:* Implement comprehensive back-testing protocol for XGBoost credit model segmented by protected class characteristics. Conduct outcomes analysis comparing predicted approval/default rates to actual outcomes across demographic segments. Investigate any statistically significant performance discrepancies that may indicate model bias or disparate impact.

- **Section V: Model Validation** — Ongoing monitoring should include analysis of overrides with appropriate documentation. Banks should evaluate reasons for overrides and track and analyze override performance. High override rates or consistent override performance improvement often indicates the underlying model needs revision or redevelopment.
  - *Recommendation:* Establish override tracking system that captures override rationale, analyzes override patterns across protected classes and alternative data feature values, and measures override performance relative to model decisions. Set override rate thresholds (e.g., >15%) that trigger mandatory model review and potential redevelopment. Analyze whether overrides systematically benefit or disadvantage particular demographic groups.

- **Section IV: Model Development, Implementation, And Use** — Understanding of model uncertainty and inaccuracy and demonstration that the bank is accounting for them appropriately are important outcomes of effective model development. Using a range of outputs rather than simple point estimates can signal model uncertainty and avoid spurious precision. Banks should account for uncertainty in a conservative manner when models influence material decisions.
  - *Recommendation:* Implement prediction confidence intervals for XGBoost credit model decisions. Establish decision thresholds that account for model uncertainty, potentially requiring manual review for applications where model confidence is low or prediction uncertainty is high. Document how model uncertainty is communicated to decision-makers and incorporated into credit approval workflows.


## 8. Appendix: Regulatory Citations

### External Regulatory Citations

- FHFA AB 2022-02, Section II
- FHFA AB 2022-02, Section II.D
- FHFA AB 2022-02, Section III.A
- FHFA AB 2022-02, Section III.D
- FHFA AB 2022-02, Section IV
- SR 11-7 and Meridian MRM Policy, Section 3.2
- SR 11-7, Section IV
- SR 11-7, Section V

### Internal Policy Citations

- Meridian AI Governance Policy, Section 3.1
- Meridian AI Governance Policy, Section 4.1
- Meridian AI Governance Policy, Section 4.2
- Meridian MRM Policy, Section 2.1
- Meridian MRM Policy, Section 3.2
- Meridian MRM Policy, Section 4.1
- Meridian MRM Policy, Section 4.3
- Meridian MRM Policy, Section 5
- Meridian MRM Policy, Section 6.1

---

*This assessment was generated by PolicyLens, an AI-powered risk assessment tool. All internal policy references are to Meridian Financial Group, a fictional entity. All data is synthetic. This report is for demonstration purposes only and does not constitute legal, regulatory, or compliance advice.*