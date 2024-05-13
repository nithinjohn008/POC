from flask import Flask, render_template, request, redirect, url_for
import openai
import os

# Set your OpenAI API key from an environment variable (recommended)
openai.api_key = os.getenv('YOUR OPENAI_API_KEY')
openai.api_key = os.getenv('OPENAI_API_KEY')
if not openai.api_key:
    raise ValueError("No OpenAI API key found. Set the OPENAI_API_KEY environment variable.")

app = Flask(__name__)
# Define the tones mapping globally
tones = {
    '1': 'Optimistic',
    '2': 'Inquisitive',
    '3': 'Urgent',
    '4': 'Informative',
    '5': 'Call to Action',
    '6': 'Humorous',
    '7': 'Inspirational',
    '8': 'Storytelling',
    '9': 'Conversational',
    '10': 'Educational'
}


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        content = request.form['content']
        selected_tones = request.form.getlist('tone-style')
        
        tweet_alternatives = []
        if '11' in selected_tones:
            for tone_value in range(1, 11):
                tone_name = tones.get(str(tone_value), 'Optimistic')
                tweet_alternatives += adapt_for_twitter(content, tone_name, 1)
        else:
            for tone_value in selected_tones:
                tone_name = tones.get(tone_value, 'Optimistic')
                tweet_alternatives += adapt_for_twitter(content, tone_name, 1)

        return render_template('index.html', tweet_alternatives=tweet_alternatives)

    return render_template('index.html')


def adapt_for_twitter(content, tone_name, n=1):
    tweets = []
    prompts = {
        'Optimistic': "Create a tweet that positively summarizes the following content, including a relevant hashtag, within 280 characters: '{}'",
        'Inquisitive': "Formulate a tweet that poses a thought-provoking question based on this content with a hashtag, staying under 280 characters: '{}'",
        'Urgent': "Draft a tweet that communicates urgency from this content and add a hashtag for impact, within a 280-character limit: '{}'",
        'Informative': "Summarize this content into an informative tweet, including a hashtag on the topic, without exceeding 280 characters: '{}'",
        'Call to Action': "Write a compelling call-to-action tweet from this content, including a motivating hashtag, within the 280-character limit: '{}'",
        'Humorous': "Turn this content into a humorous tweet, with a fitting hashtag, while keeping it under 280 characters: '{}'",
        'Inspirational': "Convey this content in an inspiring tweet, with a relevant hashtag, and ensure it's within 280 characters: '{}'",
        'Storytelling': "Narrate this content as a mini-story in a tweet, using a hashtag to engage readers, and keep it under 280 characters: '{}'",
        'Conversational': "Rewrite this content as a conversational tweet, including a hashtag, and make sure it's no more than 280 characters: '{}'",
        'Educational': "Condense this content into an educational tweet with insight, along with a descriptive hashtag, all within 280 characters: '{}'",
    }

    if tone_name not in prompts:
        return [{"text": f"Tone '{tone_name}' is not recognized.", "prompt_name": "Error", "image_url": None}]

    formatted_prompt = prompts[tone_name].format(content)
    model_name = "gpt-3.5-turbo"  # Change the model name if wanted

    for i in range(n):
        try:
            response = openai.ChatCompletion.create(
                model=model_name,
                messages=[{"role": "system", "content": formatted_prompt}],
                max_tokens=280
            )
            tweet = response.choices[0].message['content'].strip()
            image_url = generate_image_with_dalle(tweet)
            tweets.append({"text": tweet, "image_url": image_url, "prompt_name": tone_name})
        except Exception as e:
            tweets.append({"text": f"An error occurred: {e}", "image_url": None, "prompt_name": "Error"})

    return tweets


def generate_image_with_dalle(content):
    try:
        response = openai.Image.create(
            model="dall-e-3",
            prompt=content,
            n=1,
            size="1024x1024"
        )
        
        image_url = response['data'][0]['url']
        return image_url
    except Exception as e:
        print(f"An error occurred while generating the image: {e}")
        return None


if __name__ == '__main__':
    app.run(debug=True)
