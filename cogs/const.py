import discord
import asyncio
import re


punch_list = ['https://media.giphy.com/media/1n753Z1ZeGdkwxtYHo/giphy.gif',
		       'https://media.giphy.com/media/WgN70xgCycyg2ZC5G6/giphy.gif',
		       'https://media.giphy.com/media/orU5Hg8KwR430W7GIs/giphy.gif',
		       'https://media.giphy.com/media/PiieOBhf5ymvOVxnzm/giphy.gif',
		       'https://media.giphy.com/media/Xpj8gSHOCxONPz19AV/giphy.gif',
		       'https://media.giphy.com/media/YxwAwiJEqEoFi/giphy.gif']

drink_list = ['https://media.giphy.com/media/1xlqPePKvCM3xVkWet/giphy.gif',
		      'https://media.giphy.com/media/9rlYebzurMAXNaBGUO/giphy.gif',
		      'https://media.giphy.com/media/1zlE7BBo7BuwpKfA4Z/giphy.gif',
		      'https://media.giphy.com/media/nKMYwijvNrRwQJtq6W/giphy.gif',
		      'https://media.giphy.com/media/eeLJdyAGPjnChKSlhu/giphy.gif',
		      'https://media.giphy.com/media/55ma8eHi4YPCz6IZZO/giphy.gif',
		      'https://media.giphy.com/media/NSqNZRkKShyKtedi0c/giphy.gif',
		      'https://media.giphy.com/media/1BfhcYJtmPsM81JaRR/giphy.gif']

sex_list = ['https://media.giphy.com/media/35FN4lauHp6Rp8Hmbe/giphy.gif',
			'https://media.giphy.com/media/oHwzR1oBPH01N5dGb3/giphy.gif',
			'https://media.giphy.com/media/l9VRIWKUKoE1CVifCc/giphy.gif',
			'https://media.giphy.com/media/1wnYxMQDL1EaMkmvX8/giphy.gif',
			'https://media.giphy.com/media/13b21X2VrjoH2eEvTp/giphy.gif',
			'https://media.giphy.com/media/RcS3c2vgzuOvGlk2Ms/giphy.gif']

