from openai import OpenAI
import logging
from ast import literal_eval
from agents.prompts import langfun_day_by_day_agent_prompt
system_prompt = """You are given a travel plannign query as well as the current state of the travel plan as well as reference information for the travel plan in CSV format. Please give me the next day of the plan. The output must fulfill the following criteria:
1. Include specifics such as flight numbers (e.g., F0123456), restaurant names, and hotel names. 
2. All the information in your plan should be derived from the provided reference information. You must adhere to the format given in the example. 
3. All details should align with common sense. For example, attraction visits and meals are expected to be diverse; you can see which attractions and restaurants have been visited in the current state. 
4. The symbol '-' indicates that information is unnecessary. For example, in the provided sample, you do not need to plan after returning to the departure city. When you travel to two cities in one day, you should note it in the 'Current City' section as in the example (i.e., from A to B).
***** EXAMPLE *****
Query: Could you create a travel plan for 7 people from Ithaca to Charlotte spanning 3 days, from March 8th to March 14th, 2022, with a budget of $30,200?
Current State: 
Day 1:
Current City: from Ithaca to Charlotte
Transportation: Flight Number: F3633413, from Ithaca to Charlotte, Departure Time: 05:38, Arrival Time: 07:46
Breakfast: Nagaland's Kitchen, Charlotte
Attraction: The Charlotte Museum of History, Charlotte
Lunch: Cafe Maple Street, Charlotte
Dinner: Bombay Vada Pav, Charlotte
Accommodation: Affordable Spacious Refurbished Room in Bushwick!, Charlotte

Day 2:
Current City: Charlotte
Transportation: -
Breakfast: Olive Tree Cafe, Charlotte
Attraction: The Mint Museum, Charlotte;Romare Bearden Park, Charlotte.
Lunch: Birbal Ji Dhaba, Charlotte
Dinner: Pind Balluchi, Charlotte
Accommodation: Affordable Spacious Refurbished Room in Bushwick!, Charlotte

Next Day:
Day 3:
Current City: from Charlotte to Ithaca
Transportation: Flight Number: F3786167, from Charlotte to Ithaca, Departure Time: 21:42, Arrival Time: 23:26
Breakfast: Subway, Charlotte
Attraction: Books Monument, Charlotte.
Lunch: Olive Tree Cafe, Charlotte
Dinner: Kylin Skybar, Charlotte
Accommodation: -
"""

user_prompt = """You are a proficient planner. You will be provided reference information and the current state of a travel planning plan as well as the initial travel planning query. Please give me the next day of the plan.

Reference Information: {reference_information}
Query: {query}
Current State: {current_state}
```
"""

