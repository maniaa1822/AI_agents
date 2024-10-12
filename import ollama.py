import ollama

class LLM_Agent:
    def __init__(self, name, role):
        self.name = name
        self.role = role
        self.model = "llama3.2:3b"

    def send_message(self, recipient, message):
        print(f"{self.name} -> {recipient.name}: {message}")
        recipient.receive_message(self, message)

    def receive_message(self, sender, message):
        print(f"{self.name} received message from {sender.name}: {message}")
        response = self.process_message(message)
        if response:
            sender.send_message(self, response)

    def process_message(self, message):
        prompt = f"Role: {self.role}\nMessage: {message}"
        response = ollama.generate(model=self.model, prompt=prompt)
        return response['response']

class ResearcherAgent(LLM_Agent):
    def __init__(self, name):
        super().__init__(name, "Researcher")

    def perform_task(self, topic):
        print(f"{self.name} is researching on: {topic}")
        try:
            with open("research_data.txt", "r") as file:
                response = file.read()
        except FileNotFoundError:
            query = f"""Research the topic '{topic}' and gather information and present them in the most rigorous way, avoid lists and summarization.
            use an academic style of language and phrasing, be as detailed and complete as possible."""
            research = ollama.generate(model=self.model, prompt=query)
            response = research['response']
            with open("research_output.txt", "w") as file:
                file.write(response)
        return response

class SummarizerAgent(LLM_Agent):
    def __init__(self, name):
        super().__init__(name, "Summarizer")

    def summarize(self, data):
        prompt = f"Summarize the following data: {data}"
        summary = ollama.generate(model=self.model, prompt=prompt)
        response = summary['response']
        with open("summary_output.txt", "w") as file:
            file.write(response)
        return response
    
    def refine_summary(self, summary, critique,reseach_data):
        with open("research_data.txt", "r") as file:
            research_data = file.read()
        prompt = f"Refine the following summary based on the original text and the critique:\n Research Data:{research_data}\nSummary: {summary}\nCritique: {critique}"
        response = ollama.generate(model=self.model, prompt=prompt)
        with open("refined_summary_output.txt", "w") as file:
            file.write(response['response'])
        return response['response']

class CriticAgent(LLM_Agent):
    def __init__(self, name):
        super().__init__(name, "Critic")

    def critique(self, data):
        prompt = f"Critique the following research and suggest improvements: {data}"
        critique = ollama.generate(model=self.model, prompt=prompt)
        response = critique['response']
        with open("critique_output.txt", "w") as file:
            file.write(response)
        return response

# RecursiveSummarizerAgent refines the summary based on critique
class RecursiveSummarizerAgent:
    def __init__(self, summarizer, critic, max_iterations=3, quality_threshold="This summary looks good now!"):
        self.summarizer = summarizer
        self.critic = critic
        self.max_iterations = max_iterations
        self.quality_threshold = quality_threshold

    def refine_summary(self, summary, critique):
        with open("research_output.txt", "r") as file:
            research_data = file.read()
        prompt = f"Refine the following summary based on the original text and the critique:\n Research Data:{research_data}\nSummary: {summary}\nCritique: {critique}"
        response = ollama.generate(model="llama3.2:3b", prompt=prompt)
        return response['response']

    def recursive_summarization(self, research_data):
        # Generate initial summary
        summary = self.summarizer.summarize(research_data)
        print(f"Initial Summary: {summary}")

        # Save initial summary to a file
        with open("summary_iterations.txt", "w") as file:
            file.write(f"Iteration 0: {summary}\n")

        for iteration in range(self.max_iterations):
            print(f"\nIteration {iteration + 1}:")
            
            # Step 1: Critique the summary
            critique = self.critic.critique(summary)
            print(f"Critique: {critique}")
            
            # Check if critique suggests the summary is good
            if self.quality_threshold.lower() in critique.lower():
                print("Final Summary accepted based on critique.")
                break

            # Step 2: Refine the summary
            summary = self.refine_summary(summary, critique)
            print(f"Refined Summary: {summary}")

            # Save summary iteration to a file
            with open("summary_iterations.txt", "a") as file:
                file.write(f"Iteration {iteration + 1}: {summary}\n")
        
        return summary

class AgentManager:
    def __init__(self):
        self.researcher = ResearcherAgent("Agent A (Researcher)")
        self.summarizer = SummarizerAgent("Agent B (Summarizer)")
        self.critic = CriticAgent("Agent C (Critic)")
        self.recursive_summarizer = RecursiveSummarizerAgent(self.summarizer, self.critic)

    def execute_task(self, topic):
        # Step 1: Researcher gathers information
        research_data = self.researcher.perform_task(topic)
        print(f"Research Data: {research_data}")

        # Step 2: Summarizer summarizes the research
        #summary = self.summarizer.summarize(research_data)
        #print(f"Summary: {summary}")

        # Step 3: Critic critiques the research
        #critique = self.critic.critique(summary)
        #print(f"Critique: {critique}")
        
        #summarizer summary improvement
        summary = self.recursive_summarizer.recursive_summarization(research_data)
        print(f"Final Summary:\n{summary}")

if __name__ == "__main__":
    manager = AgentManager()
    topic = "the impact of climate change on biodiversity"
    manager.execute_task(topic)
