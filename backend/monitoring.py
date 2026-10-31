"""Reproducible model performance and uncertainty diagnostics."""
from __future__ import annotations
import math
from statistics import mean,median
def evaluate_intervals(actual:list[float],point:list[float],lower:list[float],upper:list[float])->dict:
    if not actual or not(len(actual)==len(point)==len(lower)==len(upper)):
        raise ValueError("All arrays must have equal nonzero lengths")
    if any(not all(map(math.isfinite,values)) for values in zip(actual,point,lower,upper)):
        raise ValueError("Non-finite values")
    if any(l>u for l,u in zip(lower,upper)):
        raise ValueError("Invalid prediction interval")
    return {"n":len(actual),"mae":round(mean(abs(y-p) for y,p in zip(actual,point)),3),
            "median_absolute_error":round(median(abs(y-p) for y,p in zip(actual,point)),3),
            "empirical_coverage":round(mean(l<=y<=u for y,l,u in zip(actual,lower,upper)),4),
            "mean_interval_width":round(mean(u-l for l,u in zip(lower,upper)),3),
            "note":"Coverage must be compared with the declared nominal interval level on independent data."}
def population_stability_index(reference:list[float],current:list[float],bins:int=10)->dict:
    if not reference or not current:raise ValueError("Both samples required")
    if any(not math.isfinite(v) for v in reference+current):raise ValueError("Non-finite values")
    a=sorted(reference)
    edges=[a[min(len(a)-1,int(len(a)*i/bins))] for i in range(1,bins)]
    def frequencies(vals):
        counts=[0]*(bins)
        for x in vals:
            idx=sum(x>edge for edge in edges)
            counts[idx]+=1
        n=len(vals)
        return [max(v/n,1e-6) for v in counts]
    p,q=frequencies(reference),frequencies(current)
    psi=sum((x-y)*math.log(x/y) for x,y in zip(p,q))
    return {"psi":round(psi,4),"reference_count":len(reference),"current_count":len(current),
            "note":"PSI is a descriptive drift indicator, not a substitute for accuracy monitoring."}