reference_information = """Description: Attractions in Toledo
```csv
 Name Latitude Longitude Address Phone Website City
 Toledo Zoo 41.621643 -83.582543 2 Hippo Way, Toledo, OH 43609, USA (419) 385-5721 https://www.toledozoo.org/ Toledo
National Museum of the Great Lakes 41.656491 -83.515160 1701 Front St, Toledo, OH 43605, USA (419) 214-5000 http://www.nmgl.org/ Toledo
 Toledo Museum of Art 41.658327 -83.559325 2445 Monroe St, Toledo, OH 43620, USA (419) 255-8000 http://www.toledomuseum.org/ Toledo
 Imagination Station 41.651930 -83.531614 1 Discovery Way, Toledo, OH 43604, USA (419) 244-2674 http://www.imaginationstationtoledo.org/ Toledo
 Toledo Botanical Garden 41.666369 -83.672088 5403 Elmer Dr, Toledo, OH 43615, USA (419) 270-7500 https://metroparkstoledo.com/explore-your-parks/toledo-botanical-garden/ Toledo
 International Park 41.650401 -83.526607 Rails To Trails Next To Maumee River, Toledo, OH 43605, USA (419) 936-2875 https://toledo.oh.gov/services/public-service/parks-recreation-forestry/parks/ Toledo
 Toledo Firefighters Museum 41.692968 -83.564122 918 W Sylvania Ave, Toledo, OH 43612, USA (419) 478-3473 http://toledofirefightersmuseum.org/ Toledo
 Wildwood Preserve Metropark 41.681807 -83.665319 5100 Central Ave, Toledo, OH 43615, USA (419) 407-9700 http://metroparkstoledo.com/wildwoodpreserve Toledo
 Point Place Lighthouse, llc 41.699612 -83.478822 Toledo, OH 43611, USA (419) 626-7980 http://coastal.ohiodnr.gov/lucas/bayviewpark Toledo
 Toledo History Museum 41.653320 -83.533357 425 N St Clair St, Toledo, OH 43604, USA (419) 215-2437 https://www.toledohistorymuseum.org/ Toledo
 Greetings From Toledo 41.647810 -83.522896 120 Main St, Toledo, OH 43605, USA Unknown Unknown Toledo
 Glass Pavilion 41.659663 -83.558082 2444 Monroe St, Toledo, OH 43620, USA (419) 255-8000 http://www.toledomuseum.org/glass-pavilion/ Toledo
 Promenade Park 41.649539 -83.533349 400 Water St, Toledo, OH 43604, USA (419) 936-2875 https://toledo.oh.gov/ Toledo
 Delaware Park 41.610612 -83.589960 3076-3098, River Rd, Toledo, OH 43614, USA (419) 936-2875 http://toledo.oh.gov/services/public-service/parks-recreation-forestry/parks/ Toledo
 Glass City River Wall 41.626630 -83.530865 1306 Miami St, Toledo, OH 43605, USA Unknown http://glasscityriverwall.org/ Toledo
 Perspective Arcade Public Art 41.655880 -83.536191 740 Jackson St CTR 1920, Toledo, OH 43604, USA Unknown Unknown Toledo
 Toledo Zoo Aquarium 41.617921 -83.580203 2700 Broadway St, Toledo, OH 43609, USA (419) 385-5721 http://www.toledozoo.org/ Toledo
 Cullen Park 41.704689 -83.474873 4526 N Summit St, Toledo, OH 43611, USA Unknown http://cullenpark.org/ Toledo
 Frida Kahlo Mural 41.640384 -83.543156 402 Broadway St, Toledo, OH 43604, USA Unknown Unknown Toledo
 Jamie Farr Park 41.671158 -83.504970 2140 N Summit St, Toledo, OH 43611, USA (419) 936-3887 https://toledo.oh.gov/services/public-service/parks-recreation-forestry/ Toledo
```
Description: Restaurants in Toledo
```csv
 Name Average Cost Cuisines Aggregate Rating City
182 Devotay 78 Chinese, BBQ, Seafood 4.0 Toledo
730 Bombay Brasserie 32 Tea, Pizza, Mediterranean 4.2 Toledo
821 Barbeque Nation 78 Desserts, Tea, Bakery, American, Mediterranean 4.4 Toledo
845 The Punjabi Essence Restaurant 72 Desserts, Tea, Mexican, Chinese, Seafood 3.6 Toledo
886 The Chocolate Room 95 Chinese, Mexican, Pizza, BBQ 3.6 Toledo
1101 Spice Wok 24 Tea, Pizza, Italian, French, BBQ 3.1 Toledo
1124 Baskin Robbins 76 Tea, Desserts, Fast Food 3.3 Toledo
1244 The People & Co. 84 Seafood, Pizza, BBQ, Fast Food 3.7 Toledo
1367 Roll's Royce 100 Tea, Cafe, BBQ, Desserts 3.2 Toledo
2285 The Woking Mama 62 Pizza, French, BBQ, Fast Food, Indian, Seafood 4.4 Toledo
2540 Divtya Budhlya Wada Restaurant 35 Tea, Seafood, Fast Food 3.8 Toledo
2856 Rabri Bhandar 90 Pizza, Bakery, Fast Food, Cafe, Indian 3.2 Toledo
3521 Barista 11 Desserts, Bakery, Fast Food, Indian, Seafood 3.2 Toledo
4761 Mother Sweets 24 Seafood, Indian, Fast Food 3.4 Toledo
4953 Bharat Chicken Inn 22 Pizza, BBQ 2.4 Toledo
4979 Dawat 46 Tea, Cafe, Bakery, Pizza 2.9 Toledo
5515 Kumar Hotel 14 Bakery, BBQ, Seafood 3.4 Toledo
6419 The Cake Shop 74 Desserts, BBQ, Cafe, Indian, Seafood 3.3 Toledo
6489 Jasmine Fast Food Centre 19 BBQ, Desserts 2.9 Toledo
6589 Sindh Sweet Corner 58 Tea, French, Mexican, Bakery 2.7 Toledo
7001 Amigo's Hub 30 Desserts, Tea, Mexican, Bakery, Seafood 3.7 Toledo
7011 Crazy Kitchen Lounge & Terrace 25 Fast Food, Pizza, Italian 3.9 Toledo
7210 Cafe Coffee Day 47 French, BBQ, Fast Food, Indian, Seafood 0.0 Toledo
7555 Bhape Di Hatti 42 Tea, BBQ, Fast Food, Cafe, Mediterranean 3.1 Toledo
7934 Health Buzzz 19 Tea, BBQ, Seafood 3.1 Toledo
8110 Kafe Republic 94 Chinese, Pizza, BBQ 3.1 Toledo
8181 Pita Pit 28 Bakery, BBQ, Italian 3.6 Toledo
8615 Domino's Pizza 77 Cafe, Fast Food 2.4 Toledo
9059 Pizza Hut 80 Cafe, Bakery, Indian, Pizza 3.3 Toledo
9267 Percolator Coffee House 97 Seafood, Fast Food 3.6 Toledo
```
Description: Accommodations in Toledo
```csv
 NAME price room type house_rules minimum nights maximum occupancy review rate number city
 Sunny Modern Lux Private House with Parking 614.0 Entire home/apt No smoking & No children under 10 & No parties 3.0 3 4.0 Toledo
 TIGER’S REST 375.0 Entire home/apt No pets & No children under 10 2.0 2 5.0 Toledo
 Newly reno 1BR Harlem brownstone 354.0 Entire home/apt No children under 10 5.0 2 3.0 Toledo
 Cozy Bedroom Uptown Manhattan 1042.0 Private room No children under 10 4.0 1 5.0 Toledo
 Sunny Railroad Apt 496.0 Entire home/apt No pets & No parties & No visitors 6.0 3 3.0 Toledo
 Summer 2019 Modern 2 Bedroom Flat New York City 284.0 Entire home/apt No parties & No smoking 3.0 2 5.0 Toledo
25 minutes from Manhattan, shared room bunk beds 1159.0 Shared room No children under 10 & No smoking 3.0 1 2.0 Toledo
 The home is where the heart is. 174.0 Entire home/apt No visitors & No smoking 2.0 2 5.0 Toledo
 Your Dream 1 bed Apartment in the heart of SoHo 701.0 Entire home/apt No parties & No children under 10 2.0 7 5.0 Toledo
 Belo Quarto/w/UPGRADE to entire apartment 1144.0 Private room No parties 2.0 2 4.0 Toledo
```
Description: Attractions in Cleveland
```csv
 Name Latitude Longitude Address Phone Website City
 Cleveland Metroparks Zoo 41.445947 -81.712625 3900 Wildlife Way, Cleveland, OH 44109, USA (216) 661-6500 https://www.clevelandmetroparks.com/zoo Cleveland
 The Cleveland Museum of Art 41.507926 -81.611972 11150 East Blvd, Cleveland, OH 44106, USA (216) 421-7350 https://www.clevelandart.org/ Cleveland
 Cleveland Botanical Garden 41.511139 -81.609598 11030 East Blvd, Cleveland, OH 44106, USA (216) 721-1600 https://holdenfg.org/ Cleveland
 Greater Cleveland Aquarium 41.496574 -81.703834 2000 Sycamore St, Cleveland, OH 44113, USA (216) 862-8803 http://greaterclevelandaquarium.com/ Cleveland
 Great Lakes Science Center 41.507420 -81.696598 601 Erieside Ave, Cleveland, OH 44114, USA (216) 694-2000 https://greatscience.com/ Cleveland
 Rock & Roll Hall of Fame 41.508541 -81.695369 1100 E 9th St, Cleveland, OH 44114, USA (216) 781-7625 https://www.rockhall.com/ Cleveland
 Edgewater Park 41.490290 -81.735455 Cleveland, OH 44102, USA (216) 635-3200 https://clevelandmetroparks.com/parks/visit/parks/lakefront-reservation/edgewater-park Cleveland
Cleveland Harbor West Pierhead Lighthouse 41.509008 -81.717699 2800 Whiskey Island Dr, Cleveland, OH 44102, USA Unknown Unknown Cleveland
 Mill Creek Falls 41.445048 -81.625326 Mill Creek Trail, Cleveland, OH 44105, USA (216) 635-3200 https://clevelandmetroparks.com/parks/visit/parks/garfield-park-reservation/mill-creek-falls-overlook Cleveland
 A Christmas Story House 41.468738 -81.687382 3159 W 11th St, Cleveland, OH 44109, USA (216) 298-4919 http://www.achristmasstoryhouse.com/ Cleveland
 The Children's Museum of Cleveland 41.504466 -81.659912 3813 Euclid Ave, Cleveland, OH 44115, USA (216) 791-7114 https://cmcleveland.org/ Cleveland
 Cleveland Cultural Gardens 41.518994 -81.618188 10823 Magnolia Dr, Cleveland, OH 44106, USA (216) 220-3075 http://www.culturalgardens.org/ Cleveland
 Cleveland History Center 41.513028 -81.611624 10825 East Blvd, Cleveland, OH 44106, USA (216) 721-5722 https://www.wrhs.org/plan-your-visit/ Cleveland
 Cleveland Script Sign - Edgewater Park 41.487580 -81.749276 Cleveland Memorial Shoreway, Cleveland, OH 44102, USA (800) 321-1001 https://www.thisiscleveland.com/locations/cleveland-script-sign-edgewater-park Cleveland
 Cleveland Museum of Natural History 41.511524 -81.612884 1 Wade Oval Dr, Cleveland, OH 44106, USA (216) 231-4600 https://www.cmnh.org/ Cleveland
 Museum of Contemporary Art Cleveland 41.508910 -81.604645 11400 Euclid Ave, Cleveland, OH 44106, USA (216) 421-8671 http://www.mocacleveland.org/ Cleveland
 Cleveland Script Sign - Tremont 41.484672 -81.692870 1502 Abbey Ave, Cleveland, OH 44113, USA (800) 321-1001 http://www.thisiscleveland.com/ Cleveland
 International Women’s Air & Space Museum 41.511568 -81.689978 1501 N Marginal Rd, Cleveland, OH 44114, USA (216) 623-1111 http://www.iwasm.org/ Cleveland
 West Side Market 41.484708 -81.702839 1979 W 25th St, Cleveland, OH 44113, USA (216) 664-3387 http://www.westsidemarket.org/ Cleveland
 Washington Reservation 41.455960 -81.660307 4408 Pallister Dr, Cleveland, OH 44105, USA Unknown https://www.clevelandmetroparks.com/parks/visit/parks/washington-reservation Cleveland
```
Description: Restaurants in Cleveland
```csv
 Name Average Cost Cuisines Aggregate Rating City
667 Bikanerwala 10 Tea, Bakery, BBQ, Fast Food 3.2 Cleveland
685 Makhan Fish and Chicken Corner 25 Pizza, French, Fast Food, Chinese, Seafood 3.4 Cleveland
1609 Pind Balluchi 96 Chinese, Pizza, French, BBQ, Cafe 2.7 Cleveland
1916 Costa Coffee 97 French, Pizza, Fast Food 0.0 Cleveland
2164 Me Kong Bowl 19 Cafe, BBQ, Seafood 4.0 Cleveland
2170 Green Leaf 73 Desserts, Tea, Cafe, BBQ, Chinese 3.0 Cleveland
2508 Big Chicken 27 Cafe, Pizza, Bakery, Italian 3.5 Cleveland
2530 Nineties 31 Cafe, Pizza, Desserts 3.9 Cleveland
2708 Master Bakers 80 Tea, Pizza, Italian, BBQ, Seafood 3.7 Cleveland
3447 Keventers 54 Pizza, American, Desserts, Fast Food 3.8 Cleveland
4474 Gullu's 38 Mexican, Pizza, Indian, Seafood 3.1 Cleveland
5389 Kathi House 52 Seafood, Fast Food 0.0 Cleveland
5844 Al Mughal 99 Desserts, Tea, French, BBQ, Seafood 0.0 Cleveland
5937 Bruncheez 36 Tea, Pizza, Bakery, Cafe, Indian, Mediterranean 0.0 Cleveland
6615 LSK Express 29 Indian, Mediterranean, BBQ, Seafood 0.0 Cleveland
7763 Bakermania 71 Bakery, Pizza, BBQ, Cafe 0.0 Cleveland
8353 Wild Chef House 93 Tea, Cafe, Mediterranean, Seafood 0.0 Cleveland
8918 Southern Santushti Cafe 20 Seafood, Pizza, BBQ, Fast Food 0.0 Cleveland
9318 Five Boroughs 97 French, Bakery, BBQ, Seafood 4.1 Cleveland
9529 Me侓hur 韄z韄elik Aspava 34 Chinese, Pizza, Mediterranean, Seafood 4.6 Cleveland
```
Description: Accommodations in Cleveland
```csv
 NAME price room type house_rules minimum nights maximum occupancy review rate number city
 Rare gem of an apartment in NYC. So Spacious! 918.0 Private room No parties & No children under 10 3.0 1 5.0 Cleveland
 Cozy minimalist room close to train (1) 593.0 Private room No parties 3.0 2 3.0 Cleveland
Richmond Hill 3 Bedroom apartment in Private home! 565.0 Entire home/apt No visitors 1.0 4 5.0 Cleveland
 Large bright artistic apartment 677.0 Entire home/apt No pets & No visitors 2.0 4 2.0 Cleveland
 Private room W/ private bathroom, shower, balcony 1188.0 Private room No children under 10 1.0 1 2.0 Cleveland
 Comfy bed in Cozy Home - GRAND ARMY PLAZA 996.0 Private room No smoking 2.0 1 5.0 Cleveland
 room in a soho loft 914.0 Private room No parties & No children under 10 & No visitors 3.0 2 2.0 Cleveland
 Modern Sunlit Room w/ Balcony on Famous Street! 979.0 Private room No smoking 4.0 2 4.0 Cleveland
Blocks to the High Line * West Village Home for 10 1031.0 Entire home/apt No parties 2.0 4 4.0 Cleveland
 Spacious Studio in E Flatbush 827.0 Entire home/apt No visitors 1.0 6 3.0 Cleveland
 Pleasant & Low-priced place in Manhattan 347.0 Private room No parties 1.0 1 2.0 Cleveland
 Private room in Sunnyside Gardens 408.0 Private room No smoking 2.0 2 1.0 Cleveland
 Gorgeous 1-2 BDR apartment in the Lower East Side 107.0 Entire home/apt No children under 10 & No pets 1.0 2 4.0 Cleveland
```
Description: Attractions in Dayton
```csv
 Name Latitude Longitude Address Phone Website City
 Carillon Historical Park 39.729197 -84.199902 1000 Carillon Blvd, Dayton, OH 45409, USA (937) 293-2841 http://www.daytonhistory.org/ Dayton
 Boonshoft Museum of Discovery 39.788635 -84.201991 2600 Deweese Pkwy, Dayton, OH 45414, USA (937) 275-7431 http://www.boonshoftmuseum.org/ Dayton
Dayton Aviation Heritage National Historical Park 39.755732 -84.211720 16 S Williams St, Dayton, OH 45402, USA (937) 225-7705 http://www.nps.gov/daav/contacts.htm Dayton
 National Museum of the US Air Force 39.780796 -84.109382 1100 Spaatz St, Dayton, OH 45433, USA (937) 255-3286 http://www.nationalmuseum.af.mil/ Dayton
 The Dayton Art Institute 39.766264 -84.201759 456 Belmonte Park N, Dayton, OH 45405, USA (937) 223-4278 http://www.daytonartinstitute.org/ Dayton
 America's Packard Museum 39.753472 -84.191767 420 S Ludlow St, Dayton, OH 45402, USA (937) 226-1710 https://www.americaspackardmuseum.org/ Dayton
 Wright Cycle Company Shop 39.755611 -84.211869 22 S Williams St, Dayton, OH 45402, USA (937) 225-7705 https://www.nps.gov/daav/planyourvisit/basicinfo.htm Dayton
 Sunwatch Indian Village 39.716361 -84.231675 2301 W River Rd, Dayton, OH 45417, USA (937) 268-8199 https://boonshoft.org/sunwatch-2/ Dayton
 The International Peace Museum 39.759655 -84.193297 10 N Ludlow St, Dayton, OH 45402, USA (937) 227-3223 http://peace.museum/ Dayton
 Wegerzyn Gardens MetroPark 39.804439 -84.204005 1301 E Siebenthaler Ave, Dayton, OH 45414, USA (937) 275-7275 http://www.metroparks.org/places-to-go/wegerzyn-gardens/ Dayton
 Five Rivers MetroParks 39.765223 -84.186155 409 E Monument Ave, Dayton, OH 45402, USA (937) 275-7275 https://www.metroparks.org/ Dayton
 National Aviation Hall Of Fame 39.781201 -84.109800 1100 Spaatz St, Dayton, OH 45433, USA (937) 256-0944 https://www.nationalaviation.org/ Dayton
 RiverScape MetroPark 39.764833 -84.188767 237 E Monument Ave, Dayton, OH 45402, USA (937) 274-0126 http://www.metroparks.org/places-to-go/riverscape/ Dayton
 Wright Brothers Memorial 39.794642 -84.088690 2380 Memorial Rd, Dayton, OH 45424, USA (937) 425-0008 https://www.nps.gov/daav/planyourvisit/visitorcenters.htm Dayton
 Eastwood MetroPark 39.787540 -84.122551 1385 Harshman Rd, Dayton, OH 45431, USA (937) 275-7275 http://www.metroparks.org/places-to-go/eastwood/ Dayton
 Patterson Homestead 39.734648 -84.182070 1815 Brown St, Dayton, OH 45409, USA (937) 293-2841 https://www.daytonhistory.org/visit/dayton-history-sites/patterson-homestead/ Dayton
 Deeds Point MetroPark 39.769972 -84.185586 510 Webster St, Dayton, OH 45402, USA (937) 275-7275 http://www.metroparks.org/places-to-go/deeds-point/ Dayton
 Possum Creek MetroPark 39.709372 -84.269249 4790 Frytown Rd, Dayton, OH 45417, USA (937) 275-7275 http://www.metroparks.org/places-to-go/possum-creek/ Dayton
 Wright Brothers National Museum 39.727820 -84.201520 Unnamed Road, Dayton, OH 45439, USA (937) 293-2841 https://www.daytonhistory.org/visit/things-to-see-do/wright-brothers-national-museum/ Dayton
 Smith Gardens 39.723707 -84.178378 Dayton, OH 45419, USA (937) 298-0600 https://oakwoodohio.gov/smith-memorial-gardens/ Dayton
```
Description: Restaurants in Dayton
```csv
 Name Average Cost Cuisines Aggregate Rating City
423 Star Noodle 17 Desserts, Bakery, BBQ, Fast Food, Chinese, American 4.6 Dayton
741 Onesta 47 Italian, BBQ, Fast Food, Cafe, American, Seafood 4.6 Dayton
1076 Pizza Express 92 Cafe, Pizza, American, Seafood 0.0 Dayton
1134 McDonald's 24 Tea, Mexican, Fast Food 3.3 Dayton
2003 Cookingo 78 Fast Food, French, BBQ, Seafood 0.0 Dayton
4206 Midnight Hunger Hub 87 Tea, BBQ, Seafood 4.5 Dayton
4250 Subway 11 BBQ, Desserts, Seafood 3.3 Dayton
5071 Kolcata Bengali Dhaba 51 Cafe, Mediterranean, Seafood 0.0 Dayton
5218 Malabar Catering House 56 Bakery, BBQ, Fast Food 3.2 Dayton
5256 Kasturi Family Restaurant 64 Pizza, Italian, French, BBQ, Fast Food, Cafe 3.0 Dayton
5288 Cafe Tandoor 100 Desserts, Tea, BBQ, Bakery, American, Mediterranean 0.0 Dayton
5519 Pindiwala 21 Pizza, Bakery 3.0 Dayton
5526 Kati Roll Cottage 15 Pizza, Bakery, BBQ, Seafood 3.7 Dayton
5874 Billu's Hut 77 Bakery, BBQ, Fast Food, Mediterranean, Seafood 3.9 Dayton
5942 Halal Pizza 'n' Joy 37 Seafood, Pizza, Bakery, Fast Food 0.0 Dayton
6339 Cilantro Woodapple 14 Fast Food, Seafood, Desserts, Italian 3.0 Dayton
6457 Nukkadwala 38 Desserts, Tea, Fast Food, Cafe, American, Mediterranean 3.8 Dayton
6669 CG's - Lounge Cafe Bar 29 Pizza, Indian, Seafood 3.9 Dayton
7110 Madras Cafe 68 Cafe, Pizza, Bakery, Chinese, Indian 3.4 Dayton
7475 Pizza Hut 76 Desserts, Cafe, Mexican, Bakery, Chinese, Seafood 3.6 Dayton
7879 Chatkora Food N Snacks Corner 88 Fast Food, Bakery, Italian 2.9 Dayton
8013 Gupta Sweets 48 Desserts, Tea, Bakery, Cafe, Indian 0.0 Dayton
9216 22nd Parallel 48 Tea, Bakery, BBQ 4.5 Dayton
```
Description: Accommodations in Dayton
```csv
 NAME price room type house_rules minimum nights maximum occupancy review rate number city
 Studio apartment; close to tourist attractions 769.0 Entire home/apt No visitors & No smoking 2.0 6 4.0 Dayton
 Luxurious, Sunny Apartment Overlooking Park 226.0 Entire home/apt No pets & No parties & No children under 10 2.0 2 5.0 Dayton
 Spacious West Harlem Studio! 418.0 Entire home/apt No children under 10 2.0 2 2.0 Dayton
 New York Hotel 618.0 Private room No visitors & No children under 10 7.0 1 5.0 Dayton
Modern & Cozy Studio In Best East Village Location 499.0 Entire home/apt No parties 2.0 4 3.0 Dayton
 Private and Comfortable bedroom 200.0 Private room No parties & No children under 10 & No visitors 7.0 2 5.0 Dayton
 Renovated & Spacious Chelsea Studio 752.0 Entire home/apt No children under 10 3.0 7 3.0 Dayton
 Sunny, peaceful home in fantastic location 1185.0 Private room No pets 1.0 2 4.0 Dayton
 Huge Room for Nightly Stays Downtown or Monthly 1021.0 Private room No smoking 5.0 2 3.0 Dayton
 Beautiful well lit studio located in Brooklyn, NY 1079.0 Entire home/apt No pets 1.0 4 5.0 Dayton
 Beautiful 1-br with Spectacular View 538.0 Entire home/apt No visitors 14.0 5 3.0 Dayton
 One BR duplex loft in midtown east townhouse - 43 223.0 Entire home/apt No pets 30.0 2 5.0 Dayton
```
Description: Flight from Minneapolis to Toledo on 2022-03-17
```csv
There is no flight from Minneapolis to Toledo on 2022-03-17.
```
Description: Self-driving from Minneapolis to Toledo
```csv
self-driving, from Minneapolis to Toledo, duration: 9 hours 43 mins, distance: 1,057 km, cost: 52
```
Description: Taxi from Minneapolis to Toledo
```csv
taxi, from Minneapolis to Toledo, duration: 9 hours 43 mins, distance: 1,057 km, cost: 1057
```
Description: Flight from Toledo to Cleveland on 2022-03-19
```csv
There is no flight from Toledo to Cleveland on 2022-03-19.
```
Description: Self-driving from Toledo to Cleveland
```csv
self-driving, from Toledo to Cleveland, duration: 1 hour 50 mins, distance: 183 km, cost: 9
```
Description: Taxi from Toledo to Cleveland
```csv
taxi, from Toledo to Cleveland, duration: 1 hour 50 mins, distance: 183 km, cost: 183
```
Description: Flight from Cleveland to Dayton on 2022-03-21
```csv
There is no flight from Cleveland to Dayton on 2022-03-21.
```
Description: Self-driving from Cleveland to Dayton
```csv
self-driving, from Cleveland to Dayton, duration: 3 hours 11 mins, distance: 340 km, cost: 17
```
Description: Taxi from Cleveland to Dayton
```csv
taxi, from Cleveland to Dayton, duration: 3 hours 11 mins, distance: 340 km, cost: 340
```
Description: Flight from Dayton to Minneapolis on 2022-03-23
```csv
There is no flight from Dayton to Minneapolis on 2022-03-23.
```
Description: Self-driving from Dayton to Minneapolis
```csv
self-driving, from Dayton to Minneapolis, duration: 10 hours 31 mins, distance: 1,138 km, cost: 56
```
Description: Taxi from Dayton to Minneapolis
```csv
taxi, from Dayton to Minneapolis, duration: 10 hours 31 mins, distance: 1,138 km, cost: 1138
```
"""
query = "We require a 7-day travel itinerary for two leaving from Minneapolis and covering three cities in Ohio, starting from March 17th to March 23rd, 2022. Our budget is up to $5,100. We will be accompanied by our pets, so we need pet-friendly accommodations. Our meals should preferably include American, Mediterranean, Chinese, and Italian cuisines. Please note we prefer not to take any flights so our travel plan should not include them."
current_state = """[Day 1:
Current City: from Minneapolis to Toledo
Transportation: self-driving, from Minneapolis to Toledo, duration: 9 hours 43 mins, distance: 1,057 km, cost: 52
Breakfast: -
Attraction: Toledo Zoo, Toledo
Lunch: 182 Devotay, Toledo
Dinner: The People & Co., Toledo
Accommodation: Sunny Modern Lux Private House with Parking, Toledo]"""
api_key = "INSERT_API_KEY"
temperature = 0.5


