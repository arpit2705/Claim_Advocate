// Realistic mock data for development and demo purposes

export const mockReadinessResult = {
  readiness_score: 82,
  rule_results: [
    {
      rule_name: "Claim filed within notification period",
      passed: true,
      explanation: "The claim was filed within the 30-day notification window specified in Clause 4.2. Date of incident: 2024-01-15, Date of notification: 2024-01-22 (7 days)."
    },
    {
      rule_name: "Required medical documentation present",
      passed: true,
      explanation: "Discharge summary from authorized hospital is present with matching patient details and diagnosis codes per Clause 5.1."
    },
    {
      rule_name: "Pre-authorization obtained for planned procedure",
      passed: false,
      explanation: "No pre-authorization letter found. Clause 6.3 requires written pre-authorization for planned hospitalizations exceeding ₹50,000. The claimed amount is ₹1,25,000."
    },
    {
      rule_name: "Waiting period satisfied",
      passed: true,
      explanation: "Policy inception date: 2022-06-01. Claim date: 2024-01-15. The 2-year waiting period for pre-existing conditions (Clause 3.4) has been satisfied."
    },
    {
      rule_name: "Claim amount within policy sub-limits",
      passed: false,
      explanation: "Room rent claimed (₹8,000/day) exceeds the sub-limit of ₹5,000/day specified in Clause 7.2 for the selected plan tier."
    }
  ],
  contradictions: [
    {
      field: "admission_date",
      value_a: "2024-01-15",
      source_a: "Hospital Discharge Summary",
      value_b: "2024-01-16",
      source_b: "Claim Application Form",
      severity: "medium",
      note: "Inconsistent admission dates between documents — requires verification"
    }
  ],
  missing_evidence: [
    "Pre-authorization letter for planned hospitalization",
    "Original diagnostic lab reports referenced in discharge summary",
    "Pharmacy bills with itemized medication list"
  ],
  prioritized_fixes: [
    "Obtain pre-authorization letter or provide emergency admission evidence to satisfy Clause 6.3 — this is the most impactful gap affecting your readiness score.",
    "Resolve the admission date discrepancy between your discharge summary (Jan 15) and claim form (Jan 16) — contradictions can trigger additional scrutiny.",
    "Request itemized pharmacy bills from the hospital billing department — missing bills may result in partial claim rejection.",
    "Collect original lab reports referenced in the discharge summary — photocopies or digital reports from the diagnostic center are acceptable."
  ],
  grounded: true,
  scoring_model_note: "Prototype weighted scoring model — not a certified readiness determination."
};