hug_list = [
"https://media.giphy.com/media/EvYHHSntaIl5m/giphy.gif",
"https://media.giphy.com/media/lXiRKBj0SAA0EWvbG/giphy.gif",
"https://media.giphy.com/media/xT0Gqne4C3IxaBcOdy/giphy.gif",
"https://media.giphy.com/media/gnXG2hODaCOru/giphy.gif",
"https://media.giphy.com/media/VGACXbkf0AeGs/giphy.gif",
"https://media.giphy.com/media/l378uBCYt1vfaj2aA/giphy.gif",
"https://media.giphy.com/media/26FeTvBUZErLbTonS/giphy.gif",
"https://media.giphy.com/media/l4FGy5UyZ1KnVZ7BC/giphy.gif",
"https://media.giphy.com/media/3oz8xt8ebVWCWujyZG/giphy.gif",
"https://media.giphy.com/media/l0HlOvJ7yaacpuSas/giphy.gif",
"https://media.giphy.com/media/3otPozEs14AOGrdcOI/giphy.gif",
#"https://media.giphy.com/media/DjoWze0Patl1m/giphy.gif",
"https://media.giphy.com/media/3o6Mb7KaEIURtCKAbS/giphy.gif",
"https://media.giphy.com/media/w09VX7IEsoX6w/giphy.gif",
"https://media.giphy.com/media/vL1meInBzYCgo/giphy.gif",
"https://media.giphy.com/media/oVr48mIz8l5XG/giphy.gif",
"https://media.giphy.com/media/mmPgxbuPiwCQg/giphy.gif",
"https://media.giphy.com/media/3EJsCqoEiq6n6/giphy.gif",
"https://media.giphy.com/media/Ilkurs1e3hP0c/giphy.gif",
"https://media.giphy.com/media/jOoxG4mWGuH9S/giphy.gif",
"https://media.giphy.com/media/3orif2vpZbXi8P0fPW/giphy.gif",
"https://media.giphy.com/media/l4KhMHSclwbAGzGeI/giphy.gif",
"https://media.giphy.com/media/13fQ3RrUjteykw/giphy.gif",
"https://media.giphy.com/media/3ornk7CaGmo2uuxiJW/giphy.gif",
"https://media.giphy.com/media/xT1XGNlkcBDSqkCRqg/giphy.gif",
"https://media.giphy.com/media/l2JJySFVazmR38Lks/giphy.gif",
"https://media.giphy.com/media/3o7WTDVMidWRDzP9ss/giphy.gif",
"https://media.giphy.com/media/mLYVrZR44EcU0/giphy.gif",
"https://media.giphy.com/media/13YrHUvPzUUmkM/giphy.gif",
"https://media.giphy.com/media/du8yT5dStTeMg/giphy.gif",
"https://media.giphy.com/media/BXrwTdoho6hkQ/giphy.gif",
"https://media.giphy.com/media/qscdhWs5o3yb6/giphy.gif",
"https://media.giphy.com/media/xJlOdEYy0r7ZS/giphy.gif",
"https://media.giphy.com/media/od5H3PmEG5EVq/giphy.gif",
"https://media.giphy.com/media/svXXBgduBsJ1u/giphy.gif",
"https://media.giphy.com/media/wnsgren9NtITS/giphy.gif",
"https://media.giphy.com/media/NZ8dp5kWRbM4g/giphy.gif",
"https://media.giphy.com/media/kFTKQfjK4ysZq/giphy.gif",
"https://media.giphy.com/media/49mdjsMrH7oze/giphy.gif",
"https://media.giphy.com/media/aD1fI3UUWC4/giphy.gif",
"https://media.giphy.com/media/5eyhBKLvYhafu/giphy.gif",
"https://media.giphy.com/media/ddGxYkb7Fp2QRuTTGO/giphy.gif",
"https://media.giphy.com/media/l2QDM9Jnim1YVILXa/giphy.gif",
"https://media.giphy.com/media/ZRI1k4BNvKX1S/giphy.gif",
"https://media.giphy.com/media/s31WaGPAmTP1e/giphy.gif",
"https://media.giphy.com/media/wSY4wcrHnB0CA/giphy.gif",
"https://media.giphy.com/media/C4gbG94zAjyYE/giphy.gif",
"https://media.giphy.com/media/kvKFM3UWg2P04/giphy.gif",
"https://media.giphy.com/media/rSNAVVANV5XhK/giphy.gif",
"https://media.giphy.com/media/HaC1WdpkL3W00/giphy.gif",
"https://media.giphy.com/media/eMpDBxxTzKety/giphy.gif",
"https://media.giphy.com/media/DjczAlIcyK1Co/giphy.gif",
"https://media.giphy.com/media/yziFo5qYAOgY8/giphy.gif",
"https://media.giphy.com/media/iMrHFdDEoxT5S/giphy.gif",
"https://media.giphy.com/media/NZ8dp5kWRbM4g/giphy.gif",
"https://media.giphy.com/media/fFC10O3zlGfe/giphy.gif",
"https://media.giphy.com/media/aD1fI3UUWC4/giphy.gif",
"https://media.giphy.com/media/ZQN9jsRWp1M76/giphy.gif",
"https://media.giphy.com/media/TdXxcoNvHDVu0/giphy.gif",
"https://media.giphy.com/media/oTiuuAuYb22KQ/giphy.gif",
"https://media.giphy.com/media/11WhdeCxSM5lyo/giphy.gif",
"https://media.giphy.com/media/DjczAlIcyK1Co/giphy.gif"
]

sex_list = ['https://discord.band/gif/1.gif',
			'https://discord.band/gif/2.gif',
			'https://discord.band/gif/3.gif',
			'https://discord.band/gif/5.gif',
			'https://discord.band/gif/6.gif']

