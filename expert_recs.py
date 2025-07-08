def get_expert_recommendation(tumor_type, stage):
    """Generate clinically valid treatment recommendations."""
    recommendations = {
        'glioma': {
            'Stage I': (
                "Treatment: Maximal safe resection\n"
                "Radiation: Consider 54–60 Gy for high‑risk features\n"
                "Monitoring: MRI every 3 months for 2 years\n"
                "Molecular Testing: IDH1/2, 1p/19q, MGMT promoter\n"
                "Clinical Trials: IDH inhibitor trials if mutation present"
            ),
            'Stage II': (
                "Treatment: Surgical resection + Radiation + Temozolomide\n"
                "Protocol: 60 Gy in 30 fractions with concurrent TMZ\n"
                "Adjuvant: 6 cycles TMZ (150–200 mg/m²)\n"
                "Monitoring: MRI monthly for 6 months, then quarterly"
            ),
            'Stage III': (
                "Treatment: Aggressive resection + Chemoradiation\n"
                "Advanced Options: TTFields therapy\n"
                "Clinical Trials: Immunotherapy trials\n"
                "Palliative Care: Early integration for symptom management"
            ),
            'Stage IV': (
                "Multimodal Approach: Surgery if feasible + Chemoradiation\n"
                "Systemic Therapy: Bevacizumab for symptomatic edema\n"
                "Clinical Trials: Targeted therapies\n"
                "Supportive Care: Corticosteroids, antiseizure medications"
            )
        },
        'meningioma': {
            'Stage I': (
                "Approach: Observation for asymptomatic tumors\n"
                "Surgical Option: Simpson Grade I resection\n"
                "Radiation: Not typically indicated\n"
                "Monitoring: Annual MRI for 5 years"
            ),
            'Stage II': (
                "Treatment: Gross total resection\n"
                "Adjuvant: Fractionated radiotherapy (50–54 Gy) if subtotal\n"
                "Follow‑up: MRI every 6 months for 3 years\n"
                "Genetic Testing: NF2, SMARCE1 mutations"
            ),
            'Stage III': (
                "Treatment: Multimodal resection + Radiation\n"
                "Advanced Options: Proton beam therapy\n"
                "Medical Therapy: Everolimus for NF2‑mutated tumors\n"
                "Clinical Trials: VEGF inhibitors (Bevacizumab)"
            )
        },
        'pituitary': {
            'Stage I': (
                "First‑line: Transsphenoidal surgery\n"
                "Medical Management: Dopamine agonists for prolactinomas\n"
                "Hormonal Assessment: Complete endocrine workup\n"
                "Monitoring: Hormonal panels at 6 weeks, MRI at 3 months"
            ),
            'Stage II': (
                "Surgical Approach: Endoscopic endonasal resection\n"
                "Radiation: Stereotactic radiosurgery for residuals\n"
                "Medical Therapy: Somatostatin analogs for GH‑secreting tumors\n"
                "Hormonal Replacement: As needed for deficiencies"
            ),
            'Stage III': (
                "Management: Multidisciplinary team approach\n"
                "Surgical Strategy: Staged procedures with skull base team\n"
                "Medical Therapy: Temozolomide for aggressive tumors\n"
                "Radiation: Fractionated radiotherapy near optic structures"
            )
        }
    }
    # Return the matching recommendation or a default message
    return recommendations.get(tumor_type, {}).get(stage,
        "Consult a multidisciplinary neuro‑oncology team for a personalized management plan."
    )