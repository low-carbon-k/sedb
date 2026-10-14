import sys, rdflib
from rdflib.compare import to_isomorphic, graph_diff
from collections import Counter
SE = rdflib.Namespace("http://www.teitanso.org/2012/04/se#")
d = rdflib.Graph().parse(sys.argv[1], format="nt")
r = rdflib.Graph().parse(sys.argv[2], format="xml")
print("dydra triples", len(d), "repo triples", len(r))
for name, g in [("dydra", d), ("repo", r)]:
    types = Counter(o for o in g.objects(None, rdflib.RDF.type))
    print(name, "types", dict(types))
    print(name, "subjects", len(set(g.subjects())), "with se:title", len(set(g.subjects(SE.title))), "with se:exTitle", len(set(g.subjects(SE.exTitle))), "exRdfName targets", len(set(g.objects(None, SE.exRdfName))))
both, only_d, only_r = graph_diff(to_isomorphic(d), to_isomorphic(r))
print("same", len(both), "only dydra", len(only_d), "only repo", len(only_r))
print("subjects only in dydra:", sorted({str(s) for s in only_d.subjects()} - {str(s) for s in r.subjects()}))
print("subjects only in repo:", sorted({str(s) for s in only_r.subjects()} - {str(s) for s in d.subjects()}))
print("predicates changed (both sides have subject):")
c = Counter(str(p) for s,p,o in only_d if (s,None,None) in r)
print(" dydra side", c)
c = Counter(str(p) for s,p,o in only_r if (s,None,None) in d)
print(" repo side", c)
for s in sorted({s for s in only_d.subjects()} - set(r.subjects())):
    print(s, d.value(s, SE.title) or d.value(s, SE.exTitle), "| exp:", d.value(d.value(s, SE.exRdfName), SE.exTitle) if d.value(s, SE.exRdfName) else "")
