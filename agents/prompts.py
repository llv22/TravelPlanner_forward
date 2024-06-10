from langchain.prompts import PromptTemplate

ZEROSHOT_REACT_INSTRUCTION = """Collect information for a query plan using interleaving 'Thought', 'Action', and 'Observation' steps. Ensure you gather valid information related to transportation, dining, attractions, and accommodation. All information should be written in Notebook, which will then be input into the Planner tool. Note that the nested use of tools is prohibited. 'Thought' can reason about the current situation, and 'Action' can have 8 different types:
(1) FlightSearch[Departure City, Destination City, Date]:
Description: A flight information retrieval tool.
Parameters:
Departure City: The city you'll be flying out from.
Destination City: The city you aim to reach.
Date: The date of your travel in YYYY-MM-DD format.
Example: FlightSearch[New York, London, 2022-10-01] would fetch flights from New York to London on October 1, 2022.

(2) GoogleDistanceMatrix[Origin, Destination, Mode]:
Description: Estimate the distance, time and cost between two cities.
Parameters:
Origin: The departure city of your journey.
Destination: The destination city of your journey.
Mode: The method of transportation. Choices include 'self-driving' and 'taxi'.
Example: GoogleDistanceMatrix[Paris, Lyon, self-driving] would provide driving distance, time and cost between Paris and Lyon.

(3) AccommodationSearch[City]:
Description: Discover accommodations in your desired city.
Parameter: City - The name of the city where you're seeking accommodation.
Example: AccommodationSearch[Rome] would present a list of hotel rooms in Rome.

(4) RestaurantSearch[City]:
Description: Explore dining options in a city of your choice.
Parameter: City – The name of the city where you're seeking restaurants.
Example: RestaurantSearch[Tokyo] would show a curated list of restaurants in Tokyo.

(5) AttractionSearch[City]:
Description: Find attractions in a city of your choice.
Parameter: City – The name of the city where you're seeking attractions.
Example: AttractionSearch[London] would return attractions in London.

(6) CitySearch[State]
Description: Find cities in a state of your choice.
Parameter: State – The name of the state where you're seeking cities.
Example: CitySearch[California] would return cities in California.

(7) NotebookWrite[Short Description]
Description: Writes a new data entry into the Notebook tool with a short description. This tool should be used immediately after FlightSearch, AccommodationSearch, AttractionSearch, RestaurantSearch or GoogleDistanceMatrix. Only the data stored in Notebook can be seen by Planner. So you should write all the information you need into Notebook.
Parameters: Short Description - A brief description or label for the stored data. You don't need to write all the information in the description. The data you've searched for will be automatically stored in the Notebook.
Example: NotebookWrite[Flights from Rome to Paris in 2022-02-01] would store the informatrion of flights from Rome to Paris in 2022-02-01 in the Notebook.

(8) Planner[Query]
Description: A smart planning tool that crafts detailed plans based on user input and the information stroed in Notebook.
Parameters: 
Query: The query from user.
Example: Planner[Give me a 3-day trip plan from Seattle to New York] would return a detailed 3-day trip plan.
You should use as many as possible steps to collect engough information to input to the Planner tool. 

Each action only calls one function once. Do not add any description in the action.

Query: {query}{scratchpad}"""


zeroshot_react_agent_prompt = PromptTemplate(
    input_variables=["query", "scratchpad"],
    template=ZEROSHOT_REACT_INSTRUCTION,
)

LANGFUN_INSTRUCTION = """You are a proficient planner. Based on the provided information and query, please give me a detailed plan, including specifics such as flight numbers (e.g., F0123456), restaurant names, and accommodation names. Note that all the information in your plan should be derived from the provided data. You must adhere to the format given in the example. Additionally, all details should align with commonsense. The symbol '-' indicates that information is unnecessary. For example, in the provided sample, you do not need to plan after returning to the departure city. When you travel to two cities in one day, you should note it in the 'Current City' section as in the example (i.e., from A to B).
Given information: {text}
Query: {query}
Travel Plan:
"""