export const mockAdjudicationResult = {
  verdict: {
    verdict: "likely_misapplied",
    consistency_score: 3,
    matched_clause_id: "CLAUSE-4.2.1",
    mismatch_explanation: "The insurer cited Clause 4.2.1 (pre-existing condition exclusion with 48-month waiting period), but the policy document specifies a 24-month waiting period for Category II conditions. The policyholder's condition (Type 2 Diabetes) is listed as Category II in Schedule A. The policy was active for 30 months at the time of claim, satisfying the 24-month requirement. The rejection appears to have applied the 48-month waiting period meant for Category I conditions.",
    pass_results: [
      "Pass 1: The rejection cites a 48-month waiting period, but the matched clause specifies 24 months for Category II conditions. Verdict: likely_misapplied.",
      "Pass 2: Schedule A classifies Type 2 Diabetes as Category II. The 48-month period applies only to Category I. The policy has been active for 30 months, exceeding the 24-month threshold. Verdict: likely_misapplied.",
      "Pass 3: Cross-referencing clause 4.2.1 with Schedule A confirms the condition category. The insurer appears to have applied the wrong waiting period tier. Verdict: likely_misapplied."
    ]
  },
  contradictions: [],
  rule_results: [
    {
      rule_name: "Waiting period verification",
      passed: true,
      explanation: "Policy active for 30 months. Category II waiting period is 24 months per Clause 4.2.1. Requirement satisfied."
    },
    {
      rule_name: "Condition category classification",
      passed: true,
      explanation: "Type 2 Diabetes is listed as Category II in Schedule A of the policy document."
    },
    {
      rule_name: "Clause reference accuracy",
      passed: false,
      explanation: "The insurer's rejection letter references a 48-month waiting period under Clause 4.2.1, but this clause specifies 24 months for Category II conditions."
    }
  ],
  grounded: true,
  explanation: "The rejection appears to have been issued based on an incorrect application of the waiting period. The insurer applied the 48-month waiting period (applicable to Category I pre-existing conditions) to a Category II condition (Type 2 Diabetes). According to the policy's own classification in Schedule A, Type 2 Diabetes falls under Category II, which carries a 24-month waiting period. Since the policy has been active for 30 months, the waiting period requirement has been met.",
  appeal_letter: `To,
The Claims Department
[Insurance Company Name]
[Address]

Date: ${new Date().toLocaleDateString('en-IN', { year: 'numeric', month: 'long', day: 'numeric' })}

Subject: Appeal Against Claim Rejection — Policy No. [POLICY_NUMBER], Claim Ref. [CLAIM_REF]

Dear Sir/Madam,

I am writing to formally appeal the rejection of my health insurance claim referenced above, issued on [REJECTION_DATE].

The rejection letter states that my claim was denied under Clause 4.2.1, citing a 48-month waiting period for pre-existing conditions. However, upon careful review of my policy document, I believe this rejection has been issued based on an incorrect application of the policy terms.

GROUNDS FOR APPEAL:

1. Condition Classification: My condition (Type 2 Diabetes) is classified as a Category II pre-existing condition under Schedule A of the policy document. Category II conditions carry a waiting period of 24 months, not 48 months.

2. Waiting Period Satisfied: My policy was incepted on [INCEPTION_DATE], and the claim was filed 30 months after inception. This exceeds the applicable 24-month waiting period for Category II conditions.

3. Incorrect Waiting Period Applied: The rejection appears to have applied the 48-month waiting period, which is specified for Category I conditions only. This does not apply to my diagnosed condition as classified in the policy's own Schedule A.

SUPPORTING EVIDENCE:
- Policy Document: Schedule A, page [X], listing Type 2 Diabetes as Category II
- Policy Document: Clause 4.2.1, specifying 24-month waiting period for Category II
- Policy inception certificate confirming coverage start date
- Medical records confirming diagnosis and treatment dates

I respectfully request that you review this claim in light of the correct policy provisions and reconsider the rejection.

I am available to provide any additional documentation required for this review.

Yours faithfully,
[POLICYHOLDER_NAME]
[CONTACT_DETAILS]`
};

export const mockReadinessResultValid = {
  readiness_score: 96,
  rule_results: [
    {
      rule_name: "Claim filed within notification period",
      passed: true,
      explanation: "Claim filed within 48 hours of incident as required by Clause 3.1."
    },
    {
      rule_name: "Required documentation complete",
      passed: true,
      explanation: "All required documents including FIR, medical certificate, and damage assessment report are present."
    },
    {
      rule_name: "Claim amount within coverage limits",
      passed: true,
      explanation: "Claimed amount of ₹2,50,000 is within the policy coverage limit of ₹5,00,000."
    }
  ],
  contradictions: [],
  missing_evidence: [],
  prioritized_fixes: [
    "Consider adding photographs of the incident scene for faster processing, though this is not strictly required."
  ],
  grounded: true,
  scoring_model_note: "Prototype weighted scoring model — not a certified readiness determination."
};

export const mockAdjudicationResultValid = {
  verdict: {
    verdict: "valid",
    consistency_score: 3,
    matched_clause_id: "CLAUSE-8.1",
    mismatch_explanation: "The rejection correctly applies Clause 8.1 which excludes coverage for incidents occurring while the policyholder is under the influence of alcohol. Blood alcohol evidence in the FIR supports this determination.",
    pass_results: [
      "Pass 1: Clause 8.1 exclusion for alcohol-related incidents is correctly applied. Evidence supports the insurer's determination. Verdict: valid.",
      "Pass 2: FIR report confirms blood alcohol level above the policy threshold. Exclusion clause is applicable. Verdict: valid.",
      "Pass 3: The rejection aligns with the policy's explicit exclusion criteria. No misapplication identified. Verdict: valid."
    ]
  },
  contradictions: [],
  rule_results: [
    {
      rule_name: "Exclusion clause applicability",
      passed: true,
      explanation: "Clause 8.1 alcohol exclusion is applicable based on FIR evidence."
    }
  ],
  grounded: true,
  explanation: "The rejection is consistent with the policy terms. Clause 8.1 explicitly excludes coverage for incidents where the policyholder is found to be under the influence of alcohol, and the evidence on file (FIR report) supports this finding. While this may be a difficult outcome, the insurer's application of the policy clause appears correct.",
  appeal_letter: null
};
