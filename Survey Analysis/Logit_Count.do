use "/Users/Taylor/Downloads/Dissertation_14.6.dta"
tab age
gen age_bins = "18-30"
replace age_bins = "30-49" if age >=30
replace age_bins = "50+" if age >= 50
tab age_bins
encode age_bins, gen(age_bins_b)
logistic labels_2 q1 q3 q4 q5 q6 q7 q8 q9 q10 q11 q12 q13 q14 q15 i.gen i.HR i.EL_groups i.PS_groups avg_hh_earnings avg_per_earnings i.age_bins_b
logistic labels_2 q1 q3 q4 q5 q6 q7 q8 q9 q10 q11 q12 q13 q14 q15 i.gen i.HR i.EL_groups i.PS_groups avg_hh_earnings avg_per_earnings i.age_bins_b i.ES i.ESS
margins gen
margins gen, atmeans
margins age_bins_b,atmeans
tab avg_per_earnings
margins, at(avg_per_earnings=(15000(10000)200000)) atmeans vsquish
margins, at(avg_per_earnings=(15000(10000)200000)) vsquish