kiss_list = [
#"https://media.giphy.com/media/KMuPz4KDkJuBq/giphy.gif",
"https://media.giphy.com/media/PFjXmKuwQsS9q/giphy.gif",
"https://media.giphy.com/media/3o7qDVQ2GrFAf1MVgc/giphy.gif",
"https://media.giphy.com/media/bCY7hoYdXmD4c/giphy.gif",
"https://media.giphy.com/media/HKQZgx0FAipPO/giphy.gif",
"https://media.giphy.com/media/l2Je2M4Nfrit0L7sQ/giphy.gif",
"https://media.giphy.com/media/3o6ozHbQHZzDTxRjsA/giphy.gif",
"https://media.giphy.com/media/3og0IvIXD1UrcEvNmw/giphy.gif",
"https://media.giphy.com/media/l0HU2EeywKGaMJCY8/giphy.gif",
"https://media.giphy.com/media/HN4Om0tu8y7gk/giphy.gif",
"https://media.giphy.com/media/3o7TKzkCiuW3E0Gn4Y/giphy.gif",
#"https://media.giphy.com/media/l0MYLr8Qh3opXBSSI/giphy.gif",
"https://media.giphy.com/media/26ufmeUh9YOVS53Xi/giphy.gif",
"https://media.giphy.com/media/26tnbo7HDeYacLQK4/giphy.gif",
"https://media.giphy.com/media/l0MYEw4RMBirPQhHy/giphy.gif",
"https://media.giphy.com/media/xThtaig5DpJpA1wuOs/giphy.gif",
"https://media.giphy.com/media/4GLJbNy3DdXPi/giphy.gif",
"https://media.giphy.com/media/2stFpADPSpfQQ/giphy.gif",
"https://media.giphy.com/media/3oAt2gl4VpnHiDW7hC/giphy.gif",
"https://media.giphy.com/media/KH1CTZtw1iP3W/giphy.gif",
"https://media.giphy.com/media/l0ErEXpCoUcS15UNq/giphy.gif",
#"https://media.giphy.com/media/1041PhUHlC0tJC/giphy.gif",
"https://media.giphy.com/media/3o6ZsXco9ACON6dSjS/giphy.gif",
"https://media.giphy.com/media/3oz8xIZrAhijabg69a/giphy.gif",
"https://media.giphy.com/media/7JaFQzMXdw759xdvpk/giphy.gif",
"https://media.giphy.com/media/3o6gDXMurw9nM2vLR6/giphy.gif",
"https://media.giphy.com/media/CzCi6itPr3yBa/giphy.gif",
"https://media.giphy.com/media/mGAzm47irxEpG/giphy.gif",
"https://media.giphy.com/media/hnNyVPIXgLdle/giphy.gif",
"https://media.giphy.com/media/f5vXCvhSJsZxu/giphy.gif",
"https://media.giphy.com/media/ZRSGWtBJG4Tza/giphy.gif",
"https://media.giphy.com/media/11k3oaUjSlFR4I/giphy.gif",
"https://media.giphy.com/media/JynbO9pnGxPrO/giphy.gif",
"https://media.giphy.com/media/nyGFcsP0kAobm/giphy.gif",
"https://media.giphy.com/media/4MBsFo1nSCfOo/giphy.gif",
#"https://media.giphy.com/media/Ch5UXfXJ3xbNK/giphy.gif",
"https://media.giphy.com/media/BaEE3QOfm2rf2/giphy.gif",
"https://media.giphy.com/media/uSHX6qYv1M7pC/giphy.gif",
"https://media.giphy.com/media/FqBTvSNjNzeZG/giphy.gif",
"https://media.giphy.com/media/EP9YxsbmbplIs/giphy.gif",
"https://media.giphy.com/media/OSq9souL3j5zW/giphy.gif",
"https://media.giphy.com/media/sS7Jac8n7L3Ve/giphy.gif",
"https://media.giphy.com/media/9P8t4wusRUdSE/giphy.gif",
"https://media.giphy.com/media/EVODaJHSXZGta/giphy.gif",
"https://media.giphy.com/media/wOtkVwroA6yzK/giphy.gif",
"https://media.giphy.com/media/fHtb1JPbfph72/giphy.gif",
#"https://media.giphy.com/media/A5FtN4L0Yp2dq/giphy.gif",
"https://media.giphy.com/media/pwZ2TLSTouCQw/giphy.gif",
"https://media.giphy.com/media/K4VEsbuHfcj6g/giphy.gif",
"https://media.giphy.com/media/HWIe1Vrs6QxFe/giphy.gif",
"https://media.giphy.com/media/tJmYMnwlvRxdK/giphy.gif",
"https://media.giphy.com/media/rSBJ7muTr25ry/giphy.gif",
"https://media.giphy.com/media/wHbQ7IMBrgTzq/giphy.gif",
"https://media.giphy.com/media/EPQDbdvqne1rM6hel8/giphy.gif",
"https://media.giphy.com/media/JFmIDQodMScJW/giphy.gif",
"https://media.giphy.com/media/ll5leTSPh4ocE/giphy.gif",
"https://media.giphy.com/media/Y9iiZdUaNRF2U/giphy.gif",
"https://media.giphy.com/media/jR22gdcPiOLaE/giphy.gif",
"https://media.giphy.com/media/CTo4IKRN4l4SA/giphy.gif",
"https://media.giphy.com/media/CRSuLR6rhDdT2/giphy.gif",
#"https://media.giphy.com/media/r1FBFMAOo8Mhy/giphy.gif",
"https://media.giphy.com/media/kU586ictpGb0Q/giphy.gif",
"https://media.giphy.com/media/bm2O3nXTcKJeU/giphy.gif",
"https://media.giphy.com/media/Ka2NAhphLdqXC/giphy.gif",
"https://media.giphy.com/media/dP8ONh1mN8YWQ/giphy.gif",
"https://media.giphy.com/media/L3rumss7XR4QM/giphy.gif",
"https://media.giphy.com/media/IdzovcoOUoUM0/giphy.gif",
"https://media.giphy.com/media/10r6oEoT6dk7E4/giphy.gif",
#"https://media.giphy.com/media/1VBRxFrg0hZ9C/giphy.gif",
#"https://media.giphy.com/media/Q1TXCgzvfLNbW/giphy.gif",
"https://media.giphy.com/media/8rE47U8UH1yEi9SI0o/giphy.gif",
#"https://media.giphy.com/media/nO8kxVKdXSaek/giphy.gif",
"https://media.giphy.com/media/s09VXOiOg79As/giphy.gif",
"https://media.giphy.com/media/G3va31oEEnIkM/giphy.gif",
"https://media.giphy.com/media/7QkZap9kQ1iy4/giphy.gif"
]