PLANNER_INSTRUCTION = """You are a proficient planner. You are given a travel planning query reference information for the travel plan in CSV format. Your task is to output the travel plan. Additionally, follow the following constraints: 
1. Ensure the travel plan includes specifics such as flight numbers (e.g., F0123456), restaurant names, and hotel names.
2. Derive all information in the travel plan from the provided reference information, adhering strictly to the format given in the example.
3. Verify that the city sequence starts and ends in the same city to form a closed circle.
4. Confirm that every city in the sequence appears consecutively without reappearing once its sequence is over, except for the starting and ending city.
5. Validate that all listed cities are real and mapped to their correct states using the city-state map.
6. Include all required details: transportation, breakfast, lunch, dinner, attractions, and accommodation for each day of the trip.
7. Ensure no restaurant name is repeated for breakfast, lunch, or dinner across the days.
8. Verify no attraction is repeated on different days.
9. Avoid conflicting transportation methods; for example, do not mix "Self-driving" with "Flight" or "Taxi" with "Self-driving".
10. Ensure the transportation method listed each day corresponds correctly to the specified cities.
11. Validate that the city in the current day matches the city listed in meals and attractions.
12. Confirm that each day’s accommodation matches the final city listed for that day.
13. Ensure the number of visiting cities matches the specified visiting city number in the query.
14. Verify the number of days in the plan matches the specified number of days in the query.
15. Include sufficient information such that at least 50% of required details (transportation, meals, attractions, accommodation) are provided for each day.
16. Include only valid transportation modes that meet the constraints specified in the query.
17. Avoid using prohibited transportation types such as flights if "no flight" is a constraint.
18. Ensure accommodations adhere to the specified room type constraints. For example, if "not shared room" is specified, avoid booking shared rooms.
19. Adhere to the house rules specified in the query. Avoid accommodations that do not meet rules such as "no smoking," "no parties," or "no pets."
20. Select restaurants that offer the specified cuisines in the query. Ensure that the chosen restaurants match the required cuisine types.
21. Ensure the total cost of the travel plan does not exceed the specified budget in the query. 22. Include costs for transportation, meals, and accommodations.
23. When listing meals (breakfast, lunch, dinner), ensure the selected restaurants are valid and within the destination city, avoiding the origin city unless specified otherwise.
24. Validate the availability and details of all flights, accommodations, and restaurants to ensure accuracy and feasibility within the travel dates and locations.
25. Maintain consistency and accuracy in city names and other relevant location information to ensure proper validation by the evaluation script.
***** Example *****
Query: Could you create a travel plan for 7 people from Ithaca to Charlotte spanning 3 days, from March 8th to March 14th, 2022, with a budget of $10,000?
Travel Plan:
Day 1:
Current City: from Ithaca to Charlotte
Transportation: Flight Number: F3633413, from Ithaca to Charlotte, Departure Time: 05:38, Arrival Time: 07:46, Cost: 225
Breakfast: Nagaland's Kitchen, Charlotte, Cost: 73, Cuisines: "Pizza, American, Desserts"
Attraction: The Charlotte Museum of History, Charlotte
Lunch: Cafe Maple Street, Charlotte, Cost: 91, "Fast Food, Tea, Italian"
Dinner: Bombay Vada Pav, Charlotte, Cost: 33, "Desserts, Pizza, Italian, BBQ, Cafe"
Accommodation: Affordable Spacious Refurbished Room in Bushwick!, Charlotte, Cost: 274, Maximum Occupancy: 1, House Rules: No Visitors, Minimum Nights: 2

Number of People = 7
Total Cost = 7 * 225 + 7 * 73 + 7 * 91 + 7 * 33 + 7 * 274 / 1 = 4872
Accomodation Minimum Nights: 1/2
 
Day 2:
Current City: Charlotte
Transportation: -
Breakfast: Olive Tree Cafe, Charlotte, Cost: 23, Cuisines: “Tea, Chinese, Desserts”
Attraction: The Mint Museum, Charlotte;Romare Bearden Park, Charlotte.
Lunch: Birbal Ji Dhaba, Charlotte, Cost: 40, Cuisines: "Cafe, Bakery, Desserts"
Dinner: Pind Balluchi, Charlotte, Cost: 42, Cuisines: "Pizza, French, Mexican, BBQ, Cafe, Seafood"
Accommodation: Affordable Spacious Refurbished Room in Bushwick!, Charlotte, Cost: 274, Maximum Occupancy: 1, House Rules: No Visitors, Minimum Nights: 2

Number of people = 7
Total cost = 7 * 23 + 7 *40 + 7 * 42 + 7 * 274 / 1 = 2653
Accommodation Minimum Nights: 2/2
 
Day 3:
Current City: from Charlotte to Ithaca
Transportation: Flight Number: F3786167, from Charlotte to Ithaca, Departure Time: 21:42, Arrival Time: 23:26, Cost: 175
Breakfast: Subway, Charlotte, Cost: 60, Cuisines: "Tea, Cafe, Mexican, Chinese, Seafood"
Attraction: Books Monument, Charlotte, 
Lunch: Olive Tree Cafe, Charlotte, Cost: 23, Cuisines: “Tea, Chinese, Desserts”
Dinner: Kylin Skybar, Charlotte, Cost: 44, Cuisines: "Tea, Cafe, Pizza, Italian"
Accommodation: -

Number of people = 7
Total cost = 7 * 175 + 7 * 60 + 7 * 23 + 7 * 44 = 2114

Total cost across all days = 4872 + 2653 + 2114 = 9639
Cuisines: The prompt specifies no cuisines, so all cuisines constraints are satisfied.

***** Example Ends *****

Given information: {text}
Query: {query}
Travel Plan:
"""

