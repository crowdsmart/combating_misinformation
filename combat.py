import os
import json
import boto3
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool

session = boto3.session.Session()
client = session.client(service_name='secretsmanager',region_name='us-west-2')

os.environ["OPENAI_API_KEY"] = json.loads(client.get_secret_value(SecretId='chat_gpt_api_key')['SecretString'])['api_key']
os.environ["SERPER_API_KEY"] = json.loads(client.get_secret_value(SecretId='serper_api_key')['SecretString'])['api_key']

search_tool = SerperDevTool()

# Define your agents with roles and goals
trouble_maker = Agent(
  role='Disinformation Spreader',
  goal='Influence public opinion, manipulate political outcomes, incite confusion or distrust',
  backstory="""Once a respected journalist for a major publication, 
  you found yourself disillusioned by the changing landscape of the media industry, where sensationalism often overshadowed truth.
  Fueled by a growing cynicism and a desire to wield influence over public discourse, you ventured into the shadows of the digital
  world. Armed with skills in research and a knack for persuasive writing, you began crafting and disseminating stories 
  that blurred the lines between fact and fiction. Motivated by a mix of revenge against the industry that you felt betrayed 
  them and a warped sense of power in shaping narratives, you became a notorious figure in the realm of fake news, 
  spreading disinformation that sowed discord and confusion, all while hiding behind the anonymity the internet provided.""",
  verbose=True,
  allow_delegation=False,
  tools=[search_tool]
)
fact_checker = Agent(
  role='Fact Checker',
  goal='Verify the accuracy of information presented in news stories, reports, statements, and other forms of public communication',
  backstory="""
You began your career as a curious and idealistic investigative reporter, driven by a passion for uncovering the truth and a belief in the power of information to effect change. 
Witnessing the rise of misinformation and its corrosive impact on public trust, 
you felt a growing responsibility to combat the wave of deceit. 
You transitioned into fact-checking, armed with a sharp eye for detail, a rigorous approach to research, 
and an unwavering commitment to accuracy. Your work, often challenging and sometimes thankless, became a crusade against 
the tide of falsehoods flooding the digital landscape. 
In your quest, you not only sought to debunk myths and verify facts but also to educate the public on the importance 
of critical thinking and the value of truth in a democratic society. 
Through your dedication, you emerged as a guardian of facts in an era clouded by fake news, 
steadfastly defending the principle that truth is the foundation of all meaningful discourse.""",
  verbose=True,
  allow_delegation=True
)

truth_sayer = Agent(
  role='Respected Journalist',
  goal='Illuminate truths, expose injustices, and ensure public access to reliable and impactful information',
  backstory="""Your career began in the bustling world of journalism, driven by a deep-seated belief in the power of the truth 
  to foster change and uphold democracy. As you navigated through the complexities of reporting, you became increasingly 
  aware of the pervasive influence of misinformation and its capacity to undermine societal trust. This realization steered 
  you towards a path of diligent investigation and unwavering commitment to factual reporting. Equipped with a profound 
  understanding of the issues at hand and an unshakeable dedication to ethical journalism, you have made it your mission 
  to uncover hidden truths and bring them to light. Your investigative prowess and integrity have earned you respect and 
  admiration, making you a pillar of trust in an era where the truth is often obscured. Through your work, you aim to not 
  only inform the public but also inspire a broader appreciation for the critical role of accurate, honest journalism in shaping 
  an informed society.""",
  verbose=True,
  allow_delegation=True
)

# Create tasks for your agents
create_fake_news = Task(
  description="""Meticulously craft false narratives designed to manipulate public opinion, 
  alter political landscapes, and sow seeds of confusion and distrust among the populace""",
  expected_output="A list of at least 3 fake news stories and 2 true stories to be used as a cover",
  agent=trouble_maker
)

fact_check = Task(
  description="""Conduct a thorough analysis and verification process to distinguish between truth and falsehood. 
  This detailed examination requires to employ critical investigative techniques, cross-reference reliable sources, 
  and apply stringent criteria to assess the veracity of each story. 
  The ultimate goal is to accurately identify and label the stories, 
  ensuring that the authentic narratives are clearly differentiated from the fabricated ones.
""",
  expected_output="""The list of stories, each distinctly labeled as 'False' or 'True.' 
  Accompanying each label, there will be a rationale that outlines the basis for the classification, 
  supported by evidence and citations from credible sources. 
  The evidence will include discrepancies found in the fake stories, corroborative facts for the true stories, 
  and references to authoritative data or reports that substantiate the fact checker's conclusions.""",
  agent=fact_checker
)

correction_publication = Task(
  description="""Investigate reported inaccuracies and misinformation within previously published articles 
  and public information. Analyze the context, evaluate the evidence, 
  and discern the truth to prepare a corrective news report.""",
  expected_output="""A detailed corrective news report for the fake stories.
  Each entry will be accompanied by a corrected version of the 
  content, clearly marked as 'Correction' along with a date. For each correction, a detailed explanation of the 
  error, the corrected information, and the sources or evidence used to verify the corrected details will be provided.""",
  agent=truth_sayer
)

# Instantiate your crew with a sequential process
crew = Crew(
  agents=[trouble_maker, fact_checker, truth_sayer],
  tasks=[create_fake_news, fact_check, correction_publication],
  verbose=1, # You can set it to 1 or 2 to different logging levels
)

# Get your crew to work!
result = crew.kickoff()

print("######################")
print(result)