wink_list = ['https://media.discordapp.net/attachments/436139161070731264/462679150163918849/orig.gif',
			 'https://cdn.discordapp.com/attachments/436139161070731264/462679245945307146/giphy-1.gif',
			 'https://cdn.discordapp.com/attachments/436139161070731264/462679323506245632/girls_winking_02.gif',
			 'https://cdn.discordapp.com/attachments/436139161070731264/462679514330431488/girls_winking_16.gif',
			 'https://cdn.discordapp.com/attachments/436139161070731264/462679850553966602/tenor.gif']

fuck_list = ['https://media.giphy.com/media/9DayfKDecuCwUMRs38/giphy.gif',
			 'https://media.giphy.com/media/621mG5MkWcAX00a5J4/giphy.gif',
			 'https://media.giphy.com/media/29MEDvCpkzMMCvuZB5/giphy.gif',
			 'https://media.giphy.com/media/cUVsttxcdKJJVRiFAd/giphy.gif',
			 'https://media.giphy.com/media/PQxjfWa751RVJTtkS5/giphy.gif',
			 'https://media.giphy.com/media/9J6Rye3Fz0Dq0oHeVH/giphy.gif']

five_list = [
'https://media.giphy.com/media/4H70la8QkZfaUvV9G4/giphy.gif',
'https://media.giphy.com/media/DQbDgJn2P5Wy3S1zr5/giphy.gif',
'https://media.giphy.com/media/pG5zFVdVsrQVteCbVS/giphy.gif',
'https://media.giphy.com/media/cRMGrkAyMdyeASLKqK/giphy.gif',
'https://media.giphy.com/media/4ZkpV1LyG0dvxYW2Zd/giphy.gif',
'https://media.giphy.com/media/n5GussPCZuekOaqMW3/giphy.gif',
"https://media.giphy.com/media/wrzf9P70YWLJK/giphy.gif",
"https://media.giphy.com/media/l0MYClvw1RPj1cZeo/giphy.gif",
"https://media.giphy.com/media/l0HlD43ktQ5f8fuWk/giphy.gif",
"https://media.giphy.com/media/3o85xHXqvkattTod68/giphy.gif",
"https://media.giphy.com/media/1nPJ5XLyZWdd4xFGw5/giphy.gif",
"https://media.giphy.com/media/r2BtghAUTmpP2/giphy.gif",
"https://media.giphy.com/media/l2JhwnKUuohwKLDnG/giphy.gif",
"https://media.giphy.com/media/2AlVpRyjAAN2/giphy.gif",
"https://media.giphy.com/media/YfTPHZ85fGnle/giphy.gif",
"https://media.giphy.com/media/C4lSxWjqSJLfG/giphy.gif",
"https://media.giphy.com/media/3o7TKTeL57EJdYFKBW/giphy.gif",
"https://media.giphy.com/media/2O0vM7oQMp4A0/giphy.gif",
"https://media.giphy.com/media/9wZybot8h5Nte/giphy.gif",
"https://media.giphy.com/media/diKF8kxuomAxy/giphy.gif",
"https://media.giphy.com/media/100QWMdxQJzQC4/giphy.gif",
"https://media.giphy.com/media/fLK0eUlYZoB6E/giphy.gif",
"https://media.giphy.com/media/13wHPKuKou0ndu/giphy.gif",
"https://media.giphy.com/media/uIu5b0YYpTPR6/giphy.gif",
"https://media.giphy.com/media/3oEduV4SOS9mmmIOkw/giphy.gif",
"https://media.giphy.com/media/fm4WhPMzu9hRK/giphy.gif",
"https://media.giphy.com/media/26ufmAlKt4ne2JDnq/giphy.gif",
"https://media.giphy.com/media/jG7UpdWLjoYuY/giphy.gif",
"https://media.giphy.com/media/l46CcVsDKp97gSDhm/giphy.gif",
"https://media.giphy.com/media/sSzCDRnOMaq3K/giphy.gif",
"https://media.giphy.com/media/DohrJX1h2W5RC/giphy.gif",
"https://media.giphy.com/media/13zazU4zSlJCiA/giphy.gif",
"https://media.giphy.com/media/WrGiAHYhZZYZ2/giphy.gif",
"https://media.giphy.com/media/3oEdvaba4h0I536VYQ/giphy.gif",
"https://media.giphy.com/media/l0HlSYVgZLQ1Y4GdO/giphy.gif",
"https://media.giphy.com/media/353PfIYZWFHaM/giphy.gif",
"https://media.giphy.com/media/3DZzjf7xCgb7y/giphy.gif",
"https://media.giphy.com/media/3o6gEgwAO6ojq63sbu/giphy.gif",
"https://media.giphy.com/media/3o85xspHMaZxVGbzY4/giphy.gif",
"https://media.giphy.com/media/l46ClnO4XNwTCuXsY/giphy.gif",
"https://media.giphy.com/media/26BREWfA5cRZJbMd2/giphy.gif",
"https://media.giphy.com/media/3o6Zt7hngn9xwnN7lC/giphy.gif",
"https://media.giphy.com/media/xT0xeQbBYVUPiKkzQs/giphy.gif",
"https://media.giphy.com/media/S6l0TQr5lomVG/giphy.gif",
"https://media.giphy.com/media/3o7TKMYAveUIqs3ZUk/giphy.gif",
"https://media.giphy.com/media/3o7buds9QVy5nCVCLe/giphy.gif",
"https://media.giphy.com/media/l42Pnm9RVo0ZG4EmI/giphy.gif",
"https://media.giphy.com/media/TQHyiK771gQw0/giphy.gif",
"https://media.giphy.com/media/l2R020v6spGBpGHrG/giphy.gif",
"https://media.giphy.com/media/GzCp9sGvlWKOc/giphy.gif",
"https://media.giphy.com/media/cAiBXaCjbHTry/giphy.gif",
"https://media.giphy.com/media/yUcor4CrgbrUY/giphy.gif",
"https://media.giphy.com/media/mJ8Xr2xYruvyF0QtMK/giphy.gif",
"https://media.giphy.com/media/QtJZpBnBJJew/giphy.gif",
"https://media.giphy.com/media/l41JOPMjzNoMYl71e/giphy.gif",
"https://media.giphy.com/media/gQ8qWas3GxlPq/giphy.gif",
"https://media.giphy.com/media/l2R0f2obXKscBVE1q/giphy.gif",
"https://media.giphy.com/media/x58AS8I9DBRgA/giphy.gif"
]