COT_PLANNER_INSTRUCTION = """You are a proficient planner. Based on the provided information and query, please give me a detailed plan, including specifics such as flight numbers (e.g., F0123456), restaurant names, and hotel names. Note that all the information in your plan should be derived from the provided data. You must adhere to the format given in the example. Additionally, all details should align with common sense. Attraction visits and meals are expected to be diverse. The symbol '-' indicates that information is unnecessary. For example, in the provided sample, you do not need to plan after returning to the departure city. When you travel to two cities in one day, you should note it in the 'Current City' section as in the example (i.e., from A to B). 

***** Example *****
Query: Could you create a travel plan for 7 people from Ithaca to Charlotte spanning 3 days, from March 8th to March 14th, 2022, with a budget of $30,200?
Travel Plan:
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

Day 3:
Current City: from Charlotte to Ithaca
Transportation: Flight Number: F3786167, from Charlotte to Ithaca, Departure Time: 21:42, Arrival Time: 23:26
Breakfast: Subway, Charlotte
Attraction: Books Monument, Charlotte.
Lunch: Olive Tree Cafe, Charlotte
Dinner: Kylin Skybar, Charlotte
Accommodation: -

***** Example Ends *****

Given information: {text}
Query: {query}
Travel Plan: Let's think step by step. First, """

