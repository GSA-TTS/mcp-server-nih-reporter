# NIH Spending Categories — Appendix I (FY2024)

**Source:** NIH RePORTER API Data Elements V2  
https://api.reporter.nih.gov/documents/Data%20Elements%20for%20RePORTER%20Project%20API_V2.pdf

---

## Purpose

Use this skill whenever a query involves filtering NIH grants by spending category. It provides:

1. The complete ID ↔ name mapping for all FY2024 Appendix I spending categories
2. Rules for resolving a plain-English topic to a valid category ID
3. The semantics of the `spending_categories` filter field

---

## Resolving a Category Name to an ID

**Never guess or invent a category ID.** Follow this resolution order:

1. **Exact integer** — if the value is already an integer in the table below, use it directly.
2. **Exact name match** — compare case-insensitively against the Name column.
3. **Normalized match** — strip punctuation, collapse whitespace, compare lowercase.
4. **No match / ambiguous** — call the `search_spending_categories` tool with a plain-English term (e.g. `"aging"`, `"breast cancer"`) to discover valid IDs before proceeding.

If a value cannot be resolved to a confirmed ID in this table, **do not use it**. Raise an error or call `search_spending_categories` first.

---

## `spending_categories` Filter Semantics

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `values` | `List[int]` | Yes | — | One or more valid FY2024 spending category IDs |
| `match_all` | `bool` | No | `false` | `true` → project must match **all** IDs; `false` → match **at least one** |

- `values` must contain at least one entry.
- Duplicate IDs are silently removed; order is preserved.
- Strings that are digit-only (e.g. `"224"`) are accepted and converted to `int`.
- Strings that match a category name (exact or normalized) are accepted and converted to the corresponding ID.
- Any value that cannot be resolved is an error.

---

## Complete FY2024 Category Table (Appendix I)

| ID | Name |
|----|------|
| 2597 | Acquired Cognitive Impairment |
| 24 | Acute Respiratory Distress Syndrome |
| 27 | Adolescent Sexual Activity |
| 30 | Agent Orange & Dioxin |
| 31 | Aging |
| 36 | Alcoholism, Alcohol Use and Health |
| 39 | Allergic Rhinitis (Hay Fever) |
| 40 | Alzheimer's Disease |
| 3246 | Alzheimer's Disease including Alzheimer's Disease Related Dementias (AD/ADRD) |
| 3254 | Alzheimer's Disease Related Dementias (ADRD) |
| 44 | American Indian or Alaska Native |
| 19 | Amyotrophic Lateral Sclerosis (ALS) |
| 47 | Anorexia |
| 48 | Anthrax |
| 50 | Antimicrobial Resistance |
| 2610 | Anxiety Disorders |
| 51 | Aphasia |
| 54 | Arctic |
| 55 | Arthritis |
| 58 | Assistive Technology |
| 59 | Asthma |
| 64 | Ataxia Telangiectasia |
| 65 | Atherosclerosis |
| 66 | Attention Deficit Hyperactivity Disorder (ADHD) |
| 67 | Autism |
| 69 | Autoimmune Disease |
| 3454 | Back Pain |
| 81 | Basic Behavioral and Social Science |
| 84 | Batten Disease |
| 89 | Behavioral and Social Science |
| 98 | Biodefense and Related Countermeasures |
| 101 | Bioengineering |
| 229 | Biomedical Imaging |
| 108 | Biotechnology |
| 2595 | Bipolar Disorder |
| 117 | Brain Cancer |
| 118 | Brain Disorders |
| 120 | Breast Cancer |
| 3932 | Breastfeeding, Lactation and Breast Milk |
| 5654 | Building Research Capacity at Institutions with Limited NIH Funding |
| 123 | Burden of Illness |
| 3461 | Cachexia |
| 132 | Cancer |
| 1393 | Cancer Genomics |
| 2609 | Cannabidiol Research |
| 2601 | Cannabinoid Research |
| 140 | Cardiovascular |
| 3491 | Caregiving Research |
| 4975 | Celiac Disease |
| 144 | Cerebral Palsy |
| 3466 | Cerebrovascular |
| 146 | Cervical Cancer |
| 157 | Charcot-Marie-Tooth Disease |
| 162 | Child Abuse and Neglect Research |
| 373 | Childhood Injury |
| 163 | Childhood Leukemia |
| 4268 | Childhood Obesity |
| 170 | Chronic Fatigue Syndrome (ME/CFS) |
| 171 | Chronic Liver Disease and Cirrhosis |
| 172 | Chronic Obstructive Pulmonary Disease |
| 616 | Chronic Pain |
| 296 | Climate-Related Exposures and Conditions |
| 176 | Clinical Research |
| 180 | Clinical Trials and Supportive Activities |
| 5224 | Cocaine |
| 183 | Colorectal Cancer |
| 187 | Comparative Effectiveness Research |
| 191 | Complementary and Integrative Health |
| 196 | Conditions Affecting the Embryonic and Fetal Periods |
| 3533 | Congenital Heart Disease |
| 2037 | Congenital Muscular Dystrophy |
| 2382 | Congenital Structural Anomalies |
| 197 | Contraception/Reproduction |
| 200 | Cooley's Anemia |
| 4835 | Coronaviruses |
| 5009 | Coronaviruses Diagnostics and Prognostics |
| 5011 | Coronaviruses Disparities and At-Risk Populations |
| 5005 | Coronaviruses Therapeutics and Interventions |
| 5014 | Coronaviruses Vaccines |
| 201 | Cost Effectiveness Research |
| 204 | Crohn's Disease |
| 206 | Cystic Fibrosis |
| 4531 | Data Science |
| 2067 | Dementia |
| 216 | Dental, Oral, and Craniofacial Disease |
| 219 | Depression |
| 224 | Diabetes |
| 3527 | Dietary Supplements |
| 231 | Diethylstilbestrol (DES) |
| 232 | Digestive Diseases |
| 233 | Digestive Diseases - (Gallbladder) |
| 234 | Digestive Diseases - (Peptic Ulcer) |
| 5745 | Disability Research |
| 4998 | Dissemination and Implementation Research |
| 238 | Down Syndrome |
| 240 | Drug Abuse (NIDA only) |
| 241 | Duchenne/ Becker Muscular Dystrophy |
| 242 | Dystonia |
| 243 | Eating Disorders |
| 2600 | Eczema / Atopic Dermatitis |
| 4721 | Electronic Nicotine Delivery Systems |
| 2375 | Emergency Care |
| 246 | Emerging Infectious Diseases |
| 248 | Emphysema |
| 3460 | Endocannabinoid System Research |
| 3529 | Endocrine Disruptors |
| 250 | Endometriosis |
| 255 | Epilepsy |
| 4714 | Esophageal Cancer |
| 257 | Estrogen |
| 259 | Eye Disease and Disorders of Vision |
| 262 | Facioscapulohumeral Muscular Dystrophy |
| 5724 | Fentanyl Misuse and Addiction |
| 263 | Fetal Alcohol Spectrum Disorders (FASD) |
| 264 | Fibroid Tumors (Uterine) |
| 265 | Fibromyalgia |
| 4465 | Firearms Research |
| 1389 | Food Allergies |
| 267 | Foodborne Illness |
| 268 | Fragile X Syndrome |
| 269 | Frontotemporal Dementia (FTD) |
| 272 | Gene Therapy |
| 273 | Gene Therapy Clinical Trials |
| 275 | Genetic Testing |
| 276 | Genetics |
| 5552 | Harm Reduction for Substance Misuse |
| 292 | Headaches |
| 5599 | Health Disparities and Racial or Ethnic Minority Health Research |
| 5546 | Health Disparities Research |
| 3180 | Health Effects of Household Energy Combustion |
| 2376 | Health Effects of Indoor Air Pollution |
| 298 | Health Services |
| 4511 | Hearing Loss |
| 299 | Heart Disease |
| 300 | Heart Disease - Coronary Heart Disease |
| 306 | Hematology |
| 307 | Hepatitis |
| 308 | Hepatitis - A |
| 309 | Hepatitis - B |
| 310 | Hepatitis - C |
| 284 | HIV/AIDS |
| 312 | Hodgkin's Disease |
| 313 | Homelessness |
| 314 | Homicide and Legal Interventions |
| 289 | HPV and/or Cervical Cancer Vaccines |
| 318 | Human Fetal Tissue |
| 320 | Human Genome |
| 325 | Huntington's Disease |
| 1791 | Hydrocephalus |
| 326 | Hyperbaric Oxygen |
| 327 | Hypertension |
| 331 | Immunization |
| 3999 | Immunotherapy |
| 3085 | Infant Mortality |
| 338 | Infectious Diseases |
| 341 | Infertility |
| 342 | Inflammatory Bowel Disease |
| 343 | Influenza |
| 453 | Intellectual and Developmental Disabilities (IDD) |
| 380 | Interstitial Cystitis |
| 385 | Kidney Disease |
| 395 | Lead Poisoning |
| 2438 | Lewy Body Dementia |
| 399 | Liver Cancer |
| 400 | Liver Disease |
| 408 | Lung |
| 409 | Lung Cancer |
| 410 | Lupus |
| 411 | Lyme Disease |
| 5044 | Lymphatic Research |
| 5024 | Lymphedema |
| 413 | Lymphoma |
| 4372 | Machine Learning and Artificial Intelligence |
| 436 | Macular Degeneration |
| 2613 | Major Depressive Disorder |
| 437 | Malaria |
| 438 | Malaria Vaccine |
| 3810 | Maternal Health |
| 4764 | Maternal Morbidity and Mortality |
| 5555 | Menopause |
| 443 | Mental Health |
| 3445 | Mental Illness |
| 458 | Methamphetamine |
| 4243 | Microbiome |
| 465 | Migraines |
| 473 | Mucopolysaccharidoses (MPS) |
| 474 | Multiple Sclerosis |
| 475 | Muscular Dystrophy |
| 479 | Myasthenia Gravis |
| 480 | Myotonic Dystrophy |
| 496 | Nanotechnology |
| 5562 | Natural Products |
| 3453 | Neck Pain |
| 687 | Neonatal Respiratory Distress |
| 329 | Networking and Information Technology R&D (NITRD) |
| 1375 | Neuroblastoma |
| 520 | Neurodegenerative |
| 521 | Neurofibromatosis |
| 525 | Neurosciences |
| 536 | Nutrition |
| 551 | Obesity |
| 4076 | Opioid Misuse and Addiction |
| 3951 | Opioids |
| 555 | Organ Transplantation |
| 556 | Orphan Drug |
| 789 | Orthopoxviruses |
| 2599 | Osteoarthritis |
| 559 | Osteogenesis Imperfecta |
| 560 | Osteoporosis |
| 563 | Otitis Media |
| 564 | Ovarian Cancer |
| 615 | Paget's Disease |
| 618 | Pain Research |
| 620 | Palliative Care |
| 1391 | Pancreatic Cancer |
| 624 | Parkinson's Disease |
| 1254 | Patient Safety |
| 679 | Pediatric |
| 680 | Pediatric - AIDS |
| 2310 | Pediatric Cancer |
| 3520 | Pediatric Cardiomyopathy |
| 685 | Pelvic Inflammatory Disease |
| 689 | Perinatal Period - Conditions Originating in Perinatal Period |
| 524 | Peripheral Neuropathy |
| 3395 | Physical Activity |
| 372 | Physical Injury - Accidents and Adverse Effects |
| 2346 | Physical Rehabilitation |
| 692 | Pneumonia |
| 693 | Pneumonia and Influenza |
| 696 | Polycystic Kidney Disease |
| 5231 | Polycystic Ovary Syndrome (PCOS) |
| 5194 | Post-Acute Sequelae of SARS-CoV-2 infection (PASC) including Long COVID |
| 1991 | Post-Traumatic Stress Disorder (PTSD) |
| 4711 | Postural Orthostatic Tachycardia Syndrome |
| 3070 | Precision Medicine |
| 3920 | Pregnancy |
| 700 | Prescription Drug Misuse |
| 686 | Preterm, Low Birth Weight and Health of the Newborn |
| 701 | Prevention |
| 5592 | Primary Health Care |
| 5804 | Primary Immunodeficiencies |
| 703 | Prostate Cancer |
| 704 | Psoriasis |
| 5773 | Psychosis |
| 5232 | Pulmonary Fibrosis |
| 5286 | Pulmonary Hypertension |
| 5544 | Racial and Ethnic Minority Health Research |
| 1859 | Radiation Oncology |
| 729 | Rare Diseases |
| 5551 | Recovery Support Services |
| 731 | Regenerative Medicine |
| 732 | Rehabilitation |
| 737 | Rett Syndrome |
| 2611 | Rheumatoid Arthritis |
| 770 | Rural Health |
| 5264 | Sarcoidosis |
| 3475 | Sarcopenia |
| 777 | Schizophrenia |
| 779 | Scleroderma |
| 780 | Screening and Brief Intervention for Substance Misuse |
| 781 | Sepsis |
| 2343 | Serious Mental Illness |
| 784 | Sexually Transmitted Infections |
| 785 | Sickle Cell Disease |
| 5789 | Skin Cancer |
| 788 | Sleep Research |
| 4793 | Social Determinants of Health |
| 792 | Spina Bifida |
| 793 | Spinal Cord Injury |
| 794 | Spinal Muscular Atrophy |
| 796 | Stem Cell Research |
| 797 | Stem Cell Research - Embryonic - Human |
| 798 | Stem Cell Research - Embryonic - Non-Human |
| 799 | Stem Cell Research - Induced Pluripotent Stem Cell |
| 800 | Stem Cell Research - Induced Pluripotent Stem Cell - Human |
| 801 | Stem Cell Research - Induced Pluripotent Stem Cell - Non-Human |
| 802 | Stem Cell Research - Nonembryonic - Human |
| 803 | Stem Cell Research - Nonembryonic - Non-Human |
| 804 | Stem Cell Research - Umbilical Cord Blood/ Placenta |
| 805 | Stem Cell Research - Umbilical Cord Blood/ Placenta - Human |
| 808 | Stem Cell Research - Umbilical Cord Blood/ Placenta - Non-Human |
| 5225 | Stimulant Use and Misuse |
| 4758 | Stomach Cancer |
| 811 | Stroke |
| 817 | Substance Misuse |
| 819 | Substance Misuse Prevention |
| 822 | Sudden Infant Death Syndrome |
| 823 | Suicide |
| 824 | Suicide Prevention |
| 830 | Teenage Pregnancy |
| 4990 | Telehealth |
| 831 | Temporomandibular Muscle/Joint Disorder (TMJD) |
| 2607 | Therapeutic Cannabinoid Research |
| 4989 | Tickborne Diseases |
| 852 | Tobacco |
| 791 | Tobacco Smoke and Health |
| 853 | Topical Microbicides |
| 854 | Tourette Syndrome |
| 861 | Transmissible Spongiform Encephalopathy (TSE) |
| 862 | Transplantation |
| 375 | Traumatic Brain Injury (TBI) |
| 374 | Traumatic Head and Spine Injury |
| 864 | Tuberculosis |
| 865 | Tuberculosis Vaccine |
| 866 | Tuberous Sclerosis |
| 867 | Underage Drinking |
| 3265 | Underage Drinking - Prevention & Treatment (NIAAA Only) |
| 376 | Unintentional Childhood Injury |
| 871 | Urologic Diseases |
| 2334 | Usher Syndrome |
| 873 | Uterine Cancer |
| 877 | Vaccine Related |
| 878 | Vaccine Related - AIDS |
| 1873 | Vaginal Cancer |
| 2339 | Valley Fever |
| 2412 | Vascular Contributions to Cognitive Impairment and Dementia (VCID) |
| 881 | Vector-Borne Diseases |
| 883 | Violence Against Women |
| 884 | Violence Research |
| 889 | Vulvodynia |
| 891 | West Nile Virus |
| 5815 | Women's Health Research |
| 4924 | Wound Healing and Care |
| 897 | Youth Violence |
| 898 | Youth Violence Prevention |
| 3617 | Zika Virus |

