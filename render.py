#!/usr/bin/env python3
"""Original, offline, deterministic news illustration. Python 3 + Pillow only."""
from pathlib import Path
from math import sin, cos, pi
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
S = 3
W = H = 1024
PAPER = '#f6f0e2'
INK = '#1c1c22'
NAVY = '#16324f'
RED = '#b3372c'
GOLD = '#c8963e'
TEAL = '#2e7f76'
MUTED = '#5b5b60'
WHITE = '#fffdf8'
# Stable regional identity; names and numbered references duplicate every hue.
REGIONS = {'Asia-Pacific':'#2a78d6', 'Middle East':'#eb6834', 'Europe':'#1baf7a',
           'Africa':'#eda100', 'Americas':'#e87ba4', 'Global · space':'#008300'}
FONTDIR = Path('/usr/share/fonts/truetype/dejavu')
FONTS = {'sans':'DejaVuSans.ttf', 'bold':'DejaVuSans-Bold.ttf',
         'serif':'DejaVuSerif.ttf', 'display':'DejaVuSerif-Bold.ttf'}
im = Image.new('RGB', (W*S, H*S), PAPER)
d = ImageDraw.Draw(im)
fontcache = {}
checks = []

def font(size, face='sans'):
    assert size >= 10, f'Text below 10px: {size}'
    key = (size, face)
    if key not in fontcache:
        fontcache[key] = ImageFont.truetype(str(FONTDIR/FONTS[face]), round(size*S))
    return fontcache[key]

def rect(box, fill, outline=None, width=1):
    d.rectangle(tuple(round(v*S) for v in box), fill, outline, round(width*S))

def line(points, fill=INK, width=1):
    d.line([(round(x*S), round(y*S)) for x,y in points], fill=fill, width=max(1,round(width*S)))

def poly(points, fill, outline=None):
    d.polygon([(round(x*S),round(y*S)) for x,y in points], fill=fill, outline=outline)

def ellipse(box, fill, outline=None, width=1):
    d.ellipse(tuple(round(v*S) for v in box), fill, outline, round(width*S))

def measure(text, size=10, face='sans', cond=1):
    return d.textlength(text, font=font(size,face))/S*cond

def text(x,y,t,size=10,face='sans',fill=INK,cond=1,align='left',maxw=None):
    f = font(size,face)
    tw = measure(t,size,face,cond)
    if maxw is not None:
        assert tw <= maxw+.3, (t, tw, maxw)
    if align=='right': x-=tw
    elif align=='center': x-=tw/2
    if cond == 1:
        d.text((round(x*S),round(y*S)),t,font=f,fill=fill,anchor='lt')
    else:
        layer=Image.new('RGBA',(max(1,round((tw/cond+4)*S)),round((size*1.7)*S)))
        ImageDraw.Draw(layer).text((0,0),t,font=f,fill=fill,anchor='lt')
        layer=layer.resize((round(layer.width*cond),layer.height),Image.Resampling.LANCZOS)
        im.paste(layer,(round(x*S),round(y*S)),layer)
    assert x >= -.1 and x+tw <= 1024.1 and y >= 0 and y+size <= 1024, ('page',t,x,y,tw)
    return tw

def wrap(t,w,size,face='sans',cond=1):
    out=[]
    for word in t.split():
        if not out or measure(out[-1]+' '+word,size,face,cond)>w:
            out.append(word)
        else: out[-1]+=' '+word
    return out

def block(x,y,t,w,size=10,face='sans',fill=INK,leading=None,bottom=None,cond=1):
    leading=leading or size*1.22
    rows=wrap(t,w,size,face,cond)
    for i,row in enumerate(rows): text(x,y+i*leading,row,size,face,fill,cond,maxw=w)
    end=y+(len(rows)-1)*leading+size
    if bottom is not None: assert end<=bottom+.1, ('block overflow',t,end,bottom)
    checks.append((t[:45],round(end,2),bottom))
    return end

def chip(x,y,t,color,size=10):
    width=measure(t,size,'bold',.88)+10
    rect((x,y,x+width,y+15),color)
    text(x+5,y+2,t,size,'bold',WHITE,.88)
    return width

