import pandas as pd, numpy as np, json, re
from scipy.stats import spearmanr
rng=np.random.default_rng(42)
d=pd.read_csv('indicators-1.csv')
CEN={'bagalkot':1889752,'bengaluru_urban':9621551,'bengaluru_rural':990923,'ramanagara':1082636,'belagavi':4779661,'ballari':1400970,'bidar':1703300,'vijayapura':2177331,'chamarajanagar':1020791,'chikkaballapur':1255104,'chikkamagaluru':1137961,'chitradurga':1659456,'dakshina_kannada':2089649,'davanagere':1643494,'dharwad':1847023,'gadag':1064570,'kalaburagi':2566326,'hassan':1776421,'haveri':1597668,'kodagu':554519,'kolar':1536401,'koppal':1389920,'mandya':1805769,'mysuru':3001127,'raichur':1928812,'shivamogga':1752753,'tumakuru':2678980,'udupi':1177361,'uttara_kannada':1437169,'vijayanagar':1353628,'yadgir':1174271}
tot=sum(CEN.values()); print('census sum',tot,'state PCA 61095297 ->',tot==61095297)
d['pop2011']=d.key.map(CEN); assert d.pop2011.notna().all()
d['dgpi_census']=d['Grand Total']/d.pop2011*1000
d['rank_implied']=d.dgpi_per_1000.rank(ascending=False).astype(int); d['rank_census']=d.dgpi_census.rank(ascending=False).astype(int)
rho,_=spearmanr(d.dgpi_per_1000,d.dgpi_census)
top=lambda c,k:set(d.nlargest(k,c).key)
print('rank corr implied vs census',round(rho,3)); print('top8 overlap',len(top('dgpi_per_1000',8)&top('dgpi_census',8)),'/8; top5',len(top('dgpi_per_1000',5)&top('dgpi_census',5)),'/5')
print(d.sort_values('dgpi_census',ascending=False)[['District','dgpi_per_1000','rank_implied','dgpi_census','rank_census']].head(10).round(2).to_string(index=False))
def boot(x,y):
    n=len(x); b=[spearmanr(x[i],y[i])[0] for i in (rng.integers(0,n,n) for _ in range(5000))]; return np.nanpercentile(b,[2.5,97.5]).round(2)
x=d.income_lakh.values
for c in ('dgpi_per_1000','dgpi_census'):
    r=spearmanr(x,d[c])[0]; e=d[d.key!='bengaluru_urban']
    print(c,'rho income',round(r,3),'CI',boot(x,d[c].values),'exBU',round(spearmanr(e.income_lakh,e[c])[0],3))
kk=['kalaburagi','yadgir','raichur','koppal','bidar','ballari','vijayanagar']
for nm,pc in (('implied','implied_pop'),('census','pop2011')):
    print(nm,'KK share pop %.1f%%'%(100*d[d.key.isin(kk)][pc].sum()/d[pc].sum()),'BU %.1f%%'%(100*d[d.key=='bengaluru_urban'][pc].sum()/d[pc].sum()))
print('KK regs share %.1f%%'%(100*d[d.key.isin(kk)]['Grand Total'].sum()/d['Grand Total'].sum()))
for c in ('dgpi_per_1000','dgpi_census'):
    s=d[d.key.isin(kk)]['Grand Total'].sum()/d[d.key.isin(kk)][('implied_pop' if c=='dgpi_per_1000' else 'pop2011')].sum()*1000
    b=d[d.key=='bengaluru_urban'][c].iloc[0]; print(c,'KK pooled %.2f vs BU %.2f'%(s,b))
# stability under census: share of draws top5 using +-15% on census pop
cnt=pd.Series(0,index=d.key)
for _ in range(5000):
    v=d['Grand Total']/(d.pop2011*rng.uniform(.85,1.15,len(d)))
    for k in d.assign(v=v).nlargest(5,'v').key: cnt[k]+=1
print((cnt/50).sort_values(ascending=False).head(7).round(0).to_dict())
d.to_csv('indicators_v2.csv',index=False)
# ---- AI B: anomaly engine injected-error test
m=pd.read_csv('ka-district-msme-employment-2025.csv',encoding='utf-8-sig'); m=m[m.District!='TOTAL'].reset_index(drop=True)
y=pd.read_csv('ka-district-yuvanidhi-2025.csv',encoding='utf-8-sig'); y=y[y.District!='Total'].reset_index(drop=True)
print('msme rows',len(m),'yuva rows',len(y))
def internal(m):
    f=set()
    s=(m['Micro Employment']+m['Small Employment']+m['Medium Employment']-m['Total Employed']).abs()>0
    u=(m['Micro Units']+m['Small units']+m['Medium Units']-m['Total Enterprises']).abs()>0
    f|=set(m.index[s|u]); return f
