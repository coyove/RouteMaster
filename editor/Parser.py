from MapData import MapDataElement


def parseBS(s: str):
    i = 0
    buf = ""
    row = []
    def app(x):
        x = x.strip()
        row.append(x)
        return ''

    rows = []
    s = s.replace('~~', '\\').replace('! !', '\\')
    while i < len(s):
        if s[i] == '\\':
            i = i + 1
            buf = app(buf)
            continue
        if s[i] == '\n':
            i = i + 1
            buf = app(buf)
            rows.append(row)
            row = []
            continue
        buf += s[i]
        i = i + 1
        
    app(buf)
    rows.append(row)

    for row in rows:
        for i in range(len(row)):
            if row[i].count('!~') > 0:
                row[i] = row[i].split('!~')
            if row[i] == 'leer':
                row[i] = ''

    for i in range(len(rows) - 1, -1, -1):
        if len(rows[i]) == 1 and rows[i][0] == '':
            del rows[i]

    return rows

def filterBS(rows):
    c = []
    rowsEl, maxRowWidth = [], 0
    for y in range(len(rows)):
        x = 0
        rowEl = []
        while x < len(rows[y]):
            d = rows[y][x]
            if not d:
                x = x + 1
                continue
            el = MapDataElement.createWithXY(x, y, d)
            if el:
                c.append(el)
                rowEl.append(el)
            elif x == 0:
                d = str(d)
                for xx in range(1, len(rows[y])):
                    el = MapDataElement.createWithXY(x, y, rows[y][xx])
                    if el:
                        el.text, el.textAlign, el.textPlacement = d, 'r', 'l'
                        c.append(el)
                        rowEl.append(el)
                        rows[y][0:xx] = []
                        break
                    else:
                        d = d + str(rows[y][xx])
            elif c:
                el: MapDataElement = c[-1]
                el.text, el.textAlign, el.textPlacement = str(d), 'l', 'r'
            x = x + 1
        if rowEl:
            maxRowWidth = max(rowEl[-1].x, maxRowWidth)
            rowsEl.append(rowEl)
    maxRowWidth = maxRowWidth // 2 * 2 + 1 # keep it odd
    for row in rowsEl:
        prepend = (maxRowWidth - row[-1].x) // 2
        if prepend > 0:
            for el in row:
                el.x = el.x + prepend
    return c
    
