import ollama

class Agent:
    def __init__(self, name, role):
        self.name = name
        self.role = role
        self.individual_context = ""
        self.shared_context = ""
    
    def update_individual_context(self, new_info):
        self.individual_context += new_info
    
    def update_shared_context(self, new_info):
        self.shared_context += new_info
    
    def generate_response(self, prompt):
        full_prompt = f"{self.role}\n\nShared Context:\n{self.shared_context}\n\nIndividual Context:\n{self.individual_context}\n\nPrompt: {prompt}\n\nResponse:"
        response = ollama.generate(model="llama3.2:3b", prompt=full_prompt)
        return response['response']

class Researcher(Agent):
    def find_information(self, topic):
        prompt = f"Please provide a comprehensive summary of the latest information on the topic: {topic}. Include key facts, different perspectives, and any recent developments."
        return self.generate_response(prompt)

class Writer(Agent):
    def reflect_on_debate(self, topic):
        prompt = f"Reflect on the interactive dialogue about '{topic}' from your perspective as a {self.role}. Consider the key points raised, areas of agreement and disagreement, and how this discussion has influenced or refined your viewpoint. Summarize your reflections concisely."
        reflection = self.generate_response(prompt)
        self.update_individual_context(f"Reflection on the debate:\n{reflection}\n")
        return reflection

    def write_article(self, topic):
        prompt = f"Write an article on the topic: {topic} from your perspective as a {self.role}. Use the shared context, individual context (including your reflection on the debate), and the results of the interactive dialogue as a basis for your article. The article should be well-structured, present a coherent argument or viewpoint, and acknowledge the complexity of the topic as revealed in the debate."
        return self.generate_response(prompt)

def interactive_dialogue(agent1, agent2, topic, rounds=5):
    dialogue = []
    for i in range(rounds):
        prompt1 = f"Round {i+1}: Based on the previous discussion, ask a thought-provoking question or make a statement about '{topic}' that challenges or explores {agent2.name}'s perspective. Be concise."
        response1 = agent1.generate_response(prompt1)
        agent1.update_individual_context(f"My question/statement: {response1}\n")
        agent2.update_individual_context(f"{agent1.name}'s question/statement: {response1}\n")
        dialogue.append(f"{agent1.name}: {response1}")

        prompt2 = f"Round {i+1}: Respond to {agent1.name}'s statement/question: '{response1}'. Then, ask a follow-up question or make a challenging statement about '{topic}' from your perspective. Be concise."
        response2 = agent2.generate_response(prompt2)
        agent2.update_individual_context(f"My response and question: {response2}\n")
        agent1.update_individual_context(f"{agent2.name}'s response and question: {response2}\n")
        dialogue.append(f"{agent2.name}: {response2}")
    
    return "\n".join(dialogue)

def main():
    topic = input("Enter research topic: ")
    
    researcher = Researcher("Researcher", "Information Gatherer")
    scientific_writer = Writer("Scientific Writer", "Science Perspective")
    religious_writer = Writer("Religious Writer", "Religious Perspective")
    
    print("Researching the topic...")
    information = researcher.find_information(topic)
    shared_context = f"Research on {topic}:\n{information}"
    
    for agent in [researcher, scientific_writer, religious_writer]:
        agent.update_shared_context(shared_context)
    
    print("Initiating interactive dialogue between Scientific and Religious perspectives...")
    dialogue_result = interactive_dialogue(scientific_writer, religious_writer, topic)
    print("Interactive dialogue complete.")
    
    # Save dialogue results to a file
    with open("interactive_dialogue.txt", "w") as f:
        f.write(f"Interactive Dialogue on the topic: {topic}\n\n")
        f.write(dialogue_result)
    print("Interactive dialogue results saved to 'interactive_dialogue.txt'")
    
    print("Writers are reflecting on the debate...")
    scientific_reflection = scientific_writer.reflect_on_debate(topic)
    religious_reflection = religious_writer.reflect_on_debate(topic)
    
    # Save reflections to a file
    with open("debate_reflections.txt", "w") as f:
        f.write(f"Reflections on the debate about: {topic}\n\n")
        f.write(f"Scientific Writer's Reflection:\n{scientific_reflection}\n\n")
        f.write(f"Religious Writer's Reflection:\n{religious_reflection}\n")
    print("Reflections saved to 'debate_reflections.txt'")
    
    print("Generating scientific article...")
    scientific_article = scientific_writer.write_article(topic)
    
    print("Generating religious article...")
    religious_article = religious_writer.write_article(topic)
    
    print("\n--- Scientific Article ---")
    print(scientific_article)
    print("\n--- Religious Article ---")
    print(religious_article)
    
    # Save the articles to files
    with open("scientific_article.txt", "w") as f:
        f.write(scientific_article)
    with open("religious_article.txt", "w") as f:
        f.write(religious_article)
    
    print("\nArticles have been saved to 'scientific_article.txt' and 'religious_article.txt'")

if __name__ == "__main__":
    main()