def call_gpt4v_extraction(u, api_key, temperature, system_prompt):
    payload = {
        "model": "gpt-4-turbo",
        "messages": [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "assistant",
            "content":  u
        }
        ],
        "temperature": temperature,
        "top_p": 1,
        "frequency_penalty": 0,
        "presence_penalty": 0,
    }
    try:
        client = OpenAI(api_key=api_key)
        r = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=payload["messages"],
            temperature=temperature,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        return r.choices[0].message.content
        # print(r.json())
        # response = literal_eval("""{"id":"chatcmpl-9OvDrYWDnVijkgAGzCeA9F5JCdHgb","choices":[{"finish_reason":"stop","index":0,"logprobs":null,"message":{"content":"{\n  \"instructions\": \"none\"\n}","role":"assistant","function_call":null,"tool_calls":null}}],"created":1715726863,"model":"gpt-4-turbo-2024-04-09","object":"chat.completion","system_fingerprint":"fp_294de9593d","usage":{"completion_tokens":9,"prompt_tokens":243,"total_tokens":252}}""")
        # print("response: ", response)
        # response = response['choices'][0]['message']['content']
        # print(response)
        # json_start_index = response.find("```json")
        # if json_start_index != -1:
        #     response = response[json_start_index:]
        #     response = response.replace("```json\n", "").replace("\n```", "")
        #     response = literal_eval(response)
        #     if "instructions" in response:
        #         if isinstance(response["instructions"], list):
        #             #logger.info(f"{v['app_name']} task {v['index']} for query {v['search_query']} calling gpt4 with result: {response}")
        #             return response["instructions"]
        #         else:
        #             if isinstance(response["instructions"], str) and response["instructions"].lower() == "none":
        #                 #logger.info(f"{v['app_name']} task {v['index']} for query {v['search_query']} calling gpt4 with result: {response['instructions']}")
        #                 return "none"
        #             else:
        #                 #logger.info(f"{v['app_name']} task {v['index']} for query {v['search_query']} calling gpt4 with result: {response['instructions']}")
        #                 return response
        # else:
        #     #logger.info(f"{v['app_name']} task {v['index']} for query {v['search_query']} calling gpt4 with result: {response.lower()}")
        #     return response.lower()
    except Exception as e:
        #logger.exception(f"error when calling gpt4: {e}, with gpt_response: {r}")
        print(f"error when calling gpt4: {e}")
        return None
    
if __name__ == "__main__":
    u = user_prompt.format(reference_information=reference_information, query=query, current_state=current_state)
    print(call_gpt4v_extraction(u, api_key, temperature, system_prompt))