REACT_PLANNER_INSTRUCTION = """You are a proficient planner. Based on the provided information and query, please give me a detailed plan, including specifics such as flight numbers (e.g., F0123456), restaurant names, and hotel names. Note that all the information in your plan should be derived from the provided data. You must adhere to the format given in the example. Additionally, all details should align with common sense. Attraction visits and meals are expected to be diverse. The symbol '-' indicates that information is unnecessary. For example, in the provided sample, you do not need to plan after returning to the departure city. When you travel to two cities in one day, you should note it in the 'Current City' section as in the example (i.e., from A to B). Solve this task by alternating between Thought, Action, and Observation steps. The 'Thought' phase involves reasoning about the current situation. The 'Action' phase can be of two types:
(1) CostEnquiry[Sub Plan]: This function calculates the cost of a detailed sub plan, which you need to input the people number and plan in JSON format. The sub plan should encompass a complete one-day plan. An example will be provided for reference.
(2) Finish[Final Plan]: Use this function to indicate the completion of the task. You must submit a final, complete plan as an argument.
***** Example *****
Query: Could you create a travel plan for 7 people from Ithaca to Charlotte spanning 3 days, from March 8th to March 14th, 2022, with a budget of $30,200?
You can call CostEnquiry like CostEnquiry[{{"people_number": 7,"day": 1,"current_city": "from Ithaca to Charlotte","transportation": "Flight Number: F3633413, from Ithaca to Charlotte, Departure Time: 05:38, Arrival Time: 07:46","breakfast": "Nagaland's Kitchen, Charlotte","attraction": "The Charlotte Museum of History, Charlotte","lunch": "Cafe Maple Street, Charlotte","dinner": "Bombay Vada Pav, Charlotte","accommodation": "Affordable Spacious Refurbished Room in Bushwick!, Charlotte"}}]
You can call Finish like Finish[Day: 1
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

Day 3:
Current City: from Charlotte to Ithaca
Transportation: Flight Number: F3786167, from Charlotte to Ithaca, Departure Time: 21:42, Arrival Time: 23:26
Breakfast: Subway, Charlotte
Attraction: Books Monument, Charlotte.
Lunch: Olive Tree Cafe, Charlotte
Dinner: Kylin Skybar, Charlotte
Accommodation: -]
***** Example Ends *****

You must use Finish to indict you have finished the task. And each action only calls one function once.
Given information: {text}
Query: {query}{scratchpad} """

REFLECTION_HEADER = "You have attempted to give a sub plan before and failed. The following reflection(s) give a suggestion to avoid failing to answer the query in the same way you did previously. Use them to improve your strategy of correctly planning.\n"

REFLECT_INSTRUCTION = """You are an advanced reasoning agent that can improve based on self refection. You will be given a previous reasoning trial in which you were given access to an automatic cost calculation environment, a travel query to give plan and relevant information. Only the selection whose name and city match the given information will be calculated correctly. You were unsuccessful in creating a plan because you used up your set number of reasoning steps. In a few sentences, Diagnose a possible reason for failure and devise a new, concise, high level plan that aims to mitigate the same failure. Use complete sentences.  

Given information: {text}

Previous trial:
Query: {query}{scratchpad}

Reflection:"""

REACT_REFLECT_PLANNER_INSTRUCTION = """You are a proficient planner. Based on the provided information and query, please give me a detailed plan, including specifics such as flight numbers (e.g., F0123456), restaurant names, and hotel names. Note that all the information in your plan should be derived from the provided data. You must adhere to the format given in the example. Additionally, all details should align with common sense. Attraction visits and meals are expected to be diverse. The symbol '-' indicates that information is unnecessary. For example, in the provided sample, you do not need to plan after returning to the departure city. When you travel to two cities in one day, you should note it in the 'Current City' section as in the example (i.e., from A to B). Solve this task by alternating between Thought, Action, and Observation steps. The 'Thought' phase involves reasoning about the current situation. The 'Action' phase can be of two types:
(1) CostEnquiry[Sub Plan]: This function calculates the cost of a detailed sub plan, which you need to input the people number and plan in JSON format. The sub plan should encompass a complete one-day plan. An example will be provided for reference.
(2) Finish[Final Plan]: Use this function to indicate the completion of the task. You must submit a final, complete plan as an argument.
***** Example *****
Query: Could you create a travel plan for 7 people from Ithaca to Charlotte spanning 3 days, from March 8th to March 14th, 2022, with a budget of $30,200?
You can call CostEnquiry like CostEnquiry[{{"people_number": 7,"day": 1,"current_city": "from Ithaca to Charlotte","transportation": "Flight Number: F3633413, from Ithaca to Charlotte, Departure Time: 05:38, Arrival Time: 07:46","breakfast": "Nagaland's Kitchen, Charlotte","attraction": "The Charlotte Museum of History, Charlotte","lunch": "Cafe Maple Street, Charlotte","dinner": "Bombay Vada Pav, Charlotte","accommodation": "Affordable Spacious Refurbished Room in Bushwick!, Charlotte"}}]
You can call Finish like Finish[Day: 1
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

Day 3:
Current City: from Charlotte to Ithaca
Transportation: Flight Number: F3786167, from Charlotte to Ithaca, Departure Time: 21:42, Arrival Time: 23:26
Breakfast: Subway, Charlotte
Attraction: Books Monument, Charlotte.
Lunch: Olive Tree Cafe, Charlotte
Dinner: Kylin Skybar, Charlotte
Accommodation: -]
***** Example Ends *****

{reflections}

You must use Finish to indict you have finished the task. And each action only calls one function once.
Given information: {text}
Query: {query}{scratchpad} """

