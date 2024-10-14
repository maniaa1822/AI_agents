import ollama
from typing import List, Tuple
import sys
import time

class Agent:
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.individual_context = ""
        self.shared_context = ""
    
    def update_individual_context(self, new_info: str):
        self.individual_context += new_info
    
    def update_shared_context(self, new_info: str):
        self.shared_context += new_info
    
    def display_output(self, text: str):
        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(0.01)  # Adjust this value to change the display speed
        sys.stdout.write('\n')
    
    def generate_response(self, prompt: str, display: bool = False) -> str:
        full_prompt = f"{self.role}\n\nShared Context:\n{self.shared_context}\n\nIndividual Context:\n{self.individual_context}\n\nPrompt: {prompt}\n\nResponse:"
        response = ollama.generate(model="llama3.2:3b", prompt=full_prompt)
        if display:
            print(f"\n{self.name} is responding:")
            self.display_output(response['response'])
        return response['response']

class Researcher(Agent):
    def find_information(self, topic: str, display: bool = False) -> str:
        prompt = f"Please provide a comprehensive summary of the latest information on the topic: {topic}. Include key facts, different perspectives, and any recent developments."
        return self.generate_response(prompt, display)

class Writer(Agent):
    def reflect_on_debate(self, topic: str, display: bool = False) -> str:
        prompt = f"Reflect on the interactive dialogue about '{topic}' from your perspective as a {self.role}. Consider the key points raised, areas of agreement and disagreement, and how this discussion has influenced or refined your viewpoint. Summarize your reflections concisely."
        reflection = self.generate_response(prompt, display)
        self.update_individual_context(f"Reflection on the debate:\n{reflection}\n")
        return reflection

    def write_article(self, topic: str, display: bool = False) -> str:
        prompt = f"Write an article on the topic: {topic} from your perspective as a {self.role}. Use the shared context, individual context (including your reflection on the debate), and the results of the interactive dialogue as a basis for your article. The article should be well-structured, present a coherent argument or viewpoint, and acknowledge the complexity of the topic as revealed in the debate."
        return self.generate_response(prompt, display)

class ResearchTeam:
    def __init__(self, agents: List[Agent], display_output: bool = False):
        self.agents = agents
        self.display_output = display_output
    
    def share_context(self, context: str):
        for agent in self.agents:
            agent.update_shared_context(context)
    
    def conduct_research(self, topic: str) -> str:
        researcher = next((agent for agent in self.agents if isinstance(agent, Researcher)), None)
        if researcher:
            return researcher.find_information(topic, self.display_output)
        else:
            raise ValueError("No Researcher agent found in the team")

    def interactive_dialogue(self, topic: str, questions_per_writer: int = 3) -> str:
        dialogue = []
        writers = [agent for agent in self.agents if isinstance(agent, Writer)]
        
        if len(writers) < 2:
            raise ValueError("At least two Writer agents are required for a dialogue")
        
        for round in range(questions_per_writer):
            for questioner in writers:
                # Questioner asks a question
                question_prompt = f"Round {round + 1}: As the {questioner.role}, ask a thought-provoking question about '{topic}' that challenges or explores different perspectives. Be concise."
                question = questioner.generate_response(question_prompt, self.display_output)
                dialogue.append(f"{questioner.name} asks: {question}")
                
                # All writers (including the questioner) answer the question
                for respondent in writers:
                    answer_prompt = f"As the {respondent.role}, answer the following question about '{topic}': {question}\nProvide your perspective concisely."
                    answer = respondent.generate_response(answer_prompt, self.display_output)
                    dialogue.append(f"{respondent.name} answers: {answer}")
                    
                    # Update individual contexts
                    for writer in writers:
                        if writer != respondent:
                            writer.update_individual_context(f"{respondent.name}'s answer: {answer}\n")
                    respondent.update_individual_context(f"My answer: {answer}\n")
                
                dialogue.append("")  # Add a blank line for readability
        
        return "\n".join(dialogue)

    def reflect_on_debate(self, topic: str) -> List[Tuple[str, str]]:
        reflections = []
        for agent in self.agents:
            if isinstance(agent, Writer):
                reflection = agent.reflect_on_debate(topic, self.display_output)
                reflections.append((agent.name, reflection))
        return reflections

    def write_articles(self, topic: str) -> List[Tuple[str, str]]:
        articles = []
        for agent in self.agents:
            if isinstance(agent, Writer):
                article = agent.write_article(topic, self.display_output)
                articles.append((agent.name, article))
        return articles

def save_to_file(filename: str, content: str):
    with open(filename, "w") as f:
        f.write(content)

def main():
    topic = input("Enter research topic: ")
    display_output = input("Display AI outputs in real-time? (y/n): ").lower() == 'y'
    
    # Create agents
    researcher = Researcher("Researcher", "Information Gatherer")
    scientific_writer = Writer("Scientific Writer", "Science Perspective")
    religious_writer = Writer("Religious Writer", "Religious Perspective")
    philosophical_writer = Writer("Philosophical Writer", "Philosophical Perspective")
    
    # Create research team
    team = ResearchTeam([researcher, scientific_writer, religious_writer, philosophical_writer], display_output)
    
    print("Researching the topic...")
    research_info = team.conduct_research(topic)
    team.share_context(f"Research on {topic}:\n{research_info}")
    
    print("Initiating interactive dialogue...")
    dialogue_result = team.interactive_dialogue(topic)
    save_to_file("interactive_dialogue.txt", f"Interactive Dialogue on the topic: {topic}\n\n{dialogue_result}")
    print("Interactive dialogue saved to 'interactive_dialogue.txt'")
    
    print("Writers are reflecting on the debate...")
    reflections = team.reflect_on_debate(topic)
    reflection_content = "\n\n".join([f"{name}'s Reflection:\n{reflection}" for name, reflection in reflections])
    save_to_file("debate_reflections.txt", f"Reflections on the debate about: {topic}\n\n{reflection_content}")
    print("Reflections saved to 'debate_reflections.txt'")
    
    print("Generating articles...")
    articles = team.write_articles(topic)
    for name, article in articles:
        save_to_file(f"{name.lower().replace(' ', '_')}_article.txt", article)
        print(f"{name}'s article saved to '{name.lower().replace(' ', '_')}_article.txt'")

if __name__ == "__main__":
    main()