piar_statuses = [
"discord.gg/tomori • Мир Томори",
"discord.gg/8FdcCXA • LemStudio [FunVoice]",
"discord.gg/G2Tynh4 • Neko.Land"
]


background_change_price = 1000

background_list = ['neko.jpg',
				   'miku.jpg',
                   'stare.jpg',
                   'magic.jpg',
                   'night.jpg',
				   'autumn.jpg',
                   'kanade.jpg',
                   'forest.jpg',
				   'railway.jpg',
                   'adventure.jpg',
				   'mountains.jpg',
                   'schoolgirl.jpg',
                   'fairy_tale.jpg',
				   'nao_tomori.jpg',
				   'anime_girl.jpg',
                   'angel_beats.jpg',
				   'guilty_crown.jpg',
				   'yukari_yakumo.jpg',
                   'girl_with_wings.jpg',
                   'your_lie_in_april.jpg'
]

background_name_list = ['Neko',
        			    'Miku',
                        'Stare',
                        'Magic',
                        'Night',
           			    'Autumn',
                        'Kanade',
                        'Forest',
        			    'Railway',
                        'Adventure',
        			    'Mountains',
                        'Schoolgirl',
                        'Fairy_Tale',
        			    'Nao Tomori',
        			    'Anime Girl',
                        'Angel Beats',
        			    'Guilty Crown',
        			    'Yukari Yakumo',
                        'Girl With Wings',
                        'Your Lie In April'
]

