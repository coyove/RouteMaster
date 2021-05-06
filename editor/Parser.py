from Common import BS
from MapData import MapDataElement


def parseBS(s: str):
    if not "{{Routemap" in s:
        return parseBSOld(s)

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

def parseBSOld(s: str):
    rows = []
    for l in s.split('\n'):
        l = l.strip().strip("{}")
        if not l or not l.startswith("BS"):
            continue
        if l.startswith("BS-map"):
            continue
        count = int(l[2])
        row = l.split("|")[1:]
        i = 0
        while i < len(row):
            if row[i].startswith("O") and i > 0:
                x = row[i].split('=')[1]
                row[i - 1] = row[i - 1] + [x] if isinstance(row[i-1], list) else [row[i-1], x]
                row = row[:i] + row[i+1:]
            else:
                i = i + 1
        if len(row) > count:
            row[count - 1] = ' '.join(row[count:]).strip()
            row = row[:count]
        rows.append(row)
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
        if not row:
            continue
        prepend = (maxRowWidth - row[-1].x) // 2
        if prepend > 0:
            for el in row:
                el.x = el.x + prepend
        if row[-1].text:
            row[-1].textX = (maxRowWidth - row[-1].x) * BS
    return c
    
if __name__ == "__main__":
    print(parseBSOld("""
    {{出典の明記|date=2019年9月}}
{{Infobox 鉄道路線
|路線名   = 上海軌道交通3号線（明珠線）
|路線色   = #ffd100
|ロゴ     = SMLine3.svg
|ロゴサイズ=100px
|画像     = Shanghai Metro Line 3 AC03 Train WestYangangRoad.jpg
|画像サイズ = 300px
|画像説明 = 03A01型
|通称     = 軽軌（轻轨）
|国       = {{CHN}}
|種類     = [[地下鉄]]
|路線網   = [[上海軌道交通]]
|起点     = [[上海南駅|上海南站駅]]
|終点     = [[江楊北路駅]]
|駅数     = 29[[駅]]
|路線記号 = M3
|路線番号 = 3
|路線色3={{Color|#ffd100|■}}[[黄色]]
|開業     = 2000年12月16日
|所有者   = 上海軌道交通明珠線发展有限公司、上海軌道交通宝山線发展有限公司
|運営者   = [[上海轨道交通]]
|路線構造 = 高架・地上・地下
|路線距離 = 40.340 [[キロメートル|km]]
|営業キロ= ? km
|軌間     = 1,435  [[ミリメートル|mm]] ([[標準軌]])
|線路数   = [[複線]]
|複線区間=全区間
|電化区間=全区間
|電化方式 = [[直流電化|直流]]1,500[[ボルト (単位)|V]] [[架空電車線方式|架線集電方式]]
|最高速度 = 80[[キロメートル毎時|km/h]]
|路線図   = Shanghai Metro Line 3.svg
|路線図名 = 上海軌道交通3号線
}}
{{BS-map|title=営業区間|title-bg=#ffd100|title-color=black|collapse=yes
|map=
{{BS3|uKBHFa|||0|[[江楊北路駅|江楊北路]]||}}
{{BS3|uKRWgl|uKRW+r|||||}}
{{BS3|utSTRa|uKDSTe|||江楊北路車両基地||}}
{{BS5|STRq|umtKRZ|STRq|||||[[中華人民共和国鉄道部|国鉄]]宝鋼支線|}}
{{BS3|utBHF|||3|[[鉄力路駅|鉄力路]]||}}
{{BS3|uhtSTRe||||||}}
{{BS3|uhBHF|||6|[[友誼路駅 (上海市)|友誼路]]||}}
{{BS3|uhBHF|||8|[[宝楊路駅|宝楊路]]||}}
{{BS3|uhBHF|||11|[[水産路駅|水産路]]||}}
{{BS3|uhBHF|||13|[[淞浜路駅|淞浜路]]||}}
{{BS3|uhBHF|||16|[[張華浜駅|張華浜]]||}}
{{BS3|uhBHF|||18|[[淞発路駅|淞発路]]||}}
{{BS3|uhBHF|||22|[[長江南路駅|長江南路]]||}}
{{BS5|STRq|umhKRZ|STRq|||||国鉄南何支線|}}
{{BS3|uhBHF|||24|[[殷高西路駅|殷高西路]]||}}
{{BS3|uhBHF|||27|[[江湾鎮駅|江湾鎮]]||}}
{{BS3|uhBHF|||30|[[大柏樹駅|大柏樹]]||}}
{{BS3|uhBHF|||33|[[赤峰路駅|赤峰路]]||}}
{{BS5|utSTRq|mhKRZt|O2=uBHF|utSTRq|||35|[[虹口足球場駅|虹口足球場]]|{{Color|#009dd9|●}}[[上海軌道交通8号線|8号線]]|}}
{{BS3|uhBHF|||37|[[東宝興路駅|東宝興路]]||}}
{{BS5||uhABZg+l|uhSTRq|uhtSTRaq|utSTR+r|O5=POINTERf@g|||{{Color|#660066|●}}[[上海軌道交通4号線|4号線]]|}}
{{BS5||uhBHFe|||uLSTR|40|[[宝山路駅|宝山路]]||}}
{{BS3|uSTR|ENDEa|utENDEa|||↓{{Color|#660066|●}}4号線共用区間|}}
{{BS3|uBHF|O1=HUBaq|BHF|O2=HUBq|utÜST|O3=HUBlg|43|[[上海駅 (上海地下鉄)|上海火車站]]||}}
{{BS5|utSTRq|uKRZt|mKRZt|utABZg+r|O4=HUB||||{{Color|#EA0437|●}}[[上海軌道交通1号線|1号線]]|}}
{{BS5|STRq|umhKRZa|STRr|utBHF|O4=HUBe||||国鉄[[京滬線]]|}}
{{BS3|uhBHF||uLSTR|46|[[中潭路駅|中潭路]]||}}
{{BS5|utSTRq|mhKRZt|O2=uBHF|utSTRq|||49|[[鎮坪路駅|鎮坪路]]|{{Color|#ff7200|●}}[[上海軌道交通7号線|7号線]]|}}
{{BS5|utSTRq|mhKRZt|O2=uBHF|utSTRq|||52|[[曹楊路駅|曹楊路]]|{{Color|#841c21|●}}[[上海軌道交通11号線|11号線]]|}}
{{BS3|uhBHF|||54|[[金沙江路駅|金沙江路]]||}}
{{BS5|WASSERq|uhKRZW|WASSERq|||||[[呉淞江|蘇州河]]|}}
{{BS5|utSTRq|mhKRZt|O2=uBHF|utSTRq|||57|[[中山公園駅|中山公園]]|{{Color|#87D300|●}}[[上海軌道交通2号線|2号線]]|}}
{{BS3|uhBHF|||59|[[延安西路駅|延安西路]]||}}
{{BS3|uhSTR|||||↑{{Color|#660066|●}}4号線共用区間|}}
{{BS5|utSTRq|mhKRZt|O2=uBHF|utSTRq|||62|[[虹橋路駅|虹橋路]]|{{Color|#c0a8e0|●}}[[上海軌道交通10号線|10号線]]|}}
{{BS3|uhABZgl|uhSTR+r|O2=POINTERf@g||||{{Color|#660066|●}}4号線|}}
{{BS3|uhSTR|htSTRa|O2=utSTRa|||||}}
{{BS5||O1=HUBrg|uhBHF|O2=HUBq|utBHF|O3=HUBeq|||64|[[宜山路駅|宜山路]]||}}
{{BS5|utBHFq|O1=HUBe|uhKRZt|utKRZt|||||{{Color|#78C7EB|●}}[[上海軌道交通9号線|9号線]]|}}
{{BS5||uhSTR|utSTR|uLSTR|||||}}
{{BS5|utSTR+l|uhKRZt|utTHSTt|utSTRr|uLSTR|||{{Color|#EA0437|●}}1号線・{{Color|#660066|●}}4号線 [[上海体育館駅|上海体育館]]|}}
{{BS5|uLSTR|uhBHF|utSTRl|utSTRq|utSTRr|67|[[漕渓路駅|漕渓路]]||}}
{{BS3|uhBHFe|||69|[[竜漕路駅|龍漕路]]||}}
{{BS3|uBHF|||72|[[石竜路駅|石龍路]]||}}
{{BS3|uSTR2|O1=uSTRl|uSTRq|O2=uSTRc3|uSTR+r||||}}
{{BS3|uSTRc1|O1=ENDEa|uSTR+4|uKDSTe|||石龍路留置線|}}
{{BS5|uLSTR|uKRW+l|O2=STR|uKRWgr|||||国鉄連絡線（{{Color|#EA0437|●}}1号線へ連絡）|}}
{{BS5|utBHF|O1=HUBaq|BHF|O2=HUBq|uKBHFe|O3=HUBeq|||74|[[上海南駅 (上海地下鉄)|上海南站]]||}}
{{BS5|utSTR|STR||||||国鉄[[滬杭線]]|}}
{{BS5|utSTR|||||||{{Color|#EA0437|●}}1号線|}}
}}
'''上海軌道交通3号線'''（シャンハイきどうこうつう3ごうせん、、{{中文表記|上海轨道交通3号线}}、{{英文表記|Shanghai Metro Line 3}}）、別名'''明珠線'''（めいじゅせん、{{中文表記|明珠线}}）と宝山線は、[[上海軌道交通]]の[[鉄道路線|路線]]。現地では'''軽軌'''（{{Lang|zh|轻轨}}）と呼ばれる。

== 概要 ==
[[2000年]]12月26日に開業。北延長第1期工程[[2006年]]12月18日開通後、営業距離は40.3キロになり、一時は上海市内で最も長い地下鉄路線であった。

全区間ATO制御による運転である。地下鉄の仲間であるが、全区間高架線を走る。

=== 路線データ ===
* 路線距離：40.340km
* [[軌間]]：1435mm
* 駅数：29駅（起終点駅含む）
* 複線区間：全線
* 電化区間：全線（直流1500V）
<!--* [[閉塞 (鉄道)|閉塞方式]]：?-->
* 最高速度: 80km/h
* 地上区間：[[上海南駅]] - [[石竜路駅]]東北、[[中潭路駅]]西 - [[宝山路駅]]西、[[鉄力路駅]]西-[[江楊北路駅]]
* 地下区間：[[友誼路駅]]西 - [[鉄力路駅]]西
* 高架区間：[[石竜路駅]]東北 - [[中潭路駅]]西、[[宝山路駅]]西 - [[江湾鎮駅]] - [[友誼路駅]]西

== 歴史 ==
* [[2000年]][[12月16日]]<ref>{{Cite journal|和書 |date = 2001-05-01 |title = Overseas Railway Topics |journal = 鉄道ジャーナル |issue = 5 |volume = 35 |publisher = 鉄道ジャーナル社 |page = 119 }}</ref>：[[上海南駅駅]] - [[江湾鎮駅]]が開通。
* [[2006年]][[12月18日]]：[[江湾鎮駅]] - [[江楊北路駅]]が開通。
* [[2014年]]：新型車両・[[上海軌道交通03A02型]]電車を導入
* [[2015年]][[7月10日]]：新型車両・[[上海軌道交通03A02型]]電車の営業開始

== 車両 ==
{{Seealso|アルストム・メトロポリス}}
; [[上海軌道交通03A01型]]電車
* 製造会社：[[アルストム]]、[[南京浦鎮車輛廠]]
* 設計最高速度：80km/h
* ATO制御
* 車両編成：6両編成（制御車＋4×中間電動車＋制御車）
* 車両：長さ23.54m、幅3m
* 定員：310人


; [[上海軌道交通03A02型]]電車
* 製造会社：[[中車長春軌道客車]]、[[上海電気]]
* 設計時速：80km/h
* [[編成 (鉄道)|車両編成]]：6両（制御車＋中間電動車×4＋制御車（Tc＋Mp＋M＋M+Mp＋Tc））
* 寸法：長さ23.54m、幅3m
* 定員：310人

== 路線 ==
{| class=wikitable
|-
!colspan="3"|駅名
!rowspan="2" style="border-bottom:solid 3px #ffd100;"|駅間<br/>キロ
!rowspan="2" style="border-bottom:solid 3px #ffd100;"|営業<br/>キロ
!rowspan="2" style="border-bottom:solid 3px #ffd100;"|接続路線・備考
!rowspan="2" style="border-bottom:solid 3px #ffd100;"|所在地
|-
!style="border-bottom:solid 3px #ffd100;"|<small>[[日本語]]</small>
!style="border-bottom:solid 3px #ffd100;"|<small>[[簡体字]][[中国語]]</small>
!style="border-bottom:solid 3px #ffd100;"|<small>[[英語]]</small>
|-
|[[上海南駅駅|上海南站駅]]
|{{lang|zh|上海南站}}
|Shanghai South Railway Station
|align=right|0.000
|align=right|0.000
|上海軌道交通：[[ファイル:SML1.svg|10px|1|link=]] [[上海軌道交通1号線|1号線]]<br />[[中国鉄路総公司]]：[[滬昆線]]・{{Color|gray|■}}[[上海軌道交通22号線|金山支線]]（[[上海南駅]]）
|align=center rowspan=5|[[徐匯区]]
|-
|[[石竜路駅|石龍路駅]]
|{{lang|zh|石龙路站}}
|Shilong Road
|align=right|1.314
|align=right|1.314
|&nbsp;
|-
|[[竜漕路駅|龍漕路駅]]
|{{lang|zh|龙漕路站}}
|Longcao Road
|align=right|1.484
|align=right|2.798
|上海軌道交通：[[ファイル:SML12.svg|10px|12|link=]] [[上海軌道交通12号線|12号線]]
|-
|[[漕渓路駅]]
|{{lang|zh|漕溪路站}}
|Caoxi Road
|align=right|1.025
|align=right|3.823
|&nbsp;
|-
|[[宜山路駅]]
|{{lang|zh|宜山路站}}
|Yishan Road
|align=right|1.538
|align=right|5.361
|上海軌道交通：[[ファイル:SML4.svg|10px|4|link=]] [[上海軌道交通4号線|4号線]]、[[ファイル:SML9.svg|10px|9|link=]] [[上海軌道交通9号線|9号線]]
|-
|[[虹橋路駅]]
|{{lang|zh|虹桥路站}}
|Hongqiao Road
|align=right|1.309
|align=right|6.670
|上海軌道交通：[[ファイル:SML4.svg|10px|4|link=]] [[上海軌道交通4号線|4号線]]、[[ファイル:SML10.svg|10px|10|link=]] [[上海軌道交通10号線|10号線]]
|align=center rowspan=3|[[長寧区]]
|-
|[[延安西路駅]]
|{{lang|zh|延安西路站}}
|West Yan'an Road
|align=right|1.461
|align=right|8.131
|上海軌道交通：[[ファイル:SML4.svg|10px|4|link=]] 4号線
|-
|[[中山公園駅 (上海市)|中山公園駅]]
|{{lang|zh|中山公园站}}
|Zhongshan Park
|align=right|1.101
|align=right|9.232
|上海軌道交通：[[ファイル:SML2.svg|10px|2|link=]] [[上海軌道交通2号線|2号線]]、[[ファイル:SML4.svg|10px|4|link=]] 4号線
|-
|[[金沙江路駅]]
|{{lang|zh|金沙江路站}}
|Jinshajiang Road
|align=right|1.507
|align=right|10.739
|上海軌道交通：[[ファイル:SML4.svg|10px|4|link=]] 4号線、[[ファイル:SML13.svg|10px|13|link=]] [[上海軌道交通13号線|13号線]]
|align=center rowspan=4|[[普陀区 (上海市)|普陀区]]
|-
|[[曹楊路駅]]
|{{lang|zh|曹杨路站}}
|Caoyang Road
|align=right|0.903
|align=right|11.642
|上海軌道交通：[[ファイル:SML4.svg|10px|4|link=]] 4号線、[[ファイル:SML11.svg|10px|11|link=]] [[上海軌道交通11号線|11号線]]
|-
|[[鎮坪路駅]]
|{{lang|zh|镇坪路站}}
|Zhenping Road
|align=right|1.373
|align=right|13.015
|上海軌道交通：[[ファイル:SML4.svg|10px|4|link=]] 4号線、[[ファイル:SML7.svg|10px|7|link=]] [[上海軌道交通7号線|7号線]]
|-
|[[中潭路駅]]
|{{lang|zh|中潭路站}}
|Zhongtan Road
|align=right|1.473
|align=right|14.488
|上海軌道交通：[[ファイル:SML4.svg|10px|4|link=]] 4号線
|-
|[[上海駅|上海火車站駅]]
|{{lang|zh|上海火车站}}
|Shanghai Railway Station
|align=right|1.727
|align=right|16.215
|上海軌道交通：[[ファイル:SML1.svg|10px|1|link=]] [[上海軌道交通1号線|1号線]]（改札外乗換え）、[[ファイル:SML4.svg|10px|4|link=]] 4号線<br/>中国鉄路総公司：[[京滬線]]・[[滬昆線]]・[[滬寧都市間鉄道]]（[[上海駅]]）
|align=center rowspan=2|[[静安区]]
|-
|[[宝山路駅]]
|{{lang|zh|宝山路站}}
|Baoshan Road
|align=right|2.017
|align=right|18.232
|上海軌道交通：[[ファイル:SML4.svg|10px|4|link=]] 4号線
|-
|[[東宝興路駅]]
|{{lang|zh|东宝兴路站}}
|Dongbaoxing Road
|align=right|1.073
|align=right|19.305
|&nbsp;
|align=center rowspan=5|[[虹口区]]
|-
|[[虹口足球場駅]]
|{{lang|zh|虹口足球场站}}
|Hongkou Football Stadium
|align=right|1.311
|align=right|20.616
|上海軌道交通：[[ファイル:SML8.svg|10px|8|link=]] [[上海軌道交通8号線|8号線]]
|-
|[[赤峰路駅]]
|{{lang|zh|赤峰路站}}
|Chifeng Road
|align=right|1.150
|align=right|21.766
|&nbsp;
|-
|[[大柏樹駅]]
|{{lang|zh|大柏树站}}
|Dabaishu
|align=right|0.911
|align=right|22.677
|&nbsp;
|-
|[[江湾鎮駅]]
|{{lang|zh|江湾镇站}}
|Jiangwan Town
|align=right|1.800
|align=right|24.477
|&nbsp;
|-
|[[殷高西路駅]]
|{{lang|zh|殷高西路站}}
|West Yingao Road
|align=right|1.603
|align=right|26.080
|&nbsp;
|align=center rowspan=10|[[宝山区 (上海市)|宝山区]]
|-
|[[長江南路駅]]
|{{lang|zh|长江南路站}}
|South Changjiang Road
|align=right|1.515
|align=right|27.595
|&nbsp;
|-
|[[淞発路駅]]
|{{lang|zh|淞发路站}}
|Songfa Road
|align=right|1.690
|align=right|29.285
|&nbsp;
|-
|[[張華浜駅]]
|{{lang|zh|张华浜站}}
|Zhanghuabang
|align=right|1.513
|align=right|30.798
|&nbsp;
|-
|[[淞浜路駅]]
|{{lang|zh|淞滨路站}}
|Songbin Road
|align=right|1.540
|align=right|32.338
|&nbsp;
|-
|[[水産路駅]]
|{{lang|zh|水产路站}}
|Shuichan Road
|align=right|1.241
|align=right|33.579
|&nbsp;
|-
|[[宝楊路駅]]
|{{lang|zh|宝杨路站}}
|Baoyang Road
|align=right|1.755
|align=right|35.334
|&nbsp;
|-
|[[友誼路駅 (上海市)|友誼路駅]]
|{{lang|zh|友谊路站}}
|Youyi Road
|align=right|1.029
|align=right|36.363
|&nbsp;
|-
|[[鉄力路駅]]
|{{lang|zh|铁力路站}}
|Tieli Road
|align=right|1.704
|align=right|38.067
|&nbsp;
|-
|[[江楊北路駅]]
|{{lang|zh|江杨北路站}}
|North Jiangyang Road
|align=right|2.081
|align=right|40.148
|&nbsp;
|-
|}

== 脚注 ==
{{脚注ヘルプ}}
{{reflist}}

==関連項目==
{{Commons|Category:Shmetro Line 3}}
*[[中華人民共和国の鉄道]]
*[[淞滬鉄道]]

{{上海軌道交通3号線}}
{{上海軌道交通}}
{{Rail-stub}}
{{China-stub}}
{{DEFAULTSORT:しやんはいきとうこうつう03}}
[[Category:上海軌道交通|路03]]
[[Category:中国の地下鉄路線]]
    """))
    raise 1
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