if __name__ == "__main__":
    print(parseBS(r"""
        KBHFa~~起點
WASSERq\hKRZW\WASSERq~~ ~~ ~~ ~~天橋
LDER\INT\~~1公里~~中途站~~轉乘高鐵
\KBHFe\BUS~~2公里~~終點~~巴士總站
"""))
    raise 1
    print(parseBS(r"""
CONTg~~ ~~ ~~ ~~{{RoutemapRoute|Licon=u|[[京沪铁路]]往{{站|北京}}}}
\\ABZg+l\STRq\STR+r~~ ~~ ~~ ~~{{RoutemapRoute|Licon=r|[[京津城际铁路|京津城际]]往{{站|天津}}}}
\\BHF\\LSTR~~0~~'''{{站|北京南}}'''
LSTR+l\LSTRq\ABZgr\\LSTR~~ ~~ ~~ ~~{{RoutemapRoute|Licon=l|[[京沪铁路]]往{{站|上海}}}}
LSTR\\hSTRa@g\\LSTR~~ ~~ ~~ ~~[[北京特大桥]]
LSTR\CONTgq\hABZgr\\LSTR~~ ~~ ~~ ~~{{RoutemapRoute|Licon=l|联络线往[[北京动车段]]}}
LSTRl\LSTRq\hKRZ\STR+r\LSTR~~ ~~ ~~ ~~{{RoutemapRoute|上跨[[京沪铁路]]、[[京九铁路]]}}
\CONTgq\hKRZ\ABZgr\LSTR~~ ~~ ~~ ~~{{RoutemapRoute|Licon=l|[[京九铁路]]往{{站|常平}}方向}}
\\hSTRe@f\LSTR\LSTR
\\HST\LSTR\LSTR~~59~~{{站|廊坊}}
\\hSTRa@g\LSTR\LSTR~~ ~~ ~~ ~~[[天津特大桥]]
\CONTgq\hKRZ\ABZql\ABZg+r~~ ~~ ~~ ~~{{RoutemapRoute|Licon=l|[[津霸铁路]]往{{站|霸州}}}}
\\hSTR\\STR~~ ~~ ~~ ~~{{RoutemapRoute|Licon=u|[[京津城际铁路|京津城际]]、[[京沪线]]往{{站|北京南}}}}

\\\hSTR\leer\ABZgl+l\CONTfq~~ ~~ ~~ ~~{{RoutemapRoute|Licon=r|[[京津城际铁路|京津城际]]、[[津山铁路]]往{{站|北京南}}}}
\\\hSTR\\ABZg+l\tCONTfq~~ ~~ ~~ ~~{{RoutemapRoute|Ricon=r|[[天津地下直径线]]往{{站|天津}}}}
\\hSTR\\BHF~~ ~~'''{{站|天津西}}''' 
\\hABZgl\hSTReq\ABZgr
\\hSTR\KBSTaq\ABZgr~~ ~~ ~~ ~~[[曹庄动车运用所]]
\CONTgq\hKRZhu\hSTRq\hABZgr~~ ~~ ~~ ~~{{RoutemapRoute|Licon=l|[[津保铁路]]往{{站|保定}}}}
\LSTR+l\hKRZ\HSTq\ABZgr~~ ~~ ~~ ~~[[京沪铁路]][[曹庄站]]
\LSTR\hABZg+l\STRq\STRr
LSTR\hSTR\
LSTR\hHST\~~131~~{{站|天津南}}
LSTR\hSTR\
LSTR\hSTR\
LSTRl\hKRZ\LSTR+r~~ ~~ ~~ ~~{{RoutemapRoute|上跨[[京沪铁路]]}}
CONTgq\hKRZ\KRZo+l~~ ~~ ~~ ~~{{RoutemapRoute|上跨[[朔黄铁路]]}}
\hSTRe@f\LSTR
\HST\LSTR~~219~~{{站|沧州西}}
\hSTRa@g\LSTR
LSTR+l\hKRZ\LSTRr~~ ~~ ~~ ~~{{RoutemapRoute|上跨[[京沪铁路]]}}
LSTRe\hSTR\
CONTgq\hKRZ\CONTfq~~ ~~ ~~ ~~{{RoutemapRoute|上跨[[邯黄铁路]]}}
hSTRe@f
CONTgq\ABZg+r\~~ ~~ ~~ ~~{{RoutemapRoute|Licon=l|[[石济客运专线|石济客专]]往{{站|石家庄}}}}
HST~~327~~{{站|德州东}}
\ABZgl\LSTR+r
\CONTgq\KRZo\KRZo\CONTfq~~ ~~ ~~ ~~{{RoutemapRoute|上跨[[德大铁路]]}}
\STR\LSTR
\\ABZg+l\LABZql\LCONTfq~~ ~~ ~~ ~~{{RoutemapRoute|Licon=r|[[石济客运专线|石济客专]]往[[济南东站]]}}
hSTRa@g
CONTgq\hKRZ\CONTfq~~ ~~ ~~ ~~{{RoutemapRoute|上跨[[邯济铁路]]}}
LSTRa!~WASSERq\hKRZW\WASSERq~~ ~~ ~~ ~~[[济南黄河特大桥]]
LSTRe!~LSTRl\hKRZ\STR+r~~ ~~ ~~ ~~{{RoutemapRoute|上跨[[济南线]]}}
CONTgq\hABZg+r\LSTR~~ ~~ ~~ ~~{{RoutemapRoute|Licon=l|往[[济南西动车运用所]]}}
LSTRa\hSTRe@f\LSTRe
LSTR\BHF\LSTRa~~419~~'''{{站|济南西}}'''
LSTR\STR\BHF~~ ~~[[济南站|{{小|济南}}]]
LSTR!~LSTRl\hKRZa\LSTR!~LSTRr~~ ~~ ~~ ~~{{RoutemapRoute|上跨[[济南线]]}}
LSTR\hABZgl+l\ABZgr!~hSTRra
LSTRl\hKRZ\LSTR!~LSTR+r~~ ~~ ~~ ~~{{RoutemapRoute|上跨[[京沪铁路]]}}
\\hABZgl+l\KRZh\CONTfq~~ ~~ ~~ ~~{{RoutemapRoute|Licon=r|[[胶济客运专线|胶济客专]]往{{站|青岛}}}}
\hSTRe@f\LSTR
\TUNNEL1\LSTR~~ ~~ ~~ ~~济南泰山区间隧道
CONTgq\KRZo\LSTR!~LSTR+r~~ ~~ ~~ ~~{{RoutemapRoute|Licon=l|[[泰肥铁路]]往{{站|湖屯}}}}
\HST\LSTR~~462~~{{站|泰安}}
\hSTRa@g\LSTR
LSTR+l\hKRZ\STRr~~ ~~ ~~ ~~{{RoutemapRoute|上跨[[京沪铁路]]}}
LSTRe\hSTR\
CONTgq\hKRZ\CONTfq~~ ~~ ~~ ~~{{RoutemapRoute|上跨[[瓦日铁路]]}}
CONTgq\hKRZ\CONTfq~~ ~~ ~~ ~~{{RoutemapRoute|上跨[[磁莱铁路]]}}
CONTgq\hKRZ\CONTfq~~ ~~ ~~ ~~{{RoutemapRoute|上跨[[新石铁路]]}}
hSTRe@f
HST~~533~~{{站|曲阜东}}
exCONTgq\KRZolr\CONTfq~~ ~~ ~~ ~~{{RoutemapRoute|Licon=l|{{站|兰考南}}|[[鲁南客运专线|鲁南客专]] – {{站|临沂北}}|Ricon=r}}
HST~~589~~{{站|滕州东}}
CONTgq\KRZo\CONTfq~~ ~~ ~~ ~~{{RoutemapRoute|上跨[[枣临铁路]]}}
HST~~625~~{{站|枣庄}}
CONTgq\ABZg+r\~~ ~~ ~~ ~~{{RoutemapRoute|Licon=l|[[郑徐客运专线|郑徐客专]]往{{站|郑州东}}}}
BHF~~688~~'''{{站|徐州东}}'''
dCONTgq\dHSTq\KRZor\CONTfq~~ ~~ ~~ ~~[[陇海铁路]][[大湖站 (江苏省)|大湖站]]
CONTgq\KRZo\CONTfq~~ ~~ ~~ ~~{{RoutemapRoute|上跨[[宿淮铁路]]}}
HST~~767~~{{站|宿州东}}
WASSERq\hKRZWae\WASSERq~~ ~~ ~~ ~~[[蚌埠淮河特大桥]]
LSTRa\STR\
LSTRl\KRZo+r\LSTR+r~~ ~~ ~~ ~~{{RoutemapRoute|Licon=l|蚌南联络线往[[京沪铁路]]{{站|蚌埠}}}}
\BHF\LSTRe~~844~~'''{{站|蚌埠南}}'''
CONTgq\ABZgr\~~ ~~ ~~ ~~{{RoutemapRoute|Licon=l|[[合蚌客运专线|合蚌客专]]往{{站|合肥}}}}
HST~~897~~{{站|定远}}
HST~~959~~{{站|滁州}}
<!--合宁铁路现状引入合肥枢纽合肥站；合肥南环线、合肥南站启用后，也可引入合肥南站-->
CONTgq\KRZo+r\CONTfq~~ ~~ ~~ ~~{{RoutemapRoute|Licon=l|[[宁合铁路]]往{{站|合肥}}|永亭线往{{站|永宁镇}}|Ricon=r}}
WASSERq\hKRZWae\WASSERq~~ ~~ ~~ ~~[[南京大胜关长江大桥 (铁路)|南京大胜关长江大桥]]
CONTgq\KRZo\CONTfq~~ ~~ ~~ ~~{{RoutemapRoute|上跨[[宁铜铁路]]}}
\ABZg+l\KBSTeq~~ ~~ ~~ ~~{{RoutemapRoute|Licon=r|[[南京南动车运用所]]}}
CONTgq\ABZg+r\ ~~ ~~ ~~ ~~{{RoutemapRoute|Licon=l|[[宁安城际铁路|宁安城际]]往{{站|安庆}}}}
BHF~~1018~~'''{{站|南京南}}'''
CONTgq\ABZgr\~~ ~~ ~~ ~~{{RoutemapRoute|Licon=l|[[宁杭客运专线|宁杭客专]]往{{站|杭州东}}、{{站|杭州}}}}
\ABZgl\CONTfq~~ ~~ ~~ ~~{{RoutemapRoute|Licon=r|''[[仙宁铁路]]''往[[沪宁城际铁路|沪宁城际]]}}
HST~~1087~~{{站|镇江南}}
\hSTRa@g\vCONTg~~ ~~ ~~ ~~{{RoutemapRoute|Ricon=u|往{{站|北京}}|Licon=u|往{{站|南京}}}}
vSTR+l\hKRZv\vSTRr~~ ~~ ~~ ~~{{RoutemapRoute|上跨[[京沪铁路]]、[[沪宁城际]]}}
vLSTR\hSTRe@f\
vLSTR\HST\~~1112~~{{站|丹阳北}}
vLSTR\hSTRa@g\~~ ~~ ~~ ~~[[丹昆特大桥]]
vLSTR\hHST\~~1144~~{{站|常州北}}
CONTgq\ABZq2\vKRZu\hKRZ\CONTfq\\~~ ~~ ~~ ~~{{RoutemapRoute|上跨[[新长铁路]]}}
vABZg+4-STR\hSTR\
vLSTR\hHST\~~1201~~{{站|无锡东}}
vLSTR\hHST\~~1227~~{{站|苏州北}}
vSTRl-SHI1ro\hKRZ\STR+r
hBHF-L\hBHF-R\LSTR~~1259~~{{站|崑山南}}
vSTR+l-SHI1+ro\hKRZ\STRr
vLSTR\hSTRe@f\
vLSTR\hSTRa@g\~~ ~~ ~~ ~~上海特大桥
\vSTR-ABZgl\KRZl!~hABZgl\hSTR+re\~~ ~~ ~~ ~~{{BSsplit|{{rmri|c2}}黄渡联络线往[[站|上海]]|{{RoutemapRoute|Licon=l|[[沪宁城际铁路|沪宁城际]]往[[站|南京]]}}}}
\\vSTRl-SHI1ro\hKRZ\ABZql+l\BHFq\CONTfq~~ ~~ ~~ ~~{{rmri|left}}[[京沪铁路]]往[[北京站|北京]] <big>'''[[上海站|上海]]'''</big> 往[[上海客技站]]{{rmri|r}}
CONTgq\KRZo+l\hKRZ\STRr\~~ ~~ ~~ ~~{{RoutemapRoute|Licon=l|[[沪昆铁路]]往{{站|昆明}}}}
STR\hSTRe@f\~~ ~~ ~~ ~~
STRl\ABZg+lr\CONTfq~~ ~~ ~~ ~~{{BSsplit|{{RoutemapRoute|Licon=l|虹安联络线往[[站|南京南]]}}|{{RoutemapRoute|Licon=r|虹所出库线往[[上海动车段|上海动车段（虹桥）]]}}|align=right}}
BHF~~1302~~{{nowrap|'''{{站|上海虹桥}}''' [[虹桥综合交通枢纽]]}}{{rint|air|link=上海虹桥国际机场}}
CONTf~~ ~~ ~~ ~~{{RoutemapRoute|Licon=d|[[沪杭高速铁路|沪杭高铁]]往{{站|杭州东}}}}
    """))