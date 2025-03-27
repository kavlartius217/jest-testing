

#EXA SEARCH TOOL
from crewai_tools import EXASearchTool
from crewai.tools import tool
from exa_py import Exa
import os

exa_api_key = os.getenv("EXA_API_KEY")

@tool("Exa search and get contents")
def search_and_get_contents_tool(question: str) -> str:
    """Tool using Exa's Python SDK to run semantic search and return result highlights."""

    exa = Exa(exa_api_key)

    response = exa.search_and_contents(
        question,
        type="neural",
        use_autoprompt=True,
        num_results=3,
        highlights=True
    )

    parsedResult = ''.join([
    f'<Title id={idx}>{eachResult.title}</Title>'  # Closing quote added
    f'<URL id={idx}>{eachResult.url}</URL>'  # Closing quote added
    f'<Highlight id={idx}>{"".join(eachResult.highlights)}</Highlight>'  # Closing quote added
    for (idx, eachResult) in enumerate(response.results)
])

    return parsedResult


from crewai import Agent, Task, Crew, Process
from crewai.project import CrewBase, agent, crew, task


@CrewBase
class TestingBot():
  """This crew aims to automate testing"""
  agents_config="/home/kavin/testing_automation_poc/agents_testing.yaml"
  tasks_config="/home/kavin/testing_automation_poc/tasks_testing.yaml"

  @agent
  def code_analyzer_agent(self)->Agent:
    return Agent(
      config=self.agents_config['code_analyzer_agent'],
      verbose=True
    )

  
  @agent
  def test_case_generator_agent(self)->Agent:
    return Agent(
      config=self.agents_config['test_case_generator_agent'],
      tools=[search_and_get_contents_tool],
      verbose=True
    )


  @agent
  def test_executor_agent(self)->Agent:
    return Agent(
      config=self.agents_config['test_executor_agent'],
      verbose=True,
      allow_code_execution=True,
      #code_execution_mode="safe",
      max_execution_time=300,
      max_retry_limit=3
    )


  @agent
  def bug_analyzer_agent(self)->Agent:
    return Agent(
      config=self.agents_config['bug_analyzer_agent'],
      tools=[search_and_get_contents_tool],
      verbose=True
    )

  @task
  def code_analysis_task(self)->Task:
    return Task(
      config=self.tasks_config['code_analysis_task']
    )

  @task
  def test_case_generation_task(self)->Task:
    return Task(
      config=self.tasks_config['test_case_generation_task']
    )

  @task
  def test_executor_task(self)->Task:
    return Task(
      config=self.tasks_config['test_executor_task']
    )

  @task
  def bug_analysis_task(self)->Task:
    return Task(
      config=self.tasks_config['bug_analysis_task']
    )

  @crew
  def crew(self)->Crew:
    return Crew(
      agents=[self.code_analyzer_agent(),self.test_case_generator_agent(),self.test_executor_agent(),self.bug_analyzer_agent()],
      tasks=[self.code_analysis_task(),self.test_case_generation_task(),self.test_executor_task(),self.bug_analysis_task()],
      process=Process.sequential,
      verbose=True
    )

test_1=TestingBot()

result = test_1.crew().kickoff({
    "code": """
    // userService.js - Simulated User Service with database interactions

const axios = require('axios');

class UserService {
    constructor() {
        this.users = [];
    }

    addUser(user) {
        if (!user || !user.name || !user.email) {
            throw new Error("Invalid user data");
        }
        this.users.push(user);
        return user;
    }

    getUserByEmail(email) {
        return this.users.find(user => user.email === email) || null;
    }

    async fetchUserFromAPI(userId) {
        try {
            const response = await axios.get(`https://jsonplaceholder.typicode.com/users/${userId}`);
            return response.data;
        } catch (error) {
            throw new Error("Failed to fetch user data");
        }
    }

    async fetchAllUsers() {
        try {
            const response = await axios.get(`https://jsonplaceholder.typicode.com/users`);
            return response.data;
        } catch (error) {
            throw new Error("Failed to fetch users");
        }
    }
}

module.exports = UserService;

    """,
  "framework":"jest"
    
})


print(result)


