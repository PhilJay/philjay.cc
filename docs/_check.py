#!/usr/bin/env python3
"""Checks the Kotlin snippets in docs/src against the MPAndroidChart sources.

It indexes every type in the library with its members, supertypes and the types of its
properties, then walks each dotted expression in the guides and reports any member that
the receiver type does not have. Run from the repository root:

    python3 docs/_check.py [path/to/MPAndroidChart]
"""

import os
import re
import sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/Programmieren/Personal/MPAndroidChart/MPAndroidChart")
SRCS = [ROOT + "/MPChartLib/src/main/kotlin", ROOT + "/MPChartCompose/src/main/kotlin"]
DOCS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "src")

decl=re.compile(r'^(?P<ind>\s*)(?:@\w+(?:\([^)]*\))?\s*)*(?:public |internal |private |protected |open |abstract |sealed |final |data |enum |annotation |value |inner |fun )*'
                r'(?P<kind>class|interface|object)\s+(?P<name>[A-Za-z_]\w*)')
member=re.compile(r'^(?P<ind>\s*)(?:@\w+(?:\([^)]*\))?\s*)*(?:public |internal |private |protected |open |override |abstract |final |lateinit |const |inline |operator |suspend |external )*'
                  r'(?P<kw>val|var|fun)\s+(?:<[^>]*>\s*)?(?:[A-Za-z_][\w.<>, ?]*\.)?(?P<name>[A-Za-z_]\w*)(?P<rest>.*)')

types={}

def strip_generics(text):
    out,depth="",0
    for ch in text:
        if ch=="<": depth+=1
        elif ch==">": depth=max(0,depth-1)
        elif depth==0: out+=ch
    return out

def type_of(rest, kw):
    rest=rest.strip()
    if kw=="fun":
        after=rest.split(")",1)[-1]
        m=re.match(r'\s*:\s*([A-Z]\w*)',after)
        return m.group(1) if m else None
    m=re.match(r'\s*:\s*([A-Z]\w*)',rest)
    if m: return m.group(1)
    m=re.match(r'\s*=\s*([A-Z]\w*)\s*[({]',rest)
    return m.group(1) if m else None

for base in SRCS:
    for d,_,fs in os.walk(base):
        for f in sorted(fs):
            if not f.endswith(".kt"): continue
            lines=open(os.path.join(d,f)).read().split("\n")
            stack=[]
            for i,line in enumerate(lines):
                m=decl.match(line)
                if m:
                    name,ind=m.group("name"),len(m.group("ind"))
                    while stack and stack[-1][1]>=ind: stack.pop()
                    e=types.setdefault(name,{"members":set(),"supers":set(),"fields":{}})
                    head=" ".join(lines[i:i+16]).split("{",1)[0]
                    if ":" in head:
                        for s in re.findall(r'\b([A-Z]\w*)',strip_generics(head.split(":",1)[1])):
                            e["supers"].add(s)
                    for kw,n,rest in re.findall(r'\b(val|var)\s+(\w+)\s*(:[^,)]*)',head):
                        e["members"].add(n)
                        t=type_of(rest,kw)
                        if t: e["fields"][n]=t
                    if stack:
                        types[stack[-1][0]]["members"].add(name)
                        types[stack[-1][0]]["fields"][name]=name
                    stack.append((name,ind))
                    continue
                mm=member.match(line)
                if mm and stack:
                    ind=len(mm.group("ind"))
                    while len(stack)>1 and stack[-1][1]>=ind: stack.pop()
                    e=types[stack[-1][0]]
                    e["members"].add(mm.group("name"))
                    t=type_of(mm.group("rest"),mm.group("kw"))
                    if t: e["fields"].setdefault(mm.group("name"),t)
                    continue
                em=re.match(r'^(\s*)([A-Z][A-Z0-9_]{1,})\s*(?:\(|,|;|$)',line)
                if em and stack:
                    ind=len(em.group(1))
                    while len(stack)>1 and stack[-1][1]>ind: stack.pop()
                    for name in re.findall(r'\b([A-Z][A-Z0-9_]{1,})\b',line.split("//")[0]):
                        types[stack[-1][0]]["members"].add(name)

def collect(name,key,seen=None):
    seen=seen or set()
    if name in seen or name not in types: return set() if key=="members" else {}
    seen.add(name)
    if key=="members":
        out=set(types[name]["members"])
        for s in types[name]["supers"]: out|=collect(s,key,seen)
        return out
    out=dict(types[name]["fields"])
    for s in types[name]["supers"]:
        for k,v in collect(s,key,seen).items(): out.setdefault(k,v)
    return out

MEMBERS={n:collect(n,"members") for n in types}
FIELDS={n:collect(n,"fields") for n in types}
VIEW={"setBackgroundColor","invalidate","postInvalidate","context","width","height","findViewById","post","setOnClickListener",
      "layoutParams","visibility","measure","layout","addView","removeView","alpha","translationX","translationY","id","resources",
      "setLayerType","paddingLeft","setPadding","requestLayout","getDrawable","background","setBackgroundResource",
      "measuredWidth","measuredHeight","apply","also","let","toString","hashCode","equals","copy","size","first","last",
      "forEach","map","filter","indices","isEmpty","isNotEmpty","sortedBy","toFloat","toInt","toLong","toDouble","joinToString"}

problems=[]
for f in sorted(os.listdir(DOCS)):
    if not f.endswith(".md"): continue
    text=open(os.path.join(DOCS,f)).read()
    for block in re.finditer(r"```kotlin\n(.*?)```",text,re.S):
        code,start=block.group(1),text[:block.start()].count("\n")+2
        varc={}
        for m in re.finditer(r'\b(?:val|var)\s+(\w+)\s*(?::\s*([A-Z]\w*))?\s*=\s*([A-Z]\w*)\s*[({]',code):
            varc[m.group(1)]=m.group(2) or m.group(3)
        for m in re.finditer(r'\b(?:val|var)\s+(\w+)\s*:\s*([A-Z]\w*)',code):
            varc.setdefault(m.group(1),m.group(2))
        for m in re.finditer(r'\b([A-Za-z_]\w*)((?:\.[A-Za-z_]\w*)+)',code):
            head=m.group(1)
            current=varc.get(head) or (head if head in types else None)
            if not current: continue
            line=start+code[:m.start()].count("\n")
            for seg in m.group(2).lstrip(".").split("."):
                if current not in MEMBERS: break
                if seg not in MEMBERS[current] and seg not in VIEW:
                    problems.append((f,line,f"{current}.{seg}"))
                    break
                current=FIELDS.get(current,{}).get(seg)
                if not current: break
seen=set()
for f,line,what in problems:
    if (f,what) in seen: continue
    seen.add((f,what))
    print(f"{f}:{line}  {what}")
print(f"{len(types)} types indexed, {len(seen)} snippet problems")
raise SystemExit(1 if seen else 0)