prefix_list = [
	'!',
	'?',
	'$',
	't!',
	't?',
	't$',
	'.',
	'-',
	'+',
	'\\',
	';',
	'>',
	'<',
	'~',
	'^',
	'=',
	'_'
]

black_filename_list = [
"2018-03-15_10.26.23_1",
"2018-03-16_01.41.19_1",
"2018-03-16_12.07.43_1",
"2018-03-16_12.12.56_1",
"2018-04-14_04.00.21_1",
"2018-04-14_04.00.35_1"
]

ddos_name_list = [
"FeijhV",
"t.me",
"jsop",
"ᴊsᴏᴘ",
"traff",
"ᴛ.ᴍᴇ",
"discord.gg"
]

slot_kanna = '<:kanna:491965559907418112>'
slot_pantsu1 = '<:pantsu:491967185254613023>'
slot_pantsu2 = '<:pantsu2:491965559387455506>'
slot_doge = '<:doge:491965559529930753>'
slot_trap = '<:trap:491965559806754847>'
slot_salt = '<:salt:491965559613947904>'
slot_awoo = '<:awoo:491965559748165633>'
slot_boom = '<:booom:491965559496376330>'
slot_melban = '<:banned:491965559659954201>'
slots_ver = []

i = 0
while i < 3:
	i += 1
	slots_ver.append(slot_kanna)