def circle_number(x,y,n,color=GOLD,r=10):
    ellipse((x-r,y-r,x+r,y+r),color,WHITE,1)
    text(x,y-5,str(n),10,'bold',INK,align='center')

def section(y,label,extra=''):
    tw=measure(label,11,'bold',.95)
    line([(18,y+6),(30,y+6)],RED)
    text(37,y,label,11,'bold',RED,.95)
    end=1006-measure(extra,10) - 10 if extra else 1006
    line([(45+tw,y+6),(end,y+6)],'#c5bba7')
    if extra: text(1006,y,extra,10,fill=MUTED,align='right')

def arrow(x1,y1,x2,y2,color,width=1):
    line([(x1,y1),(x2,y2)],color,width)
    a=__import__('math').atan2(y2-y1,x2-x1)
    poly([(x2,y2),(x2-5*cos(a-.5),y2-5*sin(a-.5)),(x2-5*cos(a+.5),y2-5*sin(a+.5))],color)

def drone(x,y,c=INK,scale=1):
    line([(x-5*scale,y),(x+5*scale,y)],c,1)
    line([(x,y-3*scale),(x,y+4*scale)],c,1)
    for dx in [-5,5]: ellipse((x+(dx-2)*scale,y-2*scale,x+(dx+2)*scale,y+2*scale),None,c,1)

def plane(x,y,scale=1,c=NAVY):
    pts=[(-48,1),(-33,-4),(-10,-5),(7,-21),(15,-21),(7,-4),(38,-3),(47,1),(37,5),(5,6),(-8,19),(-16,19),(-13,5),(-37,5)]
    poly([(x+a*scale,y+b*scale) for a,b in pts],c)

def art(n,x,y,w,h):
    # Every scene is locally composed and clipped only by explicit coordinates.
    if n==1:
        rect((x,y,x+w,y+h),'#dfe8e7')
        rect((x,y+h*.66,x+w,y+h),'#b9b9b0')
        line([(x,y+h*.83),(x+w,y+h*.83)],WHITE,1)
        poly([(x+w*.59,y+h*.7),(x+w*.72,y+h*.7),(x+w*.9,y+h),(x+w*.54,y+h)],RED)
        plane(x+w*.37,y+h*.43,1.13)
        for xx,flag in [(x+w*.78,'cn'),(x+w*.91,'us')]:
            line([(xx,y+8),(xx,y+h*.74)],NAVY)
            rect((xx,y+8,xx+19,y+21),RED)
            if flag=='cn': text(xx+3,y+9,'★',10,'sans','#f8d780')
            else:
                for yy in range(10,22,4): line([(xx,y+yy),(xx+19,y+yy)],WHITE,1)
                rect((xx,y+8,xx+8,y+15),NAVY)
        chip(x+6,y+h-18,'3-WAY TALKS · THU 19 NOV',NAVY)
    elif n==2:
        rect((x,y,x+w,y+h),NAVY)
        for xx in range(8,int(w),24):
            hh=9+((xx*17)^31)%18
            rect((x+xx,y+h-9-hh,x+xx+14,y+h-9),'#244e65')
            rect((x+xx+4,y+h-7-hh,x+xx+6,y+h-4-hh),'#e9c878')
        rect((x,y+h-8,x+w,y+h),'#376174')
        for xx,yy in [(w*.42,13),(w*.68,19),(w*.84,10)]: drone(x+xx,y+yy,WHITE,.75)
        for xx,yy in [(w*.42,13),(w*.68,19)]: line([(x+w*.2,y+h-10),(x+xx,y+yy)],'#f1bf69',1)
        ellipse((x+17,y+h-34,x+49,y+h-10),'#d0d6ce')
        rect((x+16,y+h-20,x+50,y+h-9),'#d0d6ce')
        chip(x+w-139,y+h-19,'US STRIKES QESHM',RED)
    elif n==3:
        rect((x,y,x+w,y+h),'#12273e')
        for xx in range(9,int(w)-4,17):
            yy=6+((xx*37)^127)%max(1,int(h-14))
            ellipse((x+xx,y+yy,x+xx+1,y+yy+1),'#b7c7cb')
        ellipse((x+9,y+h-31,x+52,y+h+12),'#4b9aaa')
        poly([(x+19,y+h-26),(x+37,y+h-22),(x+31,y+h-13),(x+42,y+h-8),(x+22,y+h-7)],'#88ba95')
        for k in range(10):
            xx=x+53+k*(w-113)/10; yy=y+h-20-k*(h-37)/10
            line([(xx,yy),(xx+7,yy-2)],'#b3b9b2')
        px=x+w-42; py=y+19
        ellipse((px-11,py-7,px+11,py+7),'#e4d6a6',GOLD)
        line([(px-14,py+18),(px+11,py-15)],'#eee8d8',2)
        line([(px-15,py+6),(px+22,py+22)],GOLD,2)
        rect((px+9,py+15,px+18,py+23),GOLD)
        text(x+59,y+7,'1 LIGHT-DAY — 25.9 billion km',10,'bold',WHITE,.83)
        chip(x+66,y+h-18,'10:16 UTC · NOV 18',TEAL)
    elif n==4:
        rect((x,y,x+w,y+h),NAVY)
        poly([(x+22,y+5),(x+62,y+2),(x+78,y+14),(x+65,y+25),(x+33,y+25),(x+12,y+17)],'#42697c')
        for dy in [7,17,25]: arrow(x+4,y+dy,x+55,y+dy+2,'#ecb36c')
        text(x+w-5,y+4,'141 FIRED',11,'bold',WHITE,align='right')
        text(x+w-5,y+19,'126 DOWNED',10,'bold','#b9ddcb',align='right')
    elif n==5:
        rect((x,y,x+w,y+h),'#e5ece5')
        poly([(x+7,y+10),(x+38,y+1),(x+69,y+10)],NAVY)
        for xx in range(14,68,12): rect((x+xx,y+12,x+xx+4,y+27),NAVY)
        line([(x+7,y+30),(x+71,y+30)],NAVY,2)
        arrow(x+81,y+26,x+98,y+6,TEAL,3)
        text(x+w-5,y+3,'MORE HIKES',10,'bold',NAVY,align='right')
        text(x+w-5,y+19,'DOW −1.1%',10,'bold',RED,align='right')
    elif n==6:
        rect((x,y,x+w,y+h),'#e2edef')
        poly([(x+5,y),(x+34,y),(x+53,y+13),(x+33,y+31),(x+5,y+31)],'#b7c3a9')
        pts=[]
        for k in range(100):
            a=k*.16; r=11*(1-k/110)
            pts.append((x+64+r*cos(a),y+16+r*sin(a)))
        line(pts,NAVY,2)
        arrow(x+70,y+22,x+44,y+7,RED,1)
        text(x+w-5,y+5,'LANDFALL',10,'bold',RED,align='right')
        text(x+w-5,y+20,'20 NOV',10,'bold',NAVY,align='right')
    elif n==7:
        rect((x,y,x+w,y+h),'#efe5d2')
        # One magnitude, labelled explicitly: no invented strike-by-strike data.
        line([(x+8,y+29),(x+81,y+29)],MUTED)
        rect((x+13,y+23,x+32,y+28),GOLD)
        rect((x+40,y+5,x+59,y+28),GOLD)
        text(x+68,y+3,'9 STRIKES',10,'bold')
        text(x+68,y+19,'37 KILLED',10,'bold')
        drone(x+w-17,y+10,RED,.8)
    elif n==8:
        rect((x,y,x+w,y+h),'#e5e9ef')
        rect((x+5,y+2,x+58,y+30),'#254b87')
        for k in range(12):
            a=k*pi/6
            ellipse((x+30+10*cos(a),y+15+10*sin(a),x+32+10*cos(a),y+17+10*sin(a)),GOLD)
        text(x+68,y+3,'€45bn',19,'bold',NAVY)
        text(x+w-5,y+20,'FOR 2027',10,'bold',NAVY,align='right')
    elif n==9:
        rect((x,y,x+w,y+h),'#e9eee8')
        # Zero-baseline columns. Heights preserve 3.5 : 3.6 exactly.
        line([(x+9,y+29),(x+w-9,y+29)],'#aab4aa')
        rect((x+12,y+29-3.5*5,x+36,y+29),TEAL)
        rect((x+108,y+29-3.6*5,x+132,y+29),TEAL)
        text(x+42,y+4,'SEP',10,'bold')
        text(x+42,y+19,'3.5%',10,'bold')
        text(x+138,y+4,'OCT',10,'bold')
        text(x+138,y+19,'3.6%',10,'bold')
    elif n==10:
        rect((x,y,x+w,y+h),'#e9e0c9')
        rect((x,y,x+43,y+h),'#a8c9d1')
        text(x+4,y+11,'SEA',10,'bold',NAVY)
        line([(x+w-28,y),(x+w-28,y+h)],GOLD,2)
        text(x+50,y+2,'NUSEIRAT',10,'bold')
        text(x+w-5,y+21,'YELLOW LINE',10,'bold',NAVY,align='right')
        arrow(x+w-11,y+12,x+116,y+12,RED,2)
        rect((x+111,y+8,x+124,y+14),NAVY)
    elif n==11:
        rect((x,y,x+w,y+h),'#e3ece2')
        rect((x+7,y+10,x+35,y+30),NAVY)
        line([(x+13,y+13),(x+29,y+13)],WHITE,1)
        poly([(x+15,y+2),(x+30,y+5),(x+26,y+15),(x+12,y+11)],WHITE,NAVY)
        # Exactly 251 green dots and 11 contrasting outlined dots, one per vote.
        for k in range(262):
            xx=x+43+(k%66)*2.45; yy=y+2+(k//66)*3
            ellipse((xx,yy,xx+1.4,yy+1.4),TEAL if k<251 else RED)
        text(x+45,y+20,'251–11 CAUCUS VOTE',10,'bold',NAVY)

# Coordinate-hash grain, independent of any RNG, clock or machine state.
pix=im.load()
for yy in range(1024):
    for xx in range(1024):
        v=((xx*7349+yy*9241)^(xx*yy))%41
        if v<5:
            delta=v-3
            color=(246+delta,240+delta,226+delta)
            for sy in range(S):
                for sx in range(S): pix[xx*S+sx,yy*S+sy]=color

# Masthead: every label belongs to 18 November, with explicit future references.
rect((18,10,1006,13),GOLD)
rect((18,20,93,77),RED)
text(55.5,23,'NOV',11,'bold',WHITE,align='center')
text(55.5,34,'18',29,'display',WHITE,align='center')
text(55.5,65,'WED · 2026',10,'bold',WHITE,.82,align='center')
line([(106,22),(792,22)],NAVY)
line([(106,25),(792,25)],NAVY)
text(449,32,'THE DAY IN WORLD NEWS',29,'display',NAVY,.94,align='center')
line([(106,65),(792,65)],NAVY)
line([(106,68),(792,68)],NAVY)
rect((806,20,1006,77),NAVY)
text(906,25,'40 STORIES',18,'bold',WHITE,align='center')
text(906,48,'6 CONTINENTS · ONE PAGE',10,'bold',WHITE,.94,align='center')
text(449,72,'Everything on this page happened, or was first reported, on Wednesday 18 November 2026.',11,'serif',MUTED,.89,align='center')

HEROES=[
(1,'ASIA · SUMMIT','Asia-Pacific','AP · CNN',"Xi welcomes Trump at Shenzhen’s airport", "A rare honour from China’s leader. Trump and Putin shake hands at the APEC banquet; their three-way talks with Xi are on Thursday, 19 Nov."),
(2,'MIDDLE EAST · IRAN WAR','Middle East','REUTERS · AL JAZEERA',"Bahrain and Kuwait intercept Iran’s drones", "Iran says it aimed at a US radar in Bahrain and Patriot batteries in Kuwait after a US strike on Qeshm. CENTCOM reports no damage."),
(3,'SPACE · SCIENCE','Global · space','NASA',"Voyager 1 reaches one light-day from Earth", "NASA’s probe is the first craft to get 25.9 billion km away, a record for any human-made object: a command sent today arrives tomorrow.")]
for i,(n,tag,region,source,headline,body) in enumerate(HEROES):
    x=18+i*333; y=92; w=322; bottom=302
    rect((x+2,y+3,x+w+2,bottom+3),'#d3cab9')
    rect((x,y,x+w,bottom),WHITE,INK)
    circle_number(x+17,y+15,n)
    chip(x+32,y+7,tag,REGIONS[region])
    text(x+w-9,y+27,source,11,'bold',MUTED,.88,align='right')
    block(x+10,y+42,headline,w-20,19,'display',leading=21,bottom=y+85)
    art(n,x+10,y+90,w-20,61)
    block(x+10,y+159,body,w-20,12,leading=13.2,bottom=bottom-7)

section(313,'EIGHT MORE STORIES TO KNOW','04—11 / THE BRIEFING')
MEDIUM=[
(4,'EUROPE · UKRAINE WAR','Europe','AIR FORCE','Russia fires 141 drones at Ukraine; 126 downed','Hits at seven sites overnight; attacks kill four in the Odesa region, its governor says.'),
(5,'AMERICAS · MARKETS','Americas','FED · AP','Fed minutes: officials see more hikes','A couple face a bigger December rise; the Dow falls 1.1%, the Nasdaq gains.'),
(6,'ASIA · WEATHER','Asia-Pacific','IMD','Cyclone Akvan veers north toward Odisha','Landfall due between Puri and Narsapur on 20 Nov; evacuations begin.'),
(7,'AFRICA · SUDAN WAR','Africa','AMNESTY','Amnesty: RSF drones killed 37 in El Obeid','It urges a war-crimes inquiry; the RSF blames Sudan’s army for the deaths.'),
(8,'EUROPE · UKRAINE AID','Europe','EU','EU proposes a €45bn loan to fund Ukraine in 2027','Two-thirds of a €70bn gap, repaid only once Russia pays reparations.'),
(9,'EUROPE · ECONOMY','Europe','ONS','UK inflation climbs to 3.6%, one-year high','Fuel prices and an earlier tobacco tax rise pushed October CPI up from 3.5%.'),
(10,'MIDDLE EAST · GAZA','Middle East','REUTERS','Israeli tanks roll into central Gaza near Nuseirat','The army says it is destroying a tunnel; three are killed, hospitals say.'),
(11,'AMERICAS · US POLITICS','Americas','NPR · CBS','Jeffries wins Democrats’ nod for House Speaker','A 251-11 caucus vote puts him on course to be the first Black Speaker in 2027.')]
for i,(n,tag,region,source,headline,body) in enumerate(MEDIUM):
    x=18+(i%4)*250; y=332+(i//4)*124; w=238
    rect((x,y,x+w,y+124),WHITE,'#a9a295')
    circle_number(x+13,y+12,n,REGIONS[region],9)
    chip(x+25,y+5,tag,REGIONS[region])
    text(x+w-7,y+23,source,11,'bold',MUTED,.85,align='right')
    block(x+7,y+35,headline,w-14,13,'bold',leading=14,bottom=y+63,cond=.91)
    art(n,x+7,y+66,w-14,32)
    # Body occupies its own two-line strip below the illustration, in the gutter.
    block(x+7,y+102,body,w-14,11,leading=12,bottom=y+125,cond=.92)

# Dot-matrix atlas, intentionally diagrammatic; pins use the list's story IDs.
section(584,'WHERE IT HAPPENED','NUMBERED PINS REFER TO THE STORIES')
rect((18,601,1006,705),'#ede9dc', '#c0b7a4')
MX,MY,MW,MH=30,606,590,77
continents=[
[(-168,70),(-145,72),(-128,61),(-111,54),(-93,53),(-62,59),(-53,47),(-76,25),(-89,16),(-105,23),(-119,39),(-139,57)],
[(-75,11),(-52,5),(-35,-8),(-46,-25),(-67,-55),(-77,-15)],
[(-53,82),(-22,72),(-40,59),(-57,63)],
[(-11,36),(-8,59),(20,71),(53,66),(84,76),(130,60),(177,64),(158,47),(137,35),(122,18),(107,1),(97,12),(77,8),(65,25),(44,13),(34,31)],
[(-17,35),(11,37),(36,29),(51,12),(38,-13),(20,-35),(9,-30),(-2,-4),(-16,14)],
[(112,-12),(139,-11),(154,-27),(145,-40),(116,-33)],
[(47,-13),(51,-16),(48,-26),(44,-24)],
[(128,31),(142,44),(145,43),(136,32)],
[(166,-34),(178,-40),(172,-47),(165,-45)]]
def inside(x,y,polypts):
    hit=False
    j=len(polypts)-1
    for i in range(len(polypts)):
        xi,yi=polypts[i]; xj,yj=polypts[j]
        if (yi>y)!=(yj>y) and x<(xj-xi)*(y-yi)/(yj-yi)+xi: hit=not hit
        j=i
    return hit

def mapxy(lon,lat): return MX+(lon+180)/360*MW, MY+(83-lat)/143*MH
for lat in range(-55,84,7):
    for lon in range(-178,179,4):
        if any(inside(lon,lat,p) for p in continents):
            px,py=mapxy(lon,lat); ellipse((px,py,px+1.8,py+1.8),'#a7aaa0')
# Geographic anchors plus carefully separated labels; leader lines preserve accuracy.
pins=[(1,114,23,'Asia-Pacific',26,0),(2,50,26,'Middle East',13,13),(4,31,49,'Europe',9,-19),
      (5,-74,41,'Americas',-22,-13),(6,86,18,'Asia-Pacific',15,15),(7,30,13,'Africa',-17,16),
      (8,4,51,'Europe',0,-11),(9,-1,52,'Europe',-21,-23),(10,35,32,'Middle East',-12,-1),
      (11,-77,39,'Americas',2,11),(12,121,14,'Asia-Pacific',35,16),(13,-76,45,'Americas',-42,-26),
      (14,133,36,'Asia-Pacific',32,-12),(17,38,56,'Europe',30,-23),(19,44,33,'Middle East',32,-5),
      (23,28,-26,'Africa',8,10)]
pin_labels={1:(488,633),2:(429,663),4:(368,613),5:(182,621),6:(470,671),
            7:(367,679),8:(341,613),9:(315,613),10:(384,649),11:(201,650),
            12:(547,664),13:(154,611),14:(559,631),17:(400,613),19:(407,642),23:(389,674)}
for n,lon,lat,region,dx,dy in pins:
    px,py=mapxy(lon,lat); cx,cy=pin_labels[n]
    line([(px,py),(cx,cy)],MUTED,.7)
    circle_number(cx,cy,n,REGIONS[region],8)
arrow(563,610,629,610,NAVY)
circle_number(606,610,3,REGIONS['Global · space'],8)
text(563,625,'to Voyager 1',10,'bold',NAVY)
# Legend is printed beside the atlas, in matching order with names.
for i,(name,color) in enumerate(REGIONS.items()):
    col=i%2; row=i//2
    xx=661+col*172; yy=610+row*18
    ellipse((xx,yy+2,xx+7,yy+9),color)
    text(xx+13,yy,name,10,'bold',NAVY)
line([(648,669),(991,669)],'#c4baa7')
text(659,677,'$3,792',15,'display',NAVY)
text(738,677,'Gold an ounce; lowest in over a year',10,fill=MUTED,cond=.87)
text(32,688,'25.9bn km — Voyager 1 from Earth: one light-day',10,'bold',NAVY)

section(715,'ALSO ON WEDNESDAY 18 NOVEMBER','12—40 / AROUND THE WORLD')
BRIEFS=[
(12,'Manila','Trump hails "biggest" trade deal','Asia-Pacific'),
(13,'Ottawa','Carney, Xi agree tariff relief','Americas'),
(14,'Japan','Jets scramble after Russian incursion','Asia-Pacific'),
(15,'Washington','Rubio: no evidence outages linked','Americas'),
(16,'Kyiv aid','Canada $108M; DE €11.6bn; UK missiles','Europe'),
(17,'Moscow','Russia, China hail closer military ties','Europe'),
(18,'Russia','Strikes cut refining 45%; 15 of 35 hit','Europe'),
(19,'Iraq','Oil to Turkey resumes after 12 years','Middle East'),
(20,'US','Trump weighs dirty-bomb report','Americas'),
(21,'Tehran','Army vows response; 3rd carrier joins','Middle East'),
(22,'Bahrain','Shia clerics get life for Iran plot','Middle East'),
(23,'Pretoria','Nigeria envoy summoned over remarks','Africa'),
(24,'Bangladesh','Tear gas at wage protests','Asia-Pacific'),
(25,'Khartoum','War trauma drives drug addiction','Africa'),
(26,'Frankfurt','Deutsche Bank probed over leak','Europe'),
(27,'Brussels','ECB likens AI boom to dotcom bubble','Europe'),
(28,'Mexico','Sheinbaum asks Xi for panda mate','Americas'),
(29,'Silicon Valley','Russian spy suspect arrested','Americas'),
(30,'Caracas','US defence chief makes surprise visit','Americas'),
(31,'San Salvador','Bukele confirms gang-mansion strike','Americas'),
(32,'California','Waymo pulls robotaxis off highways','Americas'),
(33,'Portugal','Bruna, Charles set rain records','Europe'),
(34,'Baghdad','French IS members jailed for life','Middle East'),
(35,'Madrid','Iglesias, 83, ordered to testify','Europe'),
(36,'New York','Trump to give sworn BBC testimony','Americas'),
(37,'Brussels','EU auditors: chemicals rules fail','Europe'),
(38,'New Delhi','Modi back from ASEAN; trade push on','Asia-Pacific'),
(39,'Astana','Middle Corridor targets 30M tonnes','Asia-Pacific'),
(40,'Tokyo','GTA VI billboards up; out tomorrow','Asia-Pacific')]
for i,(n,place,story,region) in enumerate(BRIEFS):
    col,row = (0,i) if i<15 else (1,i-15)
    x=18+col*502; y=734+row*13.0
    if row%2==0: rect((x,y-1,x+318,y+12.2),WHITE)
    circle_number(x+9,y+6,n,REGIONS[region],6.3)
    tx=x+21
    cond=.86
    label=place+': '
    ww=text(tx,y,label,11.5,'bold',INK,cond)
    text(tx+ww,y,story,11.5,'sans',INK,cond,maxw=486-21-ww)
line([(512,734),(512,920)],'#c5bba7')
text(764,913,'40 stories. One extraordinary Wednesday.',12,'serif',RED,align='center')

# Day in numbers: fixed tiles, no implied comparative scale.
rect((18,929,1006,969),NAVY)
statitems=[('141/126','drones fired / downed · Ukraine'),('€45bn','EU loan proposed · Ukraine 2027'),('37','killed · RSF drones in El Obeid'),('251–11','House Democrats’ speaker vote'),('45%','Russia’s refining disrupted')]
for i,(value,label) in enumerate(statitems):
    x=28+i*197
    if i: line([(x-9,936),(x-9,962)],'#577084')
    text(x,933,value,23,'bold',WHITE)
    text(x,958,label,10,'sans','#e8e4d6',.85,maxw=187)

rect((18,975,1006,1004),'#efdbd4')
datecheck="DATE CHECK — Left out as earlier-day news: Nvidia's Q3 results · Kerch Bridge collapse · Knesset speaker vote · NSA outage · Mongolia's president's offer to quit (all Tuesday or before)"
# Faux oblique is a geometric shear of real font glyphs, never generated lettering.
rows=wrap(datecheck,970,10,'serif',.91)
assert 1 <= len(rows) <= 2, rows
for i,row in enumerate(rows):
    layer=Image.new('RGBA',(2930,39))
    ImageDraw.Draw(layer).text((4,0),row,font=font(10,'serif'),fill=RED,anchor='lt')
    layer=layer.transform(layer.size,Image.Transform.AFFINE,(1,-.12,3,0,1,0),Image.Resampling.BICUBIC)
    layer=layer.resize((round(layer.width*.91),layer.height),Image.Resampling.LANCZOS)
    im.paste(layer,(25*S,round((979+i*11)*S)),layer)
footer="All 40 stories happened, or were first reported, on Wednesday 18 November 2026 · Original drawings"
text(512,998,footer,10,'sans',MUTED,.9,align='center')
text(512,1020-6,'Sources: AP · Reuters · AFP · CNN · CNBC · NPR · Fed · ONS · IMD · NASA · Amnesty · EU',10,'sans',MUTED,.9,align='center')

im=im.resize((1024,1024),Image.Resampling.LANCZOS)
im.save(ROOT/'entry.png',format='PNG',optimize=True,compress_level=9)
print(f'Rendered entry.png: {im.width}×{im.height}, {im.mode}; {len(checks)} text blocks checked; {(ROOT/"entry.png").stat().st_size:,} bytes')
