import json,re
h=open('Kaushal_Radar_Dashboard.html').read()
D={r['name']:r for r in json.loads(re.search(r'const D=(\[.*?\]);const P=',h,re.S).group(1))}
B={
'Raichur':"Raichur ranks 1st of 31 with 4.03 registrants per 1,000 residents, almost twice the state average of 2.17. It has 8,813 registrants against a per capita income of Rs 1.79 lakh, and it stays in the top 8 in every stability draw.",
'Kalaburagi':"Kalaburagi ranks 2nd at 3.55 registrants per 1,000, about 1.6 times the state average. Its income is the lowest in the state at Rs 1.44 lakh and it has 10,503 registrants.",
'Bagalkot':"Bagalkot sits 3rd at 3.41 per 1,000 and 3rd again on Census 2011 population (3.78). With an income of Rs 2.80 lakh it is the strongest district outside Kalyana-Karnataka.",
'Davanagere':"Davanagere is 4th at 3.17 per 1,000 on the implied population but 7th on Census population, so treat it as a band. It has 5,408 registrants and about 476 reported MSME jobs per 1,000 residents.",
'Yadgir':"Yadgir ranks 5th with 3.01 registrants per 1,000 (4th on Census population). It has 4,215 registrants and an income of Rs 1.64 lakh, and appears in the top 8 in 75% of draws.",
'Bidar':"Bidar ranks 6th at 3.01 per 1,000 with 5,644 registrants. Its workers per micro unit (21.5) are flagged for review, so confirm the MSME data before drawing conclusions.",
'Vijayapura':"Vijayapura is 7th at 2.95 per 1,000 and 5th on Census population, with 7,474 registrants. Reported MSME employment is only 235 jobs per 1,000 residents.",
'Shivamogga':"Shivamogga ranks 8th at 2.78 per 1,000, the edge of the diagnostic queue, and appears in the top 8 in 46% of draws. Its income of Rs 3.90 lakh is above the state average.",
'Koppal':"Koppal is 9th at 2.77 per 1,000 and 8th on Census population, so it is just outside the queue on one measure and inside on the other. It has 4,409 registrants.",
'Belagavi':"Belagavi has the largest number of registrants, 13,779, but ranks 10th at 2.63 per 1,000 because its population is large. It is in the top 8 in 27% of draws.",
'Uttara Kannada':"Uttara Kannada ranks 11th at 2.61 per 1,000 with 3,783 registrants and an income of Rs 2.95 lakh. MSME job density is low at 163 per 1,000.",
'Gadag':"Gadag is 12th at 2.58 per 1,000 with 2,871 registrants and about 398 reported MSME jobs per 1,000 residents.",
'Chitradurga':"Chitradurga ranks 13th at 2.50 per 1,000. Its workers per micro unit (21.5) and 579 MSME jobs per 1,000 are flagged, so verify the MSME records first.",
'Chikkamagaluru':"Chikkamagaluru ranks 14th at 2.46 per 1,000 with 2,671 registrants. Its per capita income of Rs 4.95 lakh is among the highest in the state.",
'Ballari':"Ballari ranks 15th at 2.42 per 1,000, with 3,834 registrants and 610 reported MSME jobs per 1,000 residents. Vijayanagara was carved out of the old district, so compare the two with care.",
'Haveri':"Haveri is 16th at 2.38 per 1,000 with 4,041 registrants and an income of Rs 2.03 lakh. It is close to the state average of 2.17.",
'Hassan':"Hassan ranks 17th at 2.36 per 1,000 with 4,100 registrants and a high MSME density of 522 jobs per 1,000 residents.",
'Vijayanagara':"Vijayanagara is 18th at 2.35 per 1,000 on implied population but 10th on Census population, a gap of 8 places, so its rank is uncertain. It has 3,877 registrants.",
'Udupi':"Udupi ranks 19th at 2.09 per 1,000, just below the state average of 2.17, with 2,389 registrants and a per capita income of Rs 6.01 lakh.",
'Dharwad':"Dharwad is 20th at 2.02 per 1,000 with 4,151 registrants and 280 reported MSME jobs per 1,000 residents.",
'Kodagu':"Kodagu is 21st at 1.97 per 1,000 with 1,052 registrants, the smallest count in the state, so small changes move its rate noticeably.",
'Mandya':"Mandya ranks 22nd at 1.94 per 1,000 with 3,377 registrants and an income of Rs 3.41 lakh.",
'Chikkaballapura':"Chikkaballapura is 23rd at 1.88 per 1,000 with 2,475 registrants and 321 reported MSME jobs per 1,000 residents.",
'Mysuru':"Mysuru ranks 24th at 1.87 per 1,000 (20th on Census population) with 6,131 registrants, and about 351 MSME jobs per 1,000 residents.",
'Chamarajanagar':"Chamarajanagar is 25th at 1.87 per 1,000 with 1,905 registrants and an income of Rs 3.04 lakh. It is well below the state average of 2.17.",
'Tumakuru':"Tumakuru ranks 26th at 1.86 per 1,000 with 4,924 registrants and 352 MSME jobs per 1,000 residents.",
'Ramanagara (Bengaluru South)':"Ramanagara, now Bengaluru South, ranks 27th at 1.69 per 1,000 with 2,063 registrants. Confirm the boundary and name change before comparing years.",
'Bengaluru Rural':"Bengaluru Rural ranks 28th at 1.67 per 1,000, but its 1,048 reported MSME jobs per 1,000 residents is a flagged outlier, probably commuting and registration effects.",
'Dakshina Kannada':"Dakshina Kannada ranks 29th at 1.62 per 1,000 with 3,643 registrants and a per capita income of Rs 6.26 lakh, the second highest in the state.",
'Kolar':"Kolar is 30th at 1.61 per 1,000 with 2,624 registrants and an income of Rs 2.49 lakh.",
'Bengaluru Urban':"Bengaluru Urban ranks last, 31st, at 0.75 per 1,000 (1.01 on Census population) despite 9,733 registrants. Domicile rules and migration may explain the low rate, so it is not low need.",
}
assert set(B)==set(D),set(D)-set(B)
ST=2.17
def allowed(r):
    return [r['dgpi_per_1000'],r['rk_dgpi_per_1000'],r['Grand Total'],r['income_lakh'],r['msme_jobs_per_1000'],r['dgpi_census'],r['rk_dgpi_census'],r['p8_imp'],ST,r['dgpi_per_1000']/ST,31,8,2022,1000,3000,100]
def nums(t): return [(m, len(m.split('.')[1]) if '.' in m else 0) for m in re.findall(r'\d[\d,]*\.?\d*',t.replace('Rs ','Rs '))]
def check(t,r):
    bad=[]
    for m,dec in nums(t):
        x=float(m.replace(',','').rstrip('.'))
        if not any(round(a,dec)==x or abs(a-x)<1e-9 for a in allowed(r)): bad.append(m)
    return bad
R=[]; 
for n,t in B.items():
    r=D[n]; bad=check(t,r); R.append((n,bad))
ok=[n for n,b in R if not b]; print('passed first time: %d of %d'%(len(ok),len(R)))
for n,b in R:
    if b: print('REJECT',n,b,'|',B[n][:110])
