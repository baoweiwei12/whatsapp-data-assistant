import json
from app.chatgpt.client import analyze_text
from app.chatgpt.tokens import num_tokens_from_messages

text = """126505 Sundust N2 Both Tags Non adj $396,000

226570 Black N2 Both Tags Most Sticker Non adj $81,500

279174 Grey JUB N1 Green Tag adj $65,500

279174 Grey JUB N1 Both Tags Non adj $66,000

279174 Silver Roma N1 Green Tag adj $65,500

126333 Wimbledon JUB N2 Both Tags Non adj $121,000

126331 Sundust  OYS N11 Both Tags Non adj $105,000

278273 VI  Grey OYS N2 Both Tags Non adj $97,000

278273NG Black OYS N2 Both Tags Non adj $108,000

279383RBR G Silver JUB N12 Both Tags Non adj $125,000

126333 Black JUB 30/1/2024 Both Tags FullSticker Non adj $120,000

126333G Black JUB 29/1/2024 Both Tags Non adj $141,000

116500 White N2 2024 Both Tags Non adj $245,000

277200 Blue N2 Both Tags Non adj $51,500

278240 Pink OYS N2 Both Tags Non adj $62,000

124300 Black N2 Both Tags Non adj $56,500

279173G Champ JUB N2 Both Tags Non adj $98,000

278582-3005 warranty 2023 August $56,000-46%

Q3288560 May2023 card $58,000 -33%

W326802 Open Date $44,500-38%

79360N-0001 N12 adj $31,000
79363N-0001 N12 adj $40,000
25407N-0001 N11 Non adj $26,000

Rolex HK Ready Stock 
Can Deal Monday To Sunday 
店內現貨星期一至星期日都可交易
126710BLNR JUB N2 Both Tags Non adj $126,000

224270 N2 Both Tags Non adj $66,500

124300 Silver N2 Both Tags Non adj $58,000

126000 Silver N2 Both Tags Non adj $56,000

126200 Green OYS N2 Full Sticker Both Tags Non adj $66,500

126300 Wimbledon OYS N2 Full Sticker Both Tags Non adj $74,500

126621 Cho N2 Both Tags Non adj $137,500

277200 Green N2 Both Full Sticker Tags Non adj $55,000

279171G Purple JUB N2 Both Tags adj $109,000

116509 Blue (NOS)N11 2021 Both Tags Non adj $356,000

116508PN N7 Both Tags Full Sticker Non adj $375,000

116500 White (NOS)N11 2021 Green Tag adj $240,000

116503 Black (NOS)Feb 2017Card
Full Sticker Both Tags adj $156,000

326238 Champ Both Tags N7  Non adj $260,000

126333G Champ JUB N2 Both Tags Non adj $140,000

124200 Black N2 Both Tags adj $52,000

278273 Champ Index JUB N1 Both Tags Non adj $100,000

279173G G17 Champ N1 Both Tags adj $111,000

Cartier
WSTA0074 N12 $36,600 -23%
WRSN0032 March 2023 $36,200 -27%

Omega HK Ready Stock 
311.92.44.30.01.001 $84,600 -8%
424.13.40.21.01.002 $38,400 -36%
424.10.33.20.53.001 $33,700 -37%
210.92.42.20.01.001 $70,200 -25%
434.10.30.60.02.001 $23,400 -35%
434.10.40.20.03.001 $38,700-36%

Chopard HK Ready Stock
278582-3005 warranty 2023 August $56,000-40%

JLC HK Ready Stock
Q3288560 May2023 card $58,000 -28%

Zenith HK Ready Stock
03.9300.3620/51.I001 $70,500 -42%

Breitling HK Ready Stock
A17376A31L1S1  Sep2023 card $38300 -38%

Blancpain HK Ready Stock
6104-1127-95A $84,000 -49%

Hublot HK Ready Stock

Tudor HK Ready Stock
79030N-0001 N1 adj $24,000
79360N-0001 N12 adj $33,000
79363N-0001 N12 adj $43,000
25407N-0001 N11 Non adj $28,000
25807KN-0001 2024 N1 $35,000

2Days arrive 兩天到貨
298601-3004 $121,000 -40%

DBEX1007 Limited Edition 2023card 28PCS $520,000 -27%

1Days Arrive 1天到

2Days Arrive 2天到
126610LV N2 Both Tags Non adj $119,000

Used Ready Stock
5153G-0001 2013 warrenty $168,000

116000 Champ No white Tag Warranty Card 2017 $49,500

116244 Rhodium Floral Motif Both Tag Warranty Card 2014 $77,800

126284 VIIX Grey Both Tag Warranty Card 2018 $138,000
"""
responese_content = analyze_text(text)
print(responese_content.model_dump())
