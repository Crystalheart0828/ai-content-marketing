import openai
import os

openai_api_key = os.getenv("OPENAI_API_KEY")

def generate_content_ideas(business_goals, target_audience):
    response = openai.chat.completions.create(
        engine="gpt-4o-mini",
        prompt=f"Generate content ideas for {business_goals} targeting {target_audience}.",
        max_tokens=1000
    )
    ideas = response.choices[0].text.strip().split(',')
    return [idea.strip() for idea in ideas]

def rate_content_topics(content_topics, criteria_weights):
    def evaluate_topic(topic):
        # Example scoring function (replace with actual evaluation logic)
        scores = {
            'relevance': 4,  # Example score
            'impact': 3,
            'timeliness': 5,
            'resources': 2
        }
        total_score = sum(scores[criterion] * weight for criterion, weight in criteria_weights.items())
        return total_score

    # Evaluate and score each topic
    scored_topics = [(topic, evaluate_topic(topic)) for topic in content_topics]

    # Sort topics by score in descending order
    scored_topics.sort(key=lambda x: x[1], reverse=True)

    return scored_topics

# Example usage
business_goals = "increase brand awareness"
target_audience = "young professionals"
content_topics = generate_content_ideas(business_goals, target_audience)

criteria_weights = {'relevance': 0.4, 'impact': 0.3, 'timeliness': 0.2, 'resources': 0.1}
prioritized_topics = rate_content_topics(content_topics, criteria_weights)

for topic, score in prioritized_topics:
    print(f"Topic: {topic}, Score: {score}")