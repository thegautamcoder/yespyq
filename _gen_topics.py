#!/usr/bin/env python3
"""Generate 50 UPSC topic explainer blog posts under /blog/<slug>/.
Original factual content — schemes, polity, economy, environment, IR, sci-tech
and trending topics. Each: Article + BreadcrumbList + FAQPage JSON-LD.
Run from repo root: python3 _gen_topics.py
"""
import os, re
BASE = "https://yespyq.com"
TODAY = "2026-07-05"
ROOT = os.path.dirname(os.path.abspath(__file__))

# Each topic: slug, tag, title, h1, desc, keywords, read, cta(subject slug or /pyq/),
# intro, sections [(h2, html)], why (UPSC angle html), faq [(q,a)]
T = [
 {"slug":"national-education-policy-2020","tag":"Policy","read":"7 min read","cta":"/pyq/",
  "title":"National Education Policy 2020 (NEP): Key Features Explained",
  "h1":"National Education Policy 2020 (NEP 2020)","kw":"NEP 2020, National Education Policy, NEP 2020 UPSC, 5+3+3+4 structure, education policy India",
  "desc":"National Education Policy 2020 (NEP) explained for UPSC — the 5+3+3+4 school structure, mother-tongue instruction, multidisciplinary higher education and key targets.",
  "intro":"The National Education Policy 2020 (NEP) is India's first comprehensive education policy in over three decades, replacing the National Policy on Education of 1986. Approved by the Union Cabinet in July 2020 and drafted by a committee headed by Dr. K. Kasturirangan, it lays out a roadmap to transform schooling and higher education by 2040. Its guiding themes are flexibility, foundational learning, the use of Indian languages, and a shift from rote learning towards conceptual understanding, critical thinking and skills.",
  "tldr":"NEP 2020 is India's new education policy (replacing the 1986 policy). It introduces a 5+3+3+4 school structure, mother-tongue instruction till at least Grade 5, a multidisciplinary higher-education model, and targets a 50% Gross Enrolment Ratio in higher education by 2035.",
  "facts":[("Announced","July 2020 (replaces 1986 policy)"),("Drafting committee","Chaired by Dr. K. Kasturirangan"),("School structure","5+3+3+4 (ages 3–18)"),("Medium of instruction","Mother tongue/regional language till at least Grade 5"),("Higher-ed GER target","50% by 2035"),("Spending goal","6% of GDP on education")],
  "sec":[("The 5+3+3+4 school structure","NEP replaces the old 10+2 structure with a 5+3+3+4 design — the Foundational stage (ages 3–8), Preparatory (8–11), Middle (11–14) and Secondary (14–18) stages. Crucially, it brings early childhood care and education (ages 3–6) into the formal school system for the first time, recognising that over 85% of a child's brain development occurs before age six."),
    ("Language and foundational literacy","The policy stresses the mother tongue, local or regional language as the medium of instruction at least until Grade 5 (preferably till Grade 8), while retaining flexibility. It sets universal Foundational Literacy and Numeracy (FLN) as an urgent national mission, operationalised through the NIPUN Bharat programme, aiming for every child to attain basic reading and arithmetic by Grade 3."),
    ("A flexible, multidisciplinary curriculum","NEP reduces curriculum content to core essentials, removes rigid separations between arts, science, commerce and vocational streams, and introduces vocational exposure with internships from Grade 6. Board exams are to be made 'low-stakes', and a new National Curriculum Framework and 360-degree holistic progress card replace one-time high-pressure assessment."),
    ("Higher education reforms","For higher education, NEP proposes a broad-based multidisciplinary approach, a single overarching regulator — the Higher Education Commission of India (HECI) — replacing bodies like the UGC and AICTE, multiple entry and exit points backed by an Academic Bank of Credits, and a four-year undergraduate degree with research. It targets raising the Gross Enrolment Ratio in higher education from around 27% to 50% by 2035."),
    ("Targets and implementation","The policy aims to raise public spending on education to 6% of GDP, set up institutions like the National Research Foundation to fund research, and internationalise education by allowing top foreign universities to operate in India. As education is on the Concurrent List, implementation depends on cooperation between the Centre and the states.")],
  "why":"NEP 2020 is heavily tested in both Prelims (factual features like the 5+3+3+4 structure, the GER target, the 6% of GDP goal, HECI) and Mains (education reform, cooperative federalism, the medium-of-instruction debate). It also recurs in current affairs whenever implementation steps — new curriculum frameworks, NIPUN Bharat targets or foreign-university rules — are announced.",
  "take":["NEP 2020 replaces the 1986 policy and was drafted by the Kasturirangan committee.","The 5+3+3+4 structure formally brings ages 3–6 (early childhood) into schooling.","Mother-tongue instruction is recommended till at least Grade 5; FLN is delivered via NIPUN Bharat.","Higher education moves to a multidisciplinary model with HECI, an Academic Bank of Credits and a 50% GER target by 2035.","The policy aims for public education spending of 6% of GDP."],
  "faq":[("What is the new school structure under NEP 2020?","NEP 2020 replaces 10+2 with a 5+3+3+4 structure covering ages 3 to 18 — Foundational (3–8), Preparatory (8–11), Middle (11–14) and Secondary (14–18) — bringing early childhood care and education into the formal system."),
    ("What is the higher-education GER target of NEP 2020?","NEP 2020 aims to raise the Gross Enrolment Ratio in higher education to 50% by 2035."),
    ("Which body will replace the UGC and AICTE under NEP 2020?","The policy proposes a single regulator, the Higher Education Commission of India (HECI), with separate verticals for regulation, accreditation, funding and academic standards."),
    ("How much of GDP does NEP 2020 want spent on education?","NEP 2020 recommends raising public investment in education to 6% of GDP.")]},

 {"slug":"pm-kisan-scheme","tag":"Scheme","read":"6 min read","cta":"/pyq/economy/",
  "title":"PM-KISAN Scheme: Objectives and Benefits Explained",
  "h1":"PM-KISAN Scheme","kw":"PM-KISAN, PM Kisan Samman Nidhi, PM-KISAN UPSC, farmer income support scheme",
  "desc":"PM-KISAN (Pradhan Mantri Kisan Samman Nidhi) explained for UPSC — a central-sector income-support scheme giving eligible farmer families ₹6,000 a year in three instalments.",
  "intro":"Pradhan Mantri Kisan Samman Nidhi (PM-KISAN) is a central-sector scheme launched in February 2019 to provide direct income support to landholding farmer families across India. Administered by the Ministry of Agriculture and Farmers Welfare, it is one of the largest Direct Benefit Transfer (DBT) programmes in the world, covering more than 11 crore farmers and designed to supplement their financial needs for buying seeds, fertiliser, equipment and other inputs.",
  "tldr":"PM-KISAN is a 100% centrally funded income-support scheme that gives eligible landholding farmer families ₹6,000 a year in three equal ₹2,000 instalments, paid directly into their bank accounts through Aadhaar-linked Direct Benefit Transfer.",
  "facts":[("Launched","February 2019 (effective December 2018)"),("Ministry","Agriculture and Farmers Welfare"),("Benefit","₹6,000/year in 3 instalments of ₹2,000"),("Funding","100% central-sector scheme"),("Transfer mode","Aadhaar-linked DBT"),("Beneficiaries","Landholding farmer families")],
  "sec":[("What the scheme provides","Eligible farmer families receive ₹6,000 per year, paid in three equal instalments of ₹2,000 every four months, transferred directly into their bank accounts via Direct Benefit Transfer (DBT). The support is unconditional income assistance, meaning it is not tied to the size of landholding beyond the eligibility threshold."),
    ("Who is eligible","It covers all landholding farmer families, subject to exclusion criteria. Excluded categories include income-tax payers, institutional landholders, serving and retired government employees above a certain rank, professionals like doctors and lawyers, and constitutional post-holders. Eligibility is verified through land records and Aadhaar seeding."),
    ("Central-sector vs centrally-sponsored","PM-KISAN is a central-sector scheme, meaning it is 100% funded by the Union government with no state contribution. This distinguishes it from centrally-sponsored schemes (like MGNREGA), where costs are shared between the Centre and states — a distinction frequently tested in Prelims."),
    ("Significance and challenges","By using Aadhaar-linked DBT, PM-KISAN minimises leakages, eliminates middlemen and provides predictable supplementary income. It has also been linked to reforms like e-KYC and the farmer registry. Challenges include exclusion errors, incorrect land records and identifying tenant farmers, who often do not own the land they cultivate.")],
  "why":"Government schemes like PM-KISAN are frequent Prelims targets — the administering ministry, the exact benefit amount (₹6,000), the instalment structure and especially the funding pattern (central-sector vs centrally-sponsored) are commonly tested. In Mains it is a ready example for questions on direct income transfers versus subsidies and on agrarian distress.",
  "take":["PM-KISAN gives ₹6,000/year in three ₹2,000 instalments to landholding farmer families.","It is a 100% central-sector scheme (fully Union-funded), unlike centrally-sponsored schemes.","Payments use Aadhaar-linked DBT to cut leakages and middlemen.","Income-tax payers, government employees and professionals are excluded.","Tenant farmers are largely left out because the benefit is tied to land ownership."],
  "faq":[("How much does PM-KISAN provide?","₹6,000 per year in three instalments of ₹2,000 each, transferred directly to farmer families' bank accounts every four months."),
    ("Is PM-KISAN a central-sector scheme?","Yes, it is a 100% central-sector scheme fully funded by the Government of India, with no state contribution."),
    ("Which ministry runs PM-KISAN?","The Ministry of Agriculture and Farmers Welfare."),
    ("Are tenant farmers covered under PM-KISAN?","Generally no. Because the benefit is tied to land ownership records, landless tenant and sharecropper farmers are usually excluded — a key criticism of the scheme.")]},

 {"slug":"ayushman-bharat-pm-jay","tag":"Scheme","read":"6 min read","cta":"/pyq/",
  "title":"Ayushman Bharat (PM-JAY): Health Insurance Scheme Explained",
  "h1":"Ayushman Bharat (PM-JAY)","kw":"Ayushman Bharat, PM-JAY, PMJAY UPSC, health insurance scheme India, health and wellness centres",
  "desc":"Ayushman Bharat explained for UPSC — its two pillars (Health & Wellness Centres and PM-JAY), the ₹5 lakh health cover, and why it is the world's largest health-assurance scheme.",
  "intro":"Ayushman Bharat, launched in 2018, is India's flagship health initiative, designed to move the health system from a selective, fragmented approach to universal, comprehensive coverage. Anchored in the recommendations of the National Health Policy 2017 and the vision of Universal Health Coverage, it adopts a continuum-of-care approach and rests on two interconnected components — one for primary care and one for hospitalisation.",
  "tldr":"Ayushman Bharat has two pillars: Health and Wellness Centres (now Ayushman Arogya Mandirs) for primary care, and PM-JAY, which gives eligible poor and vulnerable families cashless health cover of up to ₹5 lakh per family per year for hospitalisation — making it one of the world's largest health-assurance schemes.",
  "facts":[("Launched","2018"),("Component 1","Health & Wellness Centres / Ayushman Arogya Mandirs"),("Component 2","PM-JAY (health assurance)"),("Cover","Up to ₹5 lakh per family per year"),("Care level","Secondary & tertiary hospitalisation"),("Beneficiary basis","SECC 2011 data"),("Nodal body","National Health Authority (NHA)")],
  "sec":[("Two pillars","The first pillar is Health and Wellness Centres (now rebranded Ayushman Arogya Mandirs), which upgrade sub-centres and primary health centres to deliver comprehensive primary care — including maternal and child health, non-communicable diseases, and free essential drugs and diagnostics close to people's homes. The second pillar is the Pradhan Mantri Jan Arogya Yojana (PM-JAY), a health-assurance scheme for hospitalisation."),
    ("PM-JAY cover","PM-JAY provides health cover of up to ₹5 lakh per family per year for secondary and tertiary hospitalisation to poor and vulnerable families. There is no cap on family size or age, and pre-existing conditions are covered from day one. Beneficiaries were initially identified using the deprivation and occupational criteria of the Socio-Economic Caste Census (SECC) 2011, making it one of the largest such schemes in the world."),
    ("Cashless, paperless and portable","Beneficiaries receive cashless and paperless treatment at empanelled public and private hospitals using an Ayushman card. Because coverage is portable across states, a beneficiary from one state can avail treatment in another — valuable for migrant workers. It is an entitlement-based scheme, so no enrolment is needed if a family is on the eligible list."),
    ("Governance and expansion","The scheme is implemented by the National Health Authority (NHA) at the centre and State Health Agencies in states, and is a centrally-sponsored scheme with cost sharing between the Centre and states. Coverage has been expanded over time — for example, to all citizens aged 70 and above under a dedicated vertical, regardless of income.")],
  "why":"PM-JAY details — the ₹5 lakh cover, the two pillars, SECC-based beneficiary identification, the National Health Authority and portability — are classic Prelims facts and useful Mains examples on Universal Health Coverage, out-of-pocket expenditure and welfare delivery.",
  "take":["Ayushman Bharat has two pillars: Ayushman Arogya Mandirs (primary care) and PM-JAY (hospitalisation).","PM-JAY covers up to ₹5 lakh per family per year for secondary and tertiary care, with no family-size or age cap.","Beneficiaries were identified using SECC 2011 data; the scheme is an entitlement, not enrolment-based.","Treatment is cashless, paperless and portable across states.","It is run by the National Health Authority and coverage has expanded, including to all citizens aged 70+."],
  "faq":[("What health cover does PM-JAY provide?","Up to ₹5 lakh per family per year for secondary and tertiary hospitalisation, with no cap on family size or age."),
    ("What are the two components of Ayushman Bharat?","Health and Wellness Centres (Ayushman Arogya Mandirs) for comprehensive primary care, and PM-JAY for hospitalisation cover."),
    ("Which body implements PM-JAY?","The National Health Authority (NHA) at the national level, with State Health Agencies in the states."),
    ("How are PM-JAY beneficiaries identified?","Primarily through the deprivation and occupational criteria of the Socio-Economic Caste Census (SECC) 2011, with later expansions such as cover for all citizens aged 70 and above.")]},

 {"slug":"mgnrega-explained","tag":"Scheme","read":"6 min read","cta":"/pyq/economy/",
  "title":"MGNREGA: India's Rural Employment Guarantee Explained",
  "h1":"MGNREGA (Rural Employment Guarantee)","kw":"MGNREGA, NREGA UPSC, rural employment guarantee, 100 days work, MGNREGA features",
  "desc":"MGNREGA explained for UPSC — the legal guarantee of 100 days of wage employment, its demand-driven design, social audit and role as a rural safety net.",
  "intro":"The Mahatma Gandhi National Rural Employment Guarantee Act (MGNREGA), enacted in 2005 and rolled out from 2006, provides a legal guarantee of wage employment to rural households. It transformed employment from a discretionary welfare measure into a justiciable legal right — the first law of its kind on this scale — and acts as a crucial safety net during agricultural lean seasons and economic shocks.",
  "tldr":"MGNREGA (2005) legally guarantees at least 100 days of unskilled manual wage work per year to every rural household that demands it. It is demand-driven and rights-based: if work is not provided within 15 days, an unemployment allowance must be paid. It also mandates social audits and creates durable rural assets.",
  "facts":[("Enacted","2005 (implemented from 2006)"),("Guarantee","At least 100 days of wage work per rural household/year"),("Trigger","Demand-driven (work within 15 days)"),("If work not given","Unemployment allowance payable"),("Ministry","Rural Development"),("Oversight","Social audit by Gram Sabha"),("Type","Centrally-sponsored scheme")],
  "sec":[("The 100-day guarantee","MGNREGA guarantees at least 100 days of unskilled manual wage employment in a financial year to every rural household whose adult members volunteer to do such work. In certain cases — such as households in areas affected by drought or notified calamities — the guarantee can be extended beyond 100 days. Wages are notified by the Centre and paid directly into bank or post-office accounts."),
    ("Demand-driven and rights-based","Unlike earlier employment schemes, MGNREGA is demand-driven — a household applies for a job card and requests work, and the state must provide it within 15 days, failing which an unemployment allowance becomes payable. This inversion, where the citizen's demand triggers the state's obligation, is what makes it a genuinely rights-based programme rather than a top-down scheme."),
    ("Transparency and social audit","The Act mandates social audits by the Gram Sabha, making it a landmark in participatory accountability. Records, muster rolls and payments are meant to be publicly available, and provisions like geo-tagging of assets and the National Mobile Monitoring System (NMMS) have been added to curb fraud and fake attendance."),
    ("Durable assets and impact","At least a share of works must create durable rural assets — water conservation and harvesting structures, drought-proofing, rural connectivity, and land development — linking employment to productive infrastructure. Studies credit MGNREGA with raising rural wages, reducing distress migration and empowering women, who make up a large share of workers, though delays in wage payment remain a persistent criticism.")],
  "why":"MGNREGA is a perennial favourite — its legal 100-day guarantee, demand-driven design, the 15-day rule and unemployment allowance, the Gram Sabha social audit and its role as a countercyclical safety net are all commonly tested in Prelims and provide rich Mains material on rights-based governance and rural development.",
  "take":["MGNREGA (2005) guarantees at least 100 days of wage work per rural household per year.","It is demand-driven: work must be given within 15 days, else an unemployment allowance is due.","Social audit by the Gram Sabha is legally mandated, making it a model of accountability.","Works must create durable rural assets like water-conservation structures.","It is a centrally-sponsored scheme run by the Ministry of Rural Development; delayed wages are a key criticism."],
  "faq":[("How many days of employment does MGNREGA guarantee?","At least 100 days of unskilled manual wage employment per rural household per financial year, extendable in drought or calamity-affected areas."),
    ("What happens if work is not provided under MGNREGA?","If work is not provided within 15 days of demand, the applicant is entitled to an unemployment allowance."),
    ("What makes MGNREGA a rights-based scheme?","The legal guarantee of work on demand, enforceable through the courts, plus the unemployment allowance and mandatory social audits, distinguish it from discretionary welfare schemes."),
    ("Who conducts social audits under MGNREGA?","The Gram Sabha conducts social audits of MGNREGA works and expenditure in each village.")]},

 {"slug":"goods-and-services-tax-gst","tag":"Economy","read":"7 min read","cta":"/pyq/economy/",
  "title":"Goods and Services Tax (GST): How It Works in India",
  "h1":"Goods and Services Tax (GST)","kw":"GST, Goods and Services Tax, GST UPSC, GST Council, CGST SGST IGST, one nation one tax",
  "desc":"GST explained for UPSC — the destination-based dual GST model, CGST/SGST/IGST, the GST Council, and why it is called 'one nation, one tax'.",
  "intro":"The Goods and Services Tax (GST), launched on 1 July 2017 via the 101st Constitutional Amendment, is a comprehensive, destination-based indirect tax that subsumed most central and state indirect taxes.",
  "sec":[("The dual GST model","India follows a dual GST: on intra-state supplies both Central GST (CGST) and State GST (SGST) apply, while inter-state supplies attract Integrated GST (IGST). It is destination-based, so tax accrues to the consuming state."),
    ("The GST Council","The GST Council, a constitutional body chaired by the Union Finance Minister with state finance ministers as members, recommends rates, exemptions and rules — making GST a landmark in cooperative federalism."),
    ("Why it matters","By replacing a web of cascading taxes with input tax credit across the supply chain, GST created a common national market, earning the tagline 'one nation, one tax'.")],
  "why":"GST is core to the Economy syllabus — the dual model, the GST Council's composition and its federal significance appear regularly in Prelims and Mains.",
  "faq":[("What are CGST, SGST and IGST?","CGST and SGST apply on intra-state supplies; IGST applies on inter-state supplies. GST is destination-based."),
    ("Who chairs the GST Council?","The Union Finance Minister chairs the GST Council, with state finance ministers as members.")]},

 {"slug":"niti-aayog-explained","tag":"Polity","read":"6 min read","cta":"/pyq/polity/",
  "title":"NITI Aayog: Role, Structure and Functions Explained",
  "h1":"NITI Aayog","kw":"NITI Aayog, NITI Aayog UPSC, Planning Commission replacement, think tank India, cooperative federalism",
  "desc":"NITI Aayog explained for UPSC — how it replaced the Planning Commission in 2015, its structure, its role as a policy think tank and champion of cooperative federalism.",
  "intro":"The National Institution for Transforming India (NITI Aayog) was set up in 2015 to replace the Planning Commission, shifting from top-down central planning to a collaborative, advisory model.",
  "sec":[("Nature and structure","NITI Aayog is not a constitutional or statutory body — it was created by an executive resolution. The Prime Minister is its chairperson; it has a Vice-Chairperson, a Governing Council of Chief Ministers, and a CEO."),
    ("From allocation to advice","Unlike the Planning Commission, NITI Aayog does not allocate funds. It acts as the government's premier policy think tank, providing strategic and technical advice and fostering 'Team India'."),
    ("Cooperative and competitive federalism","It promotes cooperative federalism by involving states in policy design, and competitive federalism through indices that rank states on health, education, water and innovation.")],
  "why":"NITI Aayog vs Planning Commission is a classic comparison; its non-statutory nature, structure and federalism role are commonly asked in Prelims and Mains.",
  "faq":[("Is NITI Aayog a constitutional body?","No. NITI Aayog is neither constitutional nor statutory; it was created by a Union Cabinet executive resolution in 2015."),
    ("Does NITI Aayog allocate funds to states?","No. Unlike the Planning Commission, NITI Aayog is an advisory think tank and does not allocate funds.")]},

 {"slug":"fundamental-rights-explained","tag":"Polity","read":"7 min read","cta":"/pyq/polity/",
  "title":"Fundamental Rights in the Indian Constitution Explained",
  "h1":"Fundamental Rights (Part III)","kw":"Fundamental Rights, Fundamental Rights UPSC, Part III Constitution, Article 14 to 32, right to equality",
  "desc":"Fundamental Rights explained for UPSC — the six categories in Part III, their justiciable nature, reasonable restrictions and the right to constitutional remedies.",
  "intro":"Fundamental Rights, contained in Part III (Articles 12–35) of the Constitution, are the basic human rights guaranteed to citizens (and some to all persons), enforceable in the courts.",
  "sec":[("The six categories","The six Fundamental Rights are: Right to Equality (14–18), Right to Freedom (19–22), Right against Exploitation (23–24), Right to Freedom of Religion (25–28), Cultural and Educational Rights (29–30), and the Right to Constitutional Remedies (32)."),
    ("Justiciable but not absolute","These rights are justiciable — a person can approach the Supreme Court under Article 32 or a High Court under Article 226. However, they are subject to reasonable restrictions and can be suspended during a National Emergency (except Articles 20 and 21)."),
    ("Heart of the Constitution","Dr. B.R. Ambedkar called Article 32 the 'heart and soul' of the Constitution because it makes the rights meaningful by providing a remedy.")],
  "why":"Fundamental Rights are among the most tested Polity topics — the six categories, which apply to citizens vs all persons, and Article 32 are perennial Prelims material.",
  "faq":[("How many Fundamental Rights are there?","There are six categories of Fundamental Rights in Part III of the Constitution."),
    ("Which article is called the heart and soul of the Constitution?","Article 32, the Right to Constitutional Remedies, was described by Dr. B.R. Ambedkar as the heart and soul of the Constitution.")]},

 {"slug":"directive-principles-of-state-policy","tag":"Polity","read":"6 min read","cta":"/pyq/polity/",
  "title":"Directive Principles of State Policy (DPSP) Explained",
  "h1":"Directive Principles of State Policy (DPSP)","kw":"DPSP, Directive Principles UPSC, Part IV Constitution, non-justiciable, Ireland Constitution",
  "desc":"DPSP explained for UPSC — the non-justiciable guidelines in Part IV borrowed from Ireland, their classification, and their relationship with Fundamental Rights.",
  "intro":"The Directive Principles of State Policy (DPSP), in Part IV (Articles 36–51), are guidelines for the State to frame laws and policies aimed at establishing social and economic justice.",
  "sec":[("Non-justiciable ideals","Borrowed from the Irish Constitution, the DPSP are non-justiciable — they cannot be enforced by courts — but are 'fundamental in the governance of the country'."),
    ("Broad classification","They are often grouped as Socialistic (e.g., equal pay, living wage), Gandhian (e.g., village panchayats, cottage industries) and Liberal-Intellectual (e.g., uniform civil code, separation of judiciary from executive)."),
    ("Relationship with Fundamental Rights","While FRs are justiciable and DPSP are not, the courts have increasingly read them together; the 42nd Amendment gave certain DPSP primacy, and the basic structure requires harmony between them.")],
  "why":"The FR–DPSP relationship, the source (Ireland) and the non-justiciable nature are frequently tested, often through statement-based questions.",
  "faq":[("From which country's constitution are DPSP borrowed?","The Directive Principles of State Policy are borrowed from the Constitution of Ireland."),
    ("Are DPSP enforceable in court?","No. DPSP are non-justiciable, but they are fundamental in the governance of the country.")]},

 {"slug":"preamble-of-indian-constitution","tag":"Polity","read":"5 min read","cta":"/pyq/polity/",
  "title":"Preamble of the Indian Constitution: Meaning and Keywords",
  "h1":"Preamble of the Indian Constitution","kw":"Preamble UPSC, Preamble keywords, sovereign socialist secular, 42nd amendment preamble, basic structure",
  "desc":"The Preamble explained for UPSC — its keywords (Sovereign, Socialist, Secular, Democratic, Republic), the 42nd Amendment, and whether it is part of the Constitution.",
  "intro":"The Preamble is the introductory statement of the Constitution that sets out its guiding ideals, source of authority and objectives.",
  "sec":[("Key words","It declares India a Sovereign, Socialist, Secular, Democratic Republic and secures to citizens Justice, Liberty, Equality and Fraternity. The words 'Socialist', 'Secular' and 'Integrity' were added by the 42nd Amendment, 1976."),
    ("Source of authority","The phrase 'We, the People of India' establishes that the ultimate source of the Constitution's authority is the people of India."),
    ("Part of the Constitution","In the Kesavananda Bharati case (1973), the Supreme Court held that the Preamble is a part of the Constitution and can be amended under Article 368, without destroying the basic structure.")],
  "why":"The Preamble's keywords, the 42nd Amendment additions, and the Kesavananda ruling that it is amendable are among the most frequently examined Polity facts.",
  "faq":[("Which words were added to the Preamble by the 42nd Amendment?","'Socialist', 'Secular' and 'Integrity' were added by the 42nd Amendment, 1976."),
    ("Can the Preamble be amended?","Yes. The Supreme Court held in Kesavananda Bharati (1973) that the Preamble is part of the Constitution and can be amended under Article 368, subject to the basic structure.")]},

 {"slug":"anti-defection-law","tag":"Polity","read":"6 min read","cta":"/pyq/polity/",
  "title":"Anti-Defection Law (Tenth Schedule) Explained",
  "h1":"Anti-Defection Law","kw":"Anti-Defection Law, Tenth Schedule UPSC, 52nd amendment, disqualification, defection India",
  "desc":"The Anti-Defection Law explained for UPSC — the Tenth Schedule added by the 52nd Amendment, grounds for disqualification, and the role of the Speaker.",
  "intro":"The Anti-Defection Law was introduced by the 52nd Constitutional Amendment, 1985, adding the Tenth Schedule to curb political defections that destabilised governments.",
  "sec":[("Grounds for disqualification","A member can be disqualified if they voluntarily give up party membership or vote against the party whip. The law applies to members of Parliament and state legislatures."),
    ("The Speaker's role","The presiding officer (Speaker or Chairman) decides on disqualification. Courts can review this decision, and the Supreme Court has stressed that decisions should be made within a reasonable time."),
    ("Exceptions","The original provision allowed mergers if two-thirds of a legislative party agreed. The earlier 'split' exception was removed by the 91st Amendment, 2003.")],
  "why":"The Tenth Schedule — its amendment number, grounds for disqualification and the Speaker's deciding role — is regularly tested, especially in current-affairs-linked questions.",
  "faq":[("Which amendment introduced the Anti-Defection Law?","The 52nd Constitutional Amendment, 1985, which added the Tenth Schedule."),
    ("Who decides disqualification under the Anti-Defection Law?","The presiding officer of the House (the Speaker or Chairman), subject to judicial review.")]},

 {"slug":"basic-structure-doctrine","tag":"Polity","read":"6 min read","cta":"/pyq/polity/",
  "title":"Basic Structure Doctrine: Kesavananda Bharati Explained",
  "h1":"Basic Structure Doctrine","kw":"basic structure doctrine, Kesavananda Bharati UPSC, Article 368, judicial review, constitution amendment limits",
  "desc":"The Basic Structure Doctrine explained for UPSC — the Kesavananda Bharati (1973) judgment, limits on Parliament's amending power, and what counts as basic structure.",
  "intro":"The Basic Structure Doctrine holds that while Parliament can amend the Constitution under Article 368, it cannot alter its 'basic structure' or essential features.",
  "sec":[("The Kesavananda Bharati case","In Kesavananda Bharati v. State of Kerala (1973), a 13-judge bench of the Supreme Court laid down that Parliament's amending power is not unlimited and cannot destroy the basic structure."),
    ("What is 'basic structure'","There is no exhaustive list, but the judiciary has treated features such as the supremacy of the Constitution, rule of law, separation of powers, judicial review, federalism, secularism and free and fair elections as part of it."),
    ("Significance","The doctrine acts as a check on constitutional amendments and has been reaffirmed in later cases, protecting the Constitution's core identity.")],
  "why":"The 1973 case, Article 368 and examples of basic-structure features are staples of Polity questions and essential for Mains answers on judicial review.",
  "faq":[("Which case established the Basic Structure Doctrine?","Kesavananda Bharati v. State of Kerala (1973)."),
    ("Can Parliament amend the basic structure of the Constitution?","No. Parliament can amend the Constitution but cannot destroy or alter its basic structure.")]},

 {"slug":"finance-commission-of-india","tag":"Polity","read":"6 min read","cta":"/pyq/polity/",
  "title":"Finance Commission of India: Role and Functions",
  "h1":"Finance Commission of India","kw":"Finance Commission UPSC, Article 280, tax devolution, fiscal federalism, Finance Commission functions",
  "desc":"The Finance Commission explained for UPSC — a constitutional body under Article 280 that recommends the sharing of taxes between the Centre and states.",
  "intro":"The Finance Commission is a constitutional body constituted every five years to define financial relations between the Union and the states.",
  "sec":[("Constitutional basis","It is established under Article 280 by the President and is a constitutional body. It typically has a chairman and four members with fixed qualifications."),
    ("Core functions","It recommends the distribution of net tax proceeds between the Centre and states (vertical devolution) and among the states (horizontal devolution), and the principles governing grants-in-aid to states."),
    ("Advisory nature","Its recommendations are advisory, not binding on the government, though they are usually accepted. It is central to India's fiscal federalism.")],
  "why":"Article 280, its constitutional-body status and its advisory-but-not-binding nature are commonly tested, often in statement-based Polity questions.",
  "faq":[("Under which article is the Finance Commission constituted?","Article 280 of the Constitution."),
    ("Are the Finance Commission's recommendations binding?","No. They are advisory in nature, though they are generally accepted by the government.")]},

 {"slug":"election-commission-of-india","tag":"Polity","read":"6 min read","cta":"/pyq/polity/",
  "title":"Election Commission of India: Powers and Functions",
  "h1":"Election Commission of India (ECI)","kw":"Election Commission UPSC, Article 324, ECI functions, Chief Election Commissioner, model code of conduct",
  "desc":"The Election Commission of India explained for UPSC — the constitutional body under Article 324 that conducts elections to Parliament, state legislatures and the offices of President and Vice-President.",
  "intro":"The Election Commission of India (ECI) is an autonomous constitutional authority responsible for administering election processes in India.",
  "sec":[("Constitutional basis","The ECI is established under Article 324. It superintends, directs and controls elections to Parliament, state legislatures, and the offices of the President and Vice-President."),
    ("Composition","It is a multi-member body consisting of the Chief Election Commissioner and other Election Commissioners appointed by the President. Their removal is protected to ensure independence."),
    ("Key functions","It prepares electoral rolls, notifies election schedules, registers political parties, allots symbols and enforces the Model Code of Conduct.")],
  "why":"Article 324, the ECI's composition and its enforcement of the Model Code of Conduct are recurring Prelims and Mains themes, especially during election cycles.",
  "faq":[("Under which article is the Election Commission established?","Article 324 of the Constitution."),
    ("Does the ECI conduct local body elections?","No. Local body (panchayat and municipal) elections are conducted by State Election Commissions, not the ECI.")]},

 {"slug":"fiscal-deficit-explained","tag":"Economy","read":"6 min read","cta":"/pyq/economy/",
  "title":"Fiscal Deficit Explained: Meaning and Significance",
  "h1":"Fiscal Deficit","kw":"fiscal deficit UPSC, fiscal deficit meaning, revenue deficit vs fiscal deficit, government borrowing, FRBM",
  "desc":"Fiscal deficit explained for UPSC — what it measures, how it differs from revenue and primary deficit, and why it signals the government's borrowing needs.",
  "intro":"The fiscal deficit is the difference between the government's total expenditure and its total receipts excluding borrowings — it essentially indicates how much the government needs to borrow.",
  "sec":[("What it measures","Fiscal deficit = Total expenditure − Total receipts (excluding borrowings). A high fiscal deficit means greater borrowing, which can affect interest rates and inflation."),
    ("Related deficits","Revenue deficit is the shortfall on the revenue account; primary deficit is the fiscal deficit minus interest payments. These distinctions are frequently tested."),
    ("Fiscal discipline","The FRBM Act (Fiscal Responsibility and Budget Management Act) sets targets to keep deficits and public debt within prudent limits.")],
  "why":"The definitions of fiscal, revenue and primary deficit — and how they relate to borrowing — are core Economy concepts that recur in Prelims almost every year.",
  "faq":[("What does the fiscal deficit indicate?","It indicates the total borrowing requirement of the government — total expenditure minus total receipts excluding borrowings."),
    ("What is the primary deficit?","Primary deficit is the fiscal deficit minus interest payments on previous borrowings.")]},

 {"slug":"inflation-cpi-wpi-explained","tag":"Economy","read":"6 min read","cta":"/pyq/economy/",
  "title":"Inflation Explained: CPI vs WPI in India",
  "h1":"Inflation (CPI and WPI)","kw":"inflation UPSC, CPI WPI difference, consumer price index, wholesale price index, inflation types",
  "desc":"Inflation explained for UPSC — types of inflation, the difference between the Consumer Price Index (CPI) and Wholesale Price Index (WPI), and which one the RBI targets.",
  "intro":"Inflation is a sustained rise in the general price level of goods and services, reducing the purchasing power of money.",
  "sec":[("Measuring inflation","India measures inflation mainly through the Consumer Price Index (CPI), which tracks retail prices paid by consumers, and the Wholesale Price Index (WPI), which tracks prices at the wholesale level."),
    ("CPI vs WPI","CPI includes services and reflects consumer experience, while WPI covers only goods. The RBI uses CPI (Combined) as its main measure for inflation targeting."),
    ("Types","Demand-pull inflation arises from excess demand; cost-push inflation from rising input costs. Very high inflation is called hyperinflation, and rising prices with stagnant growth is stagflation.")],
  "why":"The CPI–WPI distinction, the RBI's use of CPI for inflation targeting, and inflation types are classic Economy Prelims topics.",
  "faq":[("Which index does the RBI target for inflation?","The RBI targets the Consumer Price Index (CPI) Combined for its inflation-targeting framework."),
    ("What is the difference between CPI and WPI?","CPI measures retail prices (including services) faced by consumers, while WPI measures wholesale prices of goods only.")]},

 {"slug":"monetary-policy-repo-rate","tag":"Economy","read":"6 min read","cta":"/pyq/economy/",
  "title":"Monetary Policy and Repo Rate: How the RBI Controls Money",
  "h1":"Monetary Policy and the Repo Rate","kw":"monetary policy UPSC, repo rate, reverse repo, CRR SLR, RBI MPC, inflation targeting",
  "desc":"Monetary policy explained for UPSC — the RBI's tools like repo rate, CRR and SLR, the Monetary Policy Committee, and the 4% inflation-targeting framework.",
  "intro":"Monetary policy is the process by which the Reserve Bank of India manages money supply and interest rates to achieve price stability while supporting growth.",
  "sec":[("Key instruments","Quantitative tools include the repo rate (the rate at which RBI lends to banks), reverse repo rate, Cash Reserve Ratio (CRR) and Statutory Liquidity Ratio (SLR). Raising the repo rate makes borrowing costlier, cooling demand and inflation."),
    ("The Monetary Policy Committee","A six-member Monetary Policy Committee (MPC), chaired by the RBI Governor, sets the policy rate. It operates under a flexible inflation-targeting framework."),
    ("The inflation target","The government, in consultation with the RBI, has set a CPI inflation target of 4% with a tolerance band of +/− 2%.")],
  "why":"Repo rate, CRR/SLR, the MPC's composition and the 4% (+/−2%) target are among the most frequently tested Economy facts.",
  "faq":[("What is the repo rate?","The repo rate is the rate at which the RBI lends short-term funds to commercial banks."),
    ("Who sets the policy interest rate in India?","The six-member Monetary Policy Committee (MPC), chaired by the RBI Governor.")]},

 {"slug":"reserve-bank-of-india-functions","tag":"Economy","read":"6 min read","cta":"/pyq/economy/",
  "title":"Reserve Bank of India (RBI): Functions Explained",
  "h1":"Reserve Bank of India (RBI)","kw":"RBI functions UPSC, central bank India, banker to government, monetary authority, currency issue",
  "desc":"The RBI explained for UPSC — its role as India's central bank: issuing currency, controlling monetary policy, regulating banks and acting as banker to the government.",
  "intro":"The Reserve Bank of India, established in 1935, is the country's central bank and monetary authority.",
  "sec":[("Monetary authority","The RBI formulates and implements monetary policy to maintain price stability while keeping in mind growth."),
    ("Issuer and regulator","It is the sole issuer of currency notes (except the one-rupee note and coins, issued by the government) and regulates and supervises the banking and financial system."),
    ("Banker roles","It acts as banker to the government and to banks, manages foreign exchange and public debt, and serves as lender of last resort.")],
  "why":"The RBI's functions — currency issue, banking regulation, and its role as banker to the government — are commonly tested, often in statement-based questions.",
  "faq":[("When was the RBI established?","The Reserve Bank of India was established in 1935."),
    ("Who issues one-rupee notes and coins in India?","The Government of India issues one-rupee notes and coins; the RBI issues all other currency notes.")]},

 {"slug":"g20-explained","tag":"IR","read":"6 min read","cta":"/pyq/",
  "title":"G20 Explained: Members, Purpose and India's Presidency",
  "h1":"G20 (Group of Twenty)","kw":"G20 UPSC, Group of Twenty, G20 members, G20 India presidency, international economic forum",
  "desc":"The G20 explained for UPSC — its origin, membership, focus on global economic cooperation, and the significance of India hosting the G20 presidency.",
  "intro":"The G20 (Group of Twenty) is the premier forum for international economic cooperation, bringing together major developed and emerging economies.",
  "sec":[("Origin and members","Formed in 1999 and elevated to leaders' level after the 2008 financial crisis, the G20 comprises 19 countries, the European Union, and the African Union (added as a member during India's presidency)."),
    ("What it does","It coordinates on global economic and financial stability, trade, development, climate finance and other cross-cutting issues. It has no permanent secretariat; a rotating presidency sets the agenda."),
    ("India's presidency","India held the G20 presidency in 2023 with the theme 'Vasudhaiva Kutumbakam — One Earth, One Family, One Future', spotlighting the Global South.")],
  "why":"G20 membership, its purpose and India's presidency are strong current-affairs topics that connect to the International Relations and economy portions of the syllabus.",
  "faq":[("What is the G20?","The G20 is the leading forum for international economic cooperation, comprising major developed and emerging economies plus the EU and African Union."),
    ("Does the G20 have a permanent secretariat?","No. The G20 has no permanent secretariat; a rotating annual presidency coordinates its work.")]},

 {"slug":"brics-explained","tag":"IR","read":"6 min read","cta":"/pyq/",
  "title":"BRICS Explained: Members, New Development Bank and Expansion",
  "h1":"BRICS","kw":"BRICS UPSC, BRICS members, New Development Bank, BRICS expansion, emerging economies grouping",
  "desc":"BRICS explained for UPSC — the grouping of major emerging economies, the New Development Bank, and its recent expansion of membership.",
  "intro":"BRICS is a grouping of major emerging economies that cooperate on economic, political and developmental issues, offering a platform beyond Western-led institutions.",
  "sec":[("Origin and members","The acronym originally stood for Brazil, Russia, India and China; South Africa joined in 2010. The group has since expanded to include additional members, broadening its economic and geographic footprint."),
    ("Institutions","BRICS established the New Development Bank (NDB), headquartered in Shanghai, to fund infrastructure and sustainable development, and a Contingent Reserve Arrangement (CRA) for liquidity support."),
    ("Significance","BRICS represents a large share of the world's population and economic output, and pushes for reform of global governance and a more multipolar order.")],
  "why":"BRICS members, the New Development Bank's location and its expansion are frequently examined current-affairs and IR topics.",
  "faq":[("Which bank did BRICS establish?","The New Development Bank (NDB), headquartered in Shanghai, China."),
    ("What did the acronym BRICS originally stand for?","Brazil, Russia, India, China and South Africa (South Africa joined in 2010).")]},

 {"slug":"quad-explained","tag":"IR","read":"5 min read","cta":"/pyq/",
  "title":"QUAD Explained: The Quadrilateral Security Dialogue",
  "h1":"QUAD (Quadrilateral Security Dialogue)","kw":"QUAD UPSC, Quadrilateral Security Dialogue, Indo-Pacific, India US Japan Australia, free and open Indo-Pacific",
  "desc":"The QUAD explained for UPSC — the strategic grouping of India, the US, Japan and Australia focused on a free, open and inclusive Indo-Pacific.",
  "intro":"The Quadrilateral Security Dialogue (QUAD) is a strategic grouping of four democracies — India, the United States, Japan and Australia — cooperating in the Indo-Pacific region.",
  "sec":[("Members and focus","The QUAD promotes a free, open and inclusive Indo-Pacific. It works on maritime security, connectivity, critical technologies, climate, health and supply-chain resilience."),
    ("Nature","It is an informal strategic forum rather than a formal military alliance, and holds leaders' summits and ministerial meetings. The Malabar naval exercise involves all four members."),
    ("Significance","For India, the QUAD supports a rules-based order and balances regional dynamics while advancing practical cooperation.")],
  "why":"QUAD members, its Indo-Pacific focus and its non-alliance nature are common IR current-affairs questions.",
  "faq":[("Which countries are members of the QUAD?","India, the United States, Japan and Australia."),
    ("Is the QUAD a military alliance?","No. The QUAD is an informal strategic forum, not a formal military alliance.")]},

 {"slug":"united-nations-structure","tag":"IR","read":"6 min read","cta":"/pyq/",
  "title":"United Nations: Structure and Principal Organs Explained",
  "h1":"United Nations (UN)","kw":"United Nations UPSC, UN organs, Security Council, General Assembly, UNSC permanent members",
  "desc":"The United Nations explained for UPSC — its six principal organs, the Security Council's permanent members and veto, and India's demand for UNSC reform.",
  "intro":"The United Nations, founded in 1945, is the world's foremost intergovernmental organisation for maintaining international peace and cooperation.",
  "sec":[("Six principal organs","The UN has six principal organs: the General Assembly, the Security Council, the Economic and Social Council, the Trusteeship Council (now suspended), the International Court of Justice, and the Secretariat."),
    ("The Security Council","The Security Council has 15 members — five permanent members (US, UK, France, Russia, China) with veto power, and ten non-permanent members elected for two-year terms."),
    ("Reform and India","India, a frequent non-permanent member, seeks permanent membership and reform of the Security Council to reflect current global realities.")],
  "why":"UN organs, the P5 with veto power and UNSC reform are recurring IR themes in both Prelims and Mains.",
  "faq":[("Which are the permanent members of the UN Security Council?","The United States, United Kingdom, France, Russia and China."),
    ("How many principal organs does the UN have?","Six — the General Assembly, Security Council, ECOSOC, Trusteeship Council, International Court of Justice and Secretariat.")]},

 {"slug":"climate-change-unfccc-cop","tag":"Environment","read":"6 min read","cta":"/pyq/environment/",
  "title":"Climate Change, UNFCCC and COP Explained",
  "h1":"Climate Change, UNFCCC and COP","kw":"climate change UPSC, UNFCCC, COP, Paris Agreement, Kyoto Protocol, net zero",
  "desc":"Climate change governance explained for UPSC — the UNFCCC, the annual COP meetings, the Paris Agreement's 1.5°C goal and India's net-zero commitment.",
  "intro":"Climate change refers to long-term shifts in temperature and weather patterns driven largely by human emissions of greenhouse gases. Global cooperation to address it is coordinated under the UNFCCC.",
  "sec":[("UNFCCC and COP","The UN Framework Convention on Climate Change (UNFCCC), adopted at the 1992 Rio Earth Summit, is the parent treaty. Its members meet annually at the Conference of the Parties (COP) to negotiate action."),
    ("Key agreements","The Kyoto Protocol (1997) set binding targets for developed countries. The Paris Agreement (2015) commits countries to limit warming to well below 2°C, ideally 1.5°C, through Nationally Determined Contributions (NDCs)."),
    ("India's stand","India champions the principle of 'common but differentiated responsibilities' and has pledged to reach net-zero emissions by 2070, alongside ambitious renewable-energy targets.")],
  "why":"UNFCCC, COP, the Paris Agreement's temperature goals and India's net-zero year are high-frequency Environment and current-affairs topics.",
  "faq":[("What is the temperature goal of the Paris Agreement?","To limit global warming to well below 2°C above pre-industrial levels, pursuing efforts to keep it to 1.5°C."),
    ("By when has India pledged to reach net-zero emissions?","India has pledged to achieve net-zero emissions by 2070.")]},

 {"slug":"biodiversity-iucn-red-list","tag":"Environment","read":"6 min read","cta":"/pyq/environment/",
  "title":"Biodiversity and the IUCN Red List Explained",
  "h1":"Biodiversity and the IUCN Red List","kw":"biodiversity UPSC, IUCN Red List, endangered species, conservation status, biodiversity hotspots",
  "desc":"Biodiversity and the IUCN Red List explained for UPSC — levels of biodiversity, Red List categories from Least Concern to Extinct, and biodiversity hotspots in India.",
  "intro":"Biodiversity is the variety of life on Earth — across genes, species and ecosystems. Its conservation status is tracked globally by the IUCN Red List.",
  "sec":[("Levels of biodiversity","Biodiversity is studied at three levels: genetic diversity, species diversity and ecosystem diversity."),
    ("IUCN Red List categories","The IUCN Red List classifies species by extinction risk: Least Concern, Near Threatened, Vulnerable, Endangered, Critically Endangered, Extinct in the Wild and Extinct. It is the most widely used measure of conservation status."),
    ("Hotspots in India","India hosts parts of four global biodiversity hotspots — the Himalayas, the Western Ghats, the Indo-Burma region and Sundaland (Nicobar Islands).")],
  "why":"IUCN Red List categories and India's biodiversity hotspots are among the most reliably tested Environment topics in Prelims.",
  "faq":[("What are the levels of biodiversity?","Genetic diversity, species diversity and ecosystem diversity."),
    ("How many biodiversity hotspots does India have parts of?","Four — the Himalayas, Western Ghats, Indo-Burma and Sundaland.")]},

 {"slug":"ramsar-convention-wetlands","tag":"Environment","read":"5 min read","cta":"/pyq/environment/",
  "title":"Ramsar Convention and Wetlands of India Explained",
  "h1":"Ramsar Convention and Wetlands","kw":"Ramsar Convention UPSC, Ramsar sites India, wetlands, Montreux Record, wetland conservation",
  "desc":"The Ramsar Convention explained for UPSC — the international treaty for wetland conservation, Ramsar sites in India, and the Montreux Record.",
  "intro":"The Ramsar Convention is an intergovernmental treaty for the conservation and wise use of wetlands, adopted in the Iranian city of Ramsar in 1971.",
  "sec":[("Wetlands of international importance","Countries designate 'Ramsar Sites' — wetlands of international importance — for conservation. India has a large and growing number of such sites."),
    ("Why wetlands matter","Wetlands provide water, support biodiversity, recharge groundwater, control floods and store carbon, making them among the most productive ecosystems."),
    ("The Montreux Record","The Montreux Record lists Ramsar sites where ecological character is threatened or changing; in India, Keoladeo and Loktak have featured on it.")],
  "why":"The Ramsar Convention, India's Ramsar sites and the Montreux Record are frequently tested Environment facts, especially when new sites are designated.",
  "faq":[("What is the Ramsar Convention about?","It is an international treaty for the conservation and wise use of wetlands, adopted in Ramsar, Iran, in 1971."),
    ("What is the Montreux Record?","A register of Ramsar wetland sites where ecological character is threatened or has changed.")]},

 {"slug":"project-tiger-india","tag":"Environment","read":"5 min read","cta":"/pyq/environment/",
  "title":"Project Tiger and Tiger Conservation in India",
  "h1":"Project Tiger","kw":"Project Tiger UPSC, tiger reserves India, NTCA, tiger conservation, tiger census",
  "desc":"Project Tiger explained for UPSC — India's flagship tiger conservation programme launched in 1973, the role of the NTCA, and tiger reserves.",
  "intro":"Project Tiger is India's flagship conservation programme launched in 1973 to protect the Bengal tiger and its habitat.",
  "sec":[("Launch and aim","Started in 1973 from Jim Corbett, Project Tiger aims to maintain a viable tiger population and preserve areas of biological importance as a natural heritage."),
    ("Governance","The National Tiger Conservation Authority (NTCA), a statutory body, oversees Project Tiger and tiger reserves. Reserves have a core (critical tiger habitat) and buffer zone."),
    ("Outcomes","Periodic tiger estimation exercises track population trends, and India hosts a large share of the world's wild tigers.")],
  "why":"Project Tiger's launch year, the NTCA and tiger-reserve structure are standard Environment Prelims content.",
  "faq":[("When was Project Tiger launched?","Project Tiger was launched in 1973."),
    ("Which body oversees Project Tiger?","The National Tiger Conservation Authority (NTCA), a statutory body.")]},

 {"slug":"isro-chandrayaan-3","tag":"Sci-Tech","read":"6 min read","cta":"/pyq/science-technology/",
  "title":"ISRO and Chandrayaan-3: India's Moon Landing Explained",
  "h1":"ISRO and Chandrayaan-3","kw":"Chandrayaan-3 UPSC, ISRO moon mission, lunar south pole, Vikram lander Pragyan rover",
  "desc":"Chandrayaan-3 explained for UPSC — India's successful soft landing near the Moon's south pole, the Vikram lander and Pragyan rover, and its significance.",
  "intro":"Chandrayaan-3 is India's third lunar exploration mission by ISRO, which achieved a historic soft landing near the Moon's south pole.",
  "sec":[("The mission","Chandrayaan-3 comprised a propulsion module, the Vikram lander and the Pragyan rover. It demonstrated safe soft-landing and roving on the lunar surface."),
    ("A historic first","With its landing, India became the first country to soft-land near the Moon's south polar region and the fourth country to achieve a soft landing on the Moon."),
    ("Why the south pole","The lunar south pole is scientifically valuable because permanently shadowed craters may hold water ice, important for future exploration.")],
  "why":"ISRO missions like Chandrayaan-3 are prime Science & Technology current-affairs topics — the landing site, spacecraft components and 'firsts' are commonly asked.",
  "faq":[("What did Chandrayaan-3 achieve?","A successful soft landing near the Moon's south pole, making India the first country to land in that region."),
    ("What were the lander and rover of Chandrayaan-3 called?","The lander was Vikram and the rover was Pragyan.")]},

 {"slug":"aditya-l1-solar-mission","tag":"Sci-Tech","read":"5 min read","cta":"/pyq/science-technology/",
  "title":"Aditya-L1: India's First Solar Mission Explained",
  "h1":"Aditya-L1 (Solar Mission)","kw":"Aditya-L1 UPSC, ISRO solar mission, Lagrange point L1, study of the Sun, solar corona",
  "desc":"Aditya-L1 explained for UPSC — India's first dedicated solar observatory placed at the Sun-Earth Lagrange point L1 to study the Sun's corona and solar wind.",
  "intro":"Aditya-L1 is India's first space-based mission dedicated to studying the Sun, launched by ISRO.",
  "sec":[("The destination — L1","The spacecraft is placed in a halo orbit around the first Sun-Earth Lagrange point (L1), about 1.5 million km from Earth, where it can observe the Sun continuously without eclipses."),
    ("What it studies","It carries instruments to study the solar corona, solar wind, solar flares and space weather, which affect satellites and communications on Earth."),
    ("Why it matters","Understanding solar activity helps protect space-based and ground-based technology from geomagnetic storms.")],
  "why":"The concept of Lagrange points, the L1 location and the mission's objectives are testable Science & Technology and current-affairs facts.",
  "faq":[("Where is Aditya-L1 placed?","In a halo orbit around the Sun-Earth Lagrange point L1, about 1.5 million km from Earth."),
    ("What does Aditya-L1 study?","The Sun — its corona, solar wind, flares and space weather.")]},

 {"slug":"one-nation-one-election","tag":"Trending","read":"6 min read","cta":"/pyq/polity/",
  "title":"One Nation One Election: Meaning, Pros and Cons",
  "h1":"One Nation, One Election","kw":"One Nation One Election UPSC, simultaneous elections, Kovind committee, electoral reform India",
  "desc":"One Nation, One Election explained for UPSC — the idea of holding Lok Sabha and state assembly elections together, its potential benefits, and the constitutional challenges.",
  "intro":"'One Nation, One Election' refers to the idea of synchronising elections to the Lok Sabha and all state legislative assemblies so they are held simultaneously.",
  "sec":[("The idea","Instead of frequent, staggered elections, the country would vote for the Lok Sabha and state assemblies together, as was largely the case in the early decades after independence."),
    ("Potential benefits","Supporters argue it could reduce election costs, limit the disruption of the Model Code of Conduct, and allow governments to focus on governance rather than continuous campaigning."),
    ("Challenges","Critics point to constitutional and federal hurdles — synchronising terms, handling a government's early fall, and concerns that national issues could overshadow state-level ones. A high-level committee examined the proposal and its implementation.")],
  "why":"This is a live governance and polity debate — its rationale, benefits and constitutional challenges make strong Mains material and Prelims current affairs.",
  "faq":[("What does One Nation, One Election mean?","Holding elections to the Lok Sabha and all state legislative assemblies simultaneously."),
    ("Were simultaneous elections ever held in India?","Yes. Elections to the Lok Sabha and state assemblies were largely held together in the first few general elections after independence.")]},

 {"slug":"uniform-civil-code-ucc","tag":"Trending","read":"6 min read","cta":"/pyq/polity/",
  "title":"Uniform Civil Code (UCC): Meaning and Debate Explained",
  "h1":"Uniform Civil Code (UCC)","kw":"Uniform Civil Code UPSC, UCC meaning, Article 44, DPSP, personal laws India",
  "desc":"The Uniform Civil Code explained for UPSC — the DPSP under Article 44, what a common civil code would mean, and the arguments on both sides.",
  "intro":"A Uniform Civil Code (UCC) refers to a common set of personal laws governing matters such as marriage, divorce, inheritance and adoption for all citizens, regardless of religion.",
  "sec":[("Constitutional basis","Article 44, a Directive Principle of State Policy, directs the State to endeavour to secure a Uniform Civil Code for citizens. As a DPSP, it is non-justiciable."),
    ("Arguments in favour","Supporters argue a UCC would promote equality, gender justice and national integration by replacing varied personal laws with a common code."),
    ("Arguments against","Critics raise concerns about religious freedom and the diversity of personal laws, and stress the need for wide consultation and consensus.")],
  "why":"Article 44, the DPSP link and the balance between uniformity and religious freedom are important for Polity and current-affairs discussions.",
  "faq":[("Under which article is the Uniform Civil Code mentioned?","Article 44 of the Constitution, a Directive Principle of State Policy."),
    ("Is Article 44 (UCC) enforceable in court?","No. As a Directive Principle, it is non-justiciable and serves as a guideline for the State.")]},

 {"slug":"digital-personal-data-protection-act","tag":"Trending","read":"6 min read","cta":"/pyq/",
  "title":"Digital Personal Data Protection Act: Key Features",
  "h1":"Digital Personal Data Protection Act","kw":"Digital Personal Data Protection Act UPSC, data protection India, data principal, consent, Data Protection Board",
  "desc":"The Digital Personal Data Protection Act explained for UPSC — how it regulates the processing of digital personal data, key terms, and the Data Protection Board.",
  "intro":"The Digital Personal Data Protection (DPDP) Act, 2023, is India's dedicated law governing the processing of digital personal data, balancing individuals' privacy with lawful data use.",
  "sec":[("Core principles","The Act is built around consent, purpose limitation and data minimisation. Entities processing data ('data fiduciaries') must handle personal data lawfully and for specified purposes."),
    ("Key terms","A 'data principal' is the individual to whom the data relates; a 'data fiduciary' determines the purpose and means of processing. The Act gives individuals rights over their data."),
    ("Enforcement","A Data Protection Board of India is to be set up to adjudicate breaches and impose penalties, and the law provides for exemptions in specified circumstances.")],
  "why":"Following the Supreme Court's recognition of privacy as a fundamental right, the DPDP Act is a key governance topic linking rights, technology and law.",
  "faq":[("What does the Digital Personal Data Protection Act regulate?","The processing of digital personal data in India, based on consent and purpose limitation."),
    ("Who is a 'data fiduciary' under the Act?","An entity that determines the purpose and means of processing personal data.")]},

 {"slug":"womens-reservation-act","tag":"Trending","read":"6 min read","cta":"/pyq/polity/",
  "title":"Women's Reservation Act (Nari Shakti Vandan Adhiniyam)",
  "h1":"Women's Reservation Act","kw":"Women's Reservation Act UPSC, Nari Shakti Vandan Adhiniyam, 33% reservation, Lok Sabha assemblies women",
  "desc":"The Women's Reservation Act explained for UPSC — the constitutional amendment reserving one-third of seats for women in the Lok Sabha and state assemblies, and its implementation.",
  "intro":"The Women's Reservation Act (Nari Shakti Vandan Adhiniyam) is a constitutional amendment that reserves seats for women in the Lok Sabha and state legislative assemblies.",
  "sec":[("The reservation","The law provides for reserving one-third (about 33%) of seats in the Lok Sabha and state legislative assemblies for women, including within seats reserved for SCs and STs."),
    ("Implementation","The reservation is to take effect after a delimitation exercise following the next Census, and is intended to last for a specified period, subject to review."),
    ("Significance","It aims to strengthen women's political representation, which has historically remained low in India's legislatures.")],
  "why":"As a recent constitutional amendment on representation, this is a strong current-affairs and Polity topic — the one-third reservation and its conditional implementation are key facts.",
  "faq":[("What share of seats does the Women's Reservation Act reserve?","One-third (about 33%) of seats in the Lok Sabha and state legislative assemblies."),
    ("Does the women's reservation apply within SC/ST reserved seats?","Yes. The one-third reservation for women applies within seats reserved for Scheduled Castes and Scheduled Tribes as well.")]},

 {"slug":"national-green-hydrogen-mission","tag":"Trending","read":"5 min read","cta":"/pyq/environment/",
  "title":"National Green Hydrogen Mission Explained",
  "h1":"National Green Hydrogen Mission","kw":"Green Hydrogen Mission UPSC, green hydrogen India, electrolysis renewable, decarbonisation, energy transition",
  "desc":"The National Green Hydrogen Mission explained for UPSC — what green hydrogen is, the mission's goals, and its role in India's energy transition and net-zero target.",
  "intro":"The National Green Hydrogen Mission aims to make India a global hub for the production, use and export of green hydrogen and its derivatives.",
  "sec":[("What is green hydrogen","Green hydrogen is produced by splitting water through electrolysis using renewable electricity, so its production emits no carbon — unlike 'grey' hydrogen made from fossil fuels."),
    ("Mission goals","The mission targets significant annual green-hydrogen production capacity and associated renewable-energy addition, aiming to decarbonise industry, transport and fertiliser sectors."),
    ("Why it matters","Green hydrogen can cut emissions in hard-to-abate sectors, reduce fossil-fuel imports and support India's net-zero-by-2070 goal.")],
  "why":"Green hydrogen links Environment, Economy and Science & Technology — the electrolysis concept and the mission's aims are testable and topical.",
  "faq":[("What is green hydrogen?","Hydrogen produced by electrolysis of water using renewable electricity, with no carbon emissions."),
    ("What is the aim of the National Green Hydrogen Mission?","To make India a global hub for producing, using and exporting green hydrogen and to support decarbonisation.")]},

 {"slug":"sustainable-development-goals-sdgs","tag":"Environment","read":"5 min read","cta":"/pyq/",
  "title":"Sustainable Development Goals (SDGs) Explained",
  "h1":"Sustainable Development Goals (SDGs)","kw":"SDGs UPSC, Sustainable Development Goals, 2030 Agenda, 17 goals, sustainable development",
  "desc":"The Sustainable Development Goals explained for UPSC — the 17 goals of the 2030 Agenda, their scope from poverty to climate, and India's SDG efforts.",
  "intro":"The Sustainable Development Goals (SDGs) are a set of global goals adopted by UN member states in 2015 as part of the 2030 Agenda for Sustainable Development.",
  "sec":[("The 17 goals","There are 17 goals with 169 targets, covering ending poverty and hunger, good health, quality education, gender equality, clean water, affordable clean energy, decent work, climate action, life below water and on land, and peace and partnerships."),
    ("Universal and integrated","Unlike the earlier Millennium Development Goals, the SDGs apply to all countries and integrate the economic, social and environmental dimensions of development."),
    ("India's role","India tracks progress through the NITI Aayog SDG India Index and has aligned many national schemes with the goals.")],
  "why":"The number of SDGs, the 2030 Agenda and the SDG India Index are commonly tested, and SDGs feature widely in Mains answers on development.",
  "faq":[("How many Sustainable Development Goals are there?","There are 17 SDGs with 169 targets, part of the 2030 Agenda."),
    ("Who tracks SDG progress across Indian states?","NITI Aayog, through the SDG India Index.")]},
]