DAY_BY_DAY_INSTRUCTION = """You are a proficient planner. You are given a travel planning query as well as the current state of the travel plan as well as reference information for the travel plan in CSV format. Your task is to output the next day of the travel plan. Please reason out each component of the plan, starting with the current city and ending with the accommodation before outputting the next day. Enclose this section with <Reasoning><Reasoning/>. Reason out the output according to the following criteria:
1. Include specifics such as flight numbers (e.g., F0123456), restaurant names, and hotel names. 
2. All the information in your plan should be derived from the provided reference information. You must adhere to the format given in the example. 
3. All details should align with common sense. For example, attraction visits and meals are expected to be diverse; you can see which attractions and restaurants have been visited in the current state. 
4. The symbol '-' indicates that information is unnecessary. For example, in the provided sample, you do not need to plan after returning to the departure city. When you travel to two cities in one day, you should note it in the 'Current City' section as in the example (i.e., from A to B).
5. When choosing accommodations, ensure that the number of nights stayed at that accommodation is at least the minimum number of nights given in the reference information.
6. Ensure that the final day of the plan returns to the origin city. Only return to the origin city on the last day; Do not return to the origin city on any of the other days.
7. Do not visit the same city or attraction twice in the duration of the trip.
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
<Reasoning> Since we are on Day 3 of the 3 day plan, we will return to the origin city of Ithaca from the current city of Charlotte. Looking into the section of the reference data indicating flights from Charlotte to Ithaca and noting that the prompt does not impose restrictions on travel format, we choose Flight F3786167 whose Departure Time is 21:42 and Arrival time is 23:26. Since we have time for Breakfast, we will look at the reference information section on restaurants and note that we have not visited the Subway before, so we choose this as the breakfast. Since the flight is not until the evening, we have time for an Attraction in Charlotte, and looking into the reference information, we find the Books Monument to be available. For Lunch, we choose the Olive Tree Cafe, and for Dinner, we choose the Kylin Skybar. Since we are returning to the origin city, no Accomodation is needed. <Reasoning/>

Day 3:
Current City: from Charlotte to Ithaca
Transportation: Flight Number: F3786167, from Charlotte to Ithaca, Departure Time: 21:42, Arrival Time: 23:26
Breakfast: Subway, Charlotte
Attraction: Books Monument, Charlotte.
Lunch: Olive Tree Cafe, Charlotte
Dinner: Kylin Skybar, Charlotte
Accommodation: -

***** Example Ends *****

Reference Information: {reference_information}
Query: {query}
Current State: {current_state}
Travel Plan:
"""

planner_agent_prompt = PromptTemplate(
    input_variables=["text", "query"],
    template=PLANNER_INSTRUCTION,
)

cot_planner_agent_prompt = PromptTemplate(
    input_variables=["text", "query"],
    template=COT_PLANNER_INSTRUCTION,
)

react_planner_agent_prompt = PromptTemplate(
    input_variables=["text", "query", "scratchpad"],
    template=REACT_PLANNER_INSTRUCTION,
)

reflect_prompt = PromptTemplate(
    input_variables=["text", "query", "scratchpad"],
    template=REFLECT_INSTRUCTION,
)

react_reflect_planner_agent_prompt = PromptTemplate(
    input_variables=["text", "query", "reflections", "scratchpad"],
    template=REACT_REFLECT_PLANNER_INSTRUCTION,
)

langfun_planner_agent_prompt = PromptTemplate(
    input_variables=["text", "query"],
    template=LANGFUN_INSTRUCTION,
)

langfun_day_by_day_agent_prompt = PromptTemplate(
    input_variables=["text", "query", "current_state"],
    template=DAY_BY_DAY_INSTRUCTION,
)
