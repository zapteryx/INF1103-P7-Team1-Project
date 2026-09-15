**1. Problem Statement and Target Users**

**Problem statement**: Social Service organisations have to deal with many cases that need to be assessed. Going through each case manually can take up a lot of time, especially when each case is unique while each shelter has different capacities and levels of services and care. Our program utilises AI to help social workers with the initial triage process by identifying the urgency of each case, checking which shelters are suitable and recommending possible placement. This helps social workers to save time and make the process more efficient while still keeping the final decision with the social worker.

What real-world problem does your application aim to solve?
- Social service organizations have large intakes that require better categorization and triage of each case / candidate.
- Utilizing AI to aid social service organizations to triage by improving efficiency of categorisation, prioritisation and assignment of cases to appropriate shelters for those in need (i.e. some shelters provide overnight resting spaces, whereas some provide long-term rehab)

Who are the intended users of the application?
- Ministry of Social and Family Development (MSF)
- Social service organizations
- Social Workers

**2. User Inputs**
What information or data will users provide to the system?
- Cases/Candidates: age, number of dependents, narrative notes, medical needs, financial needs, special needs, type of care required (short-term, long-term)
- Shelters: locations, contact, level of care provided, maximum capacity and current population (to reduce overcrowding)
- To ensure accuracy, data is split between hard facts (structured) and human context (unstructured)




**3. Use of AI**
How will AI be utilized within the application?
- AI will go through the cases and determine the urgency level of the case, as well as providing insights for each shelter-candidate combination (such as whether their needs can be met at a particular shelter)

What outputs, insights, or recommendations will the AI generate from the user inputs?
- AI will generate the urgency level for each case (From 1-5, with 5 being most urgent and 1 being least urgent)
- AI will generate a structured JSON dictionary of criterias that the shelter meets for a particular case, and will provide a recommended shelter for the candidate from the narrative text (if applicable)

**4. Business Rules**
What business rules, validations, or decision-making logic will be applied to the AI-generated outputs?
- For all AI-generated outputs, we must validate and ensure that the provided data is in the format that we expect it to be (i.e. numbers / true-false values)
- AI should provide sufficient information for our logic manager to sort and process the data appropriately
- Validates the AI's JSON outputs against real-time data using IF/THEN rules to enforce business constraints, manage shelter capacity rerouting, and process admin rejection feedback to trigger secondary AI recommendations.
- Converts raw intake record into a prompt, executes API call and validates JSON responses