print('clean internal-sum flags',sorted(m.District[list(internal(m))]))
def mad_flags(m,thr=3.5):
    r=np.log(m['Micro Employment']/m['Micro Units']); z=(r-r.median())/(1.4826*(r-r.median()).abs().median())
    return set(m.index[z.abs()>thr])
base=mad_flags(m); print('clean MAD flags',sorted(m.District[list(base)]))
def trial(kind,fac):
    mm=m.copy(); i=rng.integers(0,len(mm)); col=rng.choice(['Micro Employment','Micro Units','Total Employed','Total Enterprises'])
    mm.loc[i,col]=int(round(mm.loc[i,col]*fac)); fl=(internal(mm)|mad_flags(mm))
    return i in fl, len(fl-base-{i}), i in internal(mm), i in mad_flags(mm)
res={}
for fac in (10,.1,3,1/3,1.5,1/1.5,1.2,1/1.2):
    r=[trial('',fac) for _ in range(500)]; res[fac]=(np.mean([a[0] for a in r]),np.mean([a[1] for a in r]))
    print('factor %.2f recall %.2f avg extra flags %.2f | internal-sum alone %.2f MAD alone %.2f'%(fac,res[fac][0],res[fac][1],np.mean([a[2] for a in r]),np.mean([a[3] for a in r])))
# precision at x10 / x0.1 / x3 combined
allr=[trial('',f) for f in (10,.1,3,1/3) for _ in range(500)]
tp=sum(a[0] for a in allr); fp=sum(a[1] for a in allr); print('large-error (3x-10x) precision %.2f recall %.2f'%(tp/(tp+fp),tp/len(allr)))
# ---- AI C: shrinkage thinning validation
n=d.pop2011.values.astype(float); Y=d['Grand Total'].values
def eb(y,n):
    r=y/n; mu=y.sum()/n.sum(); v=np.average((r-mu)**2,weights=n); noise=np.average(mu/n,weights=n); tau=max(v-noise,1e-12)
    w=tau/(tau+mu/n); return mu+w*(r-mu)
rawE=[];ebE=[]
for _ in range(2000):
    a=rng.binomial(Y.astype(int),.5); b=Y-a
    ra=a/(n*.5); tb=b/(n*.5); rawE.append(np.mean((ra-tb)**2)); ebE.append(np.mean((eb(a,n*.5)-tb)**2))
print('thinning MSE raw %.3g EB %.3g reduction %.1f%%'%(np.mean(rawE),np.mean(ebE),100*(1-np.mean(ebE)/np.mean(rawE))))
w=(1.0/(1+ (Y.sum()/n.sum())/n/ max(np.average((Y/n-Y.sum()/n.sum())**2,weights=n)-np.average((Y.sum()/n.sum())/n,weights=n),1e-12)))
print('smallest-pop district shrink weight',round(float(1/(1+ (Y.sum()/n.sum())/n.min()/max(np.average((Y/n-Y.sum()/n.sum())**2,weights=n)-np.average((Y.sum()/n.sum())/n,weights=n),1e-12))),3))
# ---- AI D: claim checker
eng=d.set_index('District')
def brief(r): return f"{r.District}: {r.dgpi_per_1000:.2f} registrants per 1,000 implied residents (rank {int(r.rank_implied)} of 31); {int(r['Grand Total'])} registrants; income {r.income_lakh:.2f} lakh."
def check(text,r):
    nums=[float(x.replace(',','')) for x in re.findall(r'\d[\d,]*\.?\d*',text)]
    truth={round(r.dgpi_per_1000,2),float(r.rank_implied),float(31),float(r['Grand Total']),round(r.income_lakh,2),1000.0}
    bad=[x for x in nums if not any(abs(x-t)<=1e-9 or abs(x-t)<0.006 for t in truth)]; return len(bad)==0
rs=[r for _,r in d.iterrows()]
cl=[check(brief(r),r) for r in rs]; print('checker clean pass',np.mean(cl))
det=[]
for s_ in rs:
    t=brief(s_); v=f"{s_.dgpi_per_1000:.2f}"; wrong=f"{s_.dgpi_per_1000*rng.choice([1.1,.9,1.25]):.2f}"
    det.append(not check(t.replace(v,wrong,1),s_))
print('checker detects injected wrong DGPI',np.mean(det))
r=np.log(m['Micro Employment']/m['Micro Units']); z=(r-r.median())/(1.4826*(r-r.median()).abs().median())
print(pd.DataFrame({'D':m.District,'ratio':(m['Micro Employment']/m['Micro Units']).round(1),'z':z.round(2)}).reindex(z.abs().sort_values(ascending=False).index).head(6).to_string(index=False))
print('median ratio',round((m['Micro Employment']/m['Micro Units']).median(),2))
for thr in (2.0,2.5,3.0): print('thr',thr,'flags',sorted(m.District[z.abs()>thr]))