i = 0
while i < 50:
	i += 1
	slots_ver.append(slot_melban)
i = 0
while i < 50:
	i += 1
	slots_ver.append(slot_boom)
i = 0
while i < 5:
	i += 1
	slots_ver.append(slot_pantsu1)
i = 0
while i < 10:
	i += 1
	slots_ver.append(slot_pantsu2)
i = 0
while i < 15:
	i += 1
	slots_ver.append(slot_doge)
i = 0
while i < 20:
	i += 1
	slots_ver.append(slot_salt)
i = 0
while i < 25:
	i += 1
	slots_ver.append(slot_awoo)
i = 0
while i < 30:
	i += 1
	slots_ver.append(slot_trap)

default_message = discord.Embed(color=0xC5934B)
success_message = discord.Embed(color=0x00ff08)
error_message = discord.Embed(color=0xff3838)

default_color = 0xC5934B
success_color = 0x00ff08
error_color = 0xff3838

reaction_mes_ids = ["482646036116930560"]

emoji_zverolud_id = "481379601642160132"
emoji_nolife_id = "481379280433971220"
emoji_avanturist_id = "470944111697068032"

reaction_zverolud_ids = [
	"477367163980611595",
	"476748304844193792",
	"476723872117293057",
	"476723872000114689",
	"476723866358513665",
	"476723868825026560",
	"465254757867454474",
	"465254757531910145",
	"472795129917210654",
	"472795130521190410",
	"480372045226573825",
	"477368446384996362",
	"465254756357767168",
	"476728329446359061",
	"480810858965106719"
]

reaction_nolife_ids = [
	"477367163980611595",
	"476748304844193792",
	"476723872117293057",
	"476723872000114689",
	"476723866358513665",
	"476723868825026560",
	"465254757867454474",
	"465254757531910145",
	"472795129917210654",
	"472795130521190410",
	"480372039555743747",
	"477368446384996362",
	"465254756357767168",
	"476728329446359061",
	"476723866031357952"
]

reaction_avanturist_ids = [
	"477367163980611595",
	"476748304844193792",
	"476723872117293057",
	"476723872000114689",
	"476723866358513665",
	"476723868825026560",
	"465254757867454474",
	"465254757531910145",
	"472795129917210654",
	"472795130521190410",
	"480372035319758873",
	"477368446384996362",
	"465254756357767168",
	"476728329446359061",
	"465568335904505886"
]

not_log_servers = [
"264445053596991498",
"110373943822540800"
]

log_join_leave_server_channel_id = "493196075352457247"

#             Ананасовая Печенюха         Unknown           Питерская Илита            Teris
admin_list = ['430383342182203392', '316287332779163648', '432879426066317322', '281037696225247233']
#               Ананасовая Печенюха         Unknown           Питерская Илита            Teris                Oddy38              mankidelufi
support_list = ['430383342182203392', '316287332779163648', '432879426066317322', '281037696225247233', '476626134432481281', '342557917121347585']

nazarik_id = "465616048050143232"
nazarik_log_id = "480692089332695040"

tester_role_id = "477738087212908544"

uptimes = 0

global top_servers
top_servers = []

tomori_links = '[Проголосовать](https://discordbots.org/bot/491605739635212298/vote "за Томори") \
[Patreon](https://www.patreon.com/tomori_discord "Поддержать донатом") \
[YouTube](https://www.youtube.com/channel/UCxqg3WZws6KxftnC-MdrIpw "Канал творческого объединения Tomori Project") \
[Telegram](https://t.me/TomoriDiscord "Наш telegram канал") \
[Сайт](https://discord.band "Наш сайт") \
[ВК](https://vk.com/tomori_discord "Наша группа в ВК")'

def clear_name(name):
	return re.sub(r'[\';"\\]+', '', name)
