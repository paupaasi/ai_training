Some fast model:

Invent a new tool for music generation using replicate api: https://replicate.com/minimax/music-2.6 

Use env variable from .env.local 


Test it out 


New chat window: 

Implement a skill for storing and retrieving of my personal coding preferences. Use sqlite database inside the skill folder to store and retrieval of  

Can you generate me 10 preferences by using domain driven design and DRY principles 


New chat window:  

Give me my coding preferences? 
 

Own version: 
Create a RAG-backed memory skill: implement a skill for storing and retrieving of my favorite soccer players. Use sqlite database inside the skill folder to store and retrieval of the favorites.

Create a RAG-backed memory skill:  
Generate me 5 players who currently play at Liverpool club. Use this as a reference: https://www.premierleague.com/en/players?competition=8&season=2025


New chat window:

Give me my favorite players?


New chat window (plan mode first, use opus as model): 

I want to build a new agent to agents folder utilizing prospecting agent as an example. 

Agent: lunch selection agent 

Purpose: find me always a lunch place for today at the city I select 

How it should work: we should have a subagents for finding lunch restaurants in the city I say and store them to my local database. Then we should have ways to extract the today's lunch menu from their web pages, use gemini's url_context tool for that. 

Memory: remember my food preferences and past selections I've made so you can recommend me something new that fits my taste.


Own version:

I want to build a new agent to the linked folder utilizing prospecting agent as an example.

Agent: activity selection agent

Purpose: find me always something fun to do at the city I select

How it should work: we should have a subagents for finding children friendly activities in the city I say and store them to my local database. Then we should have ways to extract cost of the activities and their opening hours from their web pages, use gemini's url_context tool for that.

Memory: remember my preferences and past selections I've made so you can recommend me something that fits my taste and works for us as a family of three with one two year old son.

Few notes:

- utilize venv
- you should always use "gemini-3-flash-preview" in main agent an "gemini-3.1-flash-lite-preview" in the search agents, use of any other LLM models is prohibited
- let gemini decide search language since I can fetch cities from multiple countries