---

## Matching Tips

Some categories have close relatives — use the most specific applicable ID:

- **Alzheimer's:** `40` (AD only) · `3254` (ADRD only) · `3246` (AD/ADRD combined)
- **Dementia (general):** `2067`
- **Cancer (general):** `132` — use more specific IDs when topic is narrow (e.g. `120` Breast Cancer, `409` Lung Cancer)
- **Cannabinoids:** `2601` (general) · `2609` (CBD) · `2607` (therapeutic) · `3460` (endocannabinoid system)
- **Coronaviruses:** `4835` (general) · `5009` (dx/px) · `5011` (disparities) · `5005` (therapeutics) · `5014` (vaccines)
- **Stem cells:** multiple sub-categories under `796` — prefer the most specific
- **Substance misuse:** `817` (general) · `819` (prevention) · `700` (prescription) · `240` (NIDA) · `780` (screening/brief intervention) · `5552` (harm reduction) · `5551` (recovery)
- **Health disparities:** `5546` (general) · `5544` (racial/ethnic) · `5599` (combined)
- **Opioids:** `3951` (general) · `4076` (misuse/addiction)
- **Depression:** `219` (general) · `2613` (major depressive disorder)
- **Mental health:** `443` (general) · `3445` (mental illness) · `2343` (serious mental illness)