TMPL = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-G2DK8674FB"></script>
  <script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','G-G2DK8674FB');</script>
  <title>{title} | YESPYQ</title>
  <meta name="description" content="{desc}" />
  <meta name="keywords" content="{kw}" />
  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1" />
  <meta name="googlebot" content="index, follow" />
  <meta name="author" content="YESPYQ" />
  <meta name="theme-color" content="#2563eb" />
  <link rel="canonical" href="{base}/blog/{slug}/" />
  <meta property="og:type" content="article" />
  <meta property="og:site_name" content="YESPYQ" />
  <meta property="og:url" content="{base}/blog/{slug}/" />
  <meta property="og:title" content="{title}" />
  <meta property="og:description" content="{desc}" />
  <meta property="og:image" content="{base}/assets/og-image.png" />
  <meta property="og:locale" content="en_IN" />
  <meta property="article:published_time" content="{today}" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{h1}" />
  <meta name="twitter:description" content="{desc}" />
  <meta name="twitter:image" content="{base}/assets/og-image.png" />
  <link rel="icon" type="image/svg+xml" href="/assets/favicon.svg" />
  <link rel="apple-touch-icon" href="/assets/apple-touch-icon.png" />
  <link rel="manifest" href="/manifest.webmanifest" />
  <link rel="stylesheet" href="/styles.css?v=25" />
  <link rel="stylesheet" href="/blog.css?v=5" />
  <style>
    .quick-answer{{border:1px solid var(--border,#e2e8f0);background:var(--surface,#f8fafc);border-left:4px solid #2563eb;padding:14px 16px;border-radius:10px;margin:18px 0}}
    .quick-answer .qa-label{{display:inline-block;font-size:.72rem;font-weight:700;letter-spacing:.05em;text-transform:uppercase;color:#2563eb;margin-bottom:4px}}
    .quick-answer p{{margin:0;font-size:1.02rem;line-height:1.6}}
    .toc{{border:1px solid var(--border,#e2e8f0);border-radius:10px;padding:12px 16px 12px 18px;margin:18px 0;background:var(--surface,#f8fafc)}}
    .toc-h{{font-size:.75rem;font-weight:700;text-transform:uppercase;letter-spacing:.05em;margin:0 0 6px;color:var(--muted,#64748b)}}
    .toc ol{{margin:0;padding-left:18px}}
    .toc li{{margin:3px 0}}
    .toc a{{color:#2563eb;text-decoration:none}}
    .toc a:hover{{text-decoration:underline}}
    .keyfacts{{margin:20px 0}}
    .keyfacts table{{width:100%;border-collapse:collapse;font-size:.95rem}}
    .keyfacts th,.keyfacts td{{text-align:left;padding:8px 10px;border-bottom:1px solid var(--border,#e2e8f0);vertical-align:top}}
    .keyfacts th{{width:38%;font-weight:600;color:var(--muted,#475569)}}
    .takeaways{{border:1px solid var(--border,#e2e8f0);background:var(--surface,#f8fafc);border-radius:10px;padding:14px 18px;margin:22px 0}}
    .takeaways h2{{margin-top:0}}
    .takeaways ul{{margin:8px 0 0;padding-left:20px}}
    .takeaways li{{margin:6px 0}}
    [data-theme="dark"] .quick-answer,[data-theme="dark"] .toc,[data-theme="dark"] .takeaways{{background:rgba(255,255,255,.04);border-color:rgba(255,255,255,.12)}}
    [data-theme="dark"] .keyfacts th,[data-theme="dark"] .keyfacts td{{border-color:rgba(255,255,255,.12)}}
  </style>
  <script type="application/ld+json">
  {{"@context":"https://schema.org","@type":"Article","headline":"{h1}","description":"{desc}","image":"{base}/assets/og-image.png","datePublished":"{today}","dateModified":"{today}","inLanguage":"en-IN","wordCount":{wc},"keywords":"{kw}","articleSection":"{tag}","about":{{"@type":"Thing","name":"{h1}"}},"author":{{"@type":"Organization","name":"YESPYQ","url":"{base}/"}},"publisher":{{"@type":"EducationalOrganization","name":"YESPYQ","logo":{{"@type":"ImageObject","url":"{base}/assets/favicon.svg"}}}},"mainEntityOfPage":{{"@type":"WebPage","@id":"{base}/blog/{slug}/"}}}}
  </script>
  <script type="application/ld+json">
  {{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{{"@type":"ListItem","position":1,"name":"Home","item":"{base}/"}},{{"@type":"ListItem","position":2,"name":"Blog","item":"{base}/blog/"}},{{"@type":"ListItem","position":3,"name":"{tag}","item":"{base}/blog/{slug}/"}}]}}
  </script>
  <script type="application/ld+json">
  {{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{faq_ld}]}}
  </script>
  <script src="/theme.js?v=1"></script>
</head>
<body>
  <header class="site-header">
    <div class="container header-inner">
      <a class="brand" href="/"><img src="/assets/favicon.svg" alt="" class="brand-mark" /><span class="brand-name">YES<span>PYQ</span></span></a>
      <nav class="main-nav"><a href="/">Home</a><a href="/">Practice</a><a href="/subjects/">Subjects</a></nav>
      <a href="/" class="btn btn-primary btn-sm">Start Practice</a>
    </div>
  </header>
  <main>
    <article class="article">
      <nav class="breadcrumb"><a href="/">Home</a> › <a href="/blog/">Blog</a> › {tag}</nav>
      <h1>{h1}</h1>
      <div class="meta"><span>By YESPYQ</span> · <span>Updated July 2026</span> · <span>{read}</span></div>
      <div class="quick-answer"><span class="qa-label">Quick answer</span><p>{quick_answer}</p></div>
      <div class="prose">
        {toc}
        <p>{intro}</p>
        {keyfacts}
{sections}
        <h2 id="why-upsc">Why it matters for UPSC</h2>
        <p>{why}</p>
        {takeaways}
        <div class="cta-box">
          <h3>Practise related UPSC PYQs</h3>
          <p>See how this topic has actually been asked. Solve real UPSC Prelims previous year questions with answers and explanations — free.</p>
          <a href="{cta}" class="btn btn-primary">Practise PYQs →</a>
        </div>
        <div class="faq">
          <h2 id="faq">Frequently asked questions</h2>
{faq_html}
        </div>
      </div>
      <section class="related">
        <h2>Keep reading</h2>
        <div class="related-list">{related}</div>
      </section>
    </article>
  </main>
  <footer class="site-footer">
    <div class="container footer-inner">
      <div class="footer-brand"><img src="/assets/favicon.svg" alt="" class="brand-mark" /><span class="brand-name">YES<span>PYQ</span></span><p>Previous Year Questions, simplified.</p></div>
      <div class="footer-col"><h4>Practice</h4><a href="/">Home</a><a href="/subjects/">Subjects</a><a href="/pyq/">All PYQs</a><a href="/guides/">Guides</a><a href="/blog/">Blog</a></div>
      <div class="footer-col"><h4>Company</h4><a href="/about/">About</a><a href="/contact/">Contact</a></div>
      <div class="footer-col"><h4>Legal</h4><a href="/privacy-policy/">Privacy Policy</a><a href="/terms/">Terms &amp; Conditions</a><a href="/disclaimer/">Disclaimer</a></div>
    </div>
    <div class="footer-bottom">© <span id="year"></span> YESPYQ.com · Built for UPSC CSE aspirants · Not affiliated with UPSC</div>
  </footer>
  <script>document.getElementById("year").textContent = new Date().getFullYear();</script>
</body>
</html>
"""

def esc(s): return s.replace('"','\\"')

def _h1(t): return t.get("h1") or (t["title"].split(":")[0].strip() if ":" in t["title"] else t["title"])

def slugify(s):
    s=re.sub(r'[^a-z0-9]+','-',s.lower()).strip('-')
    return s[:44] or 'section'

def render(t, Tlist, idx):
    h1=_h1(t)
    sec_html=""; toc_items=[]
    for h,p in t["sec"]:
        sid=slugify(h)
        sec_html+=f'        <h2 id="{sid}">{h}</h2>\n        <p>{p}</p>\n'
        toc_items.append((sid,h))
    toc_li="".join(f'<li><a href="#{sid}">{h}</a></li>' for sid,h in toc_items)
    if t.get("take"): toc_li+='<li><a href="#key-takeaways">Key takeaways</a></li>'
    toc_li+='<li><a href="#faq">FAQs</a></li>'
    toc=f'<nav class="toc" aria-label="On this page"><p class="toc-h">On this page</p><ol>{toc_li}</ol></nav>'
    quick_answer=t.get("tldr") or t["intro"]
    facts=t.get("facts")
    if facts:
        rows="".join(f'<tr><th>{l}</th><td>{v}</td></tr>' for l,v in facts)
        keyfacts=f'<div class="keyfacts"><h2 id="at-a-glance">Key facts at a glance</h2><table><tbody>{rows}</tbody></table></div>'
    else: keyfacts=""
    take=t.get("take")
    if take:
        lis="".join(f'<li>{x}</li>' for x in take)
        takeaways=f'<div class="takeaways"><h2 id="key-takeaways">Key takeaways</h2><ul>{lis}</ul></div>'
    else: takeaways=""
    faq_html="".join('          <details><summary>{}</summary><p>{}</p></details>\n'.format(q,a) for q,a in t["faq"])
    faq_ld=",".join('{{"@type":"Question","name":"{}","acceptedAnswer":{{"@type":"Answer","text":"{}"}}}}'.format(esc(q),esc(a)) for q,a in t["faq"])
    rel=""
    for j in range(1,4):
        r=Tlist[(idx+j)%len(Tlist)]
        rel+=f'<a href="/blog/{r["slug"]}/"><span class="tag">{r["tag"]}</span><b>{_h1(r)}</b></a>'
    text=t["intro"]+" "+" ".join(p for _,p in t["sec"])+" "+t["why"]
    wc=len(re.sub(r'<[^>]+>',' ',text).split())
    return TMPL.format(base=BASE, slug=t["slug"], title=t["title"], h1=h1, desc=t["desc"], kw=t["kw"],
        tag=t["tag"], read=t.get("read","6 min read"), today=TODAY, intro=t["intro"], sections=sec_html,
        why=t["why"], cta=t.get("cta","/pyq/"), faq_html=faq_html, faq_ld=faq_ld, related=rel,
        toc=toc, quick_answer=quick_answer, keyfacts=keyfacts, takeaways=takeaways, wc=wc)

def build(t, idx): return render(t, T, idx)

def main():
    for i,t in enumerate(T):
        d=os.path.join(ROOT,"blog",t["slug"])
        os.makedirs(d,exist_ok=True)
        open(os.path.join(d,"index.html"),"w").write(build(t,i))
    print("wrote",len(T),"topic posts")
    # emit slugs/titles/tags for index + sitemap wiring
    for t in T: print("CARD", t["slug"], "||", t["tag"], "||", t["h1"], "||", t["desc"][:90])

if __name__=="__main__":
    main()
