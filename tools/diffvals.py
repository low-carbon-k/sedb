import sys, rdflib, difflib
d = rdflib.Graph().parse(sys.argv[1], format="nt"); r = rdflib.Graph().parse(sys.argv[2], format="xml")
kinds = {}
n=0
for s,p,o in sorted(d):
    if (s,p,o) in r or str(s)=="http://dydra.com/": continue
    ro = list(r.objects(s,p))
    if len(ro)!=1: print("multi", s, p, len(ro)); continue
    a, b = str(o), str(ro[0])
    if a.split()==b.split(): k="whitespace only"
    elif a.replace("\r","")==b.replace("\r",""): k="CR only"
    else: k="text"
    kinds[k]=kinds.get(k,0)+1
    if k=="text" and n<4:
        n+=1
        for op in difflib.SequenceMatcher(None,a,b).get_opcodes():
            if op[0]!="equal": print(p.split("#")[1], op[0], repr(a[op[1]:op[2]][:60]), "->", repr(b[op[3]:op[4]][:60]))
    if o.language!=ro[0].language or o.datatype!=ro[0].datatype: print("lang/dt differ", o.language, ro[0].language, o.datatype, ro[0].datatype)
print(kinds)
