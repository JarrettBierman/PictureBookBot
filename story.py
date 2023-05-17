from decouple import config
from PIL import Image
from gtts import gTTS
from datetime import datetime
import openai
import requests
import os

openai.api_key = config('GPT_KEY')
openai.organization = config("ORG")



def main():
    # generate_audio_visuals("Generate a story about four brothers fighting Spongebob Squarepant. Set up a exposition, conflict, and resolution. Separate the story into atleast 5 paragraphs. Output the story as 2 separate lists. One list, named \"TEXT\", contains each paragraph of the story in order. The second list, named \"IMAGES\", contains a generated image description based off each element in \"TEXT\". Do not number the elements of the list.")
    tts = gTTS("hello world")
    tts.save("hello.mp3")
    os.system("mpg321 hello.mp3")

def generate_audio_visuals(prompt):
    # set up folder
    cur_dir = str(datetime.now())
    os.mkdir(cur_dir)
    with open(cur_dir + "/prompt.txt", "w+") as file:
        file.write(prompt)

    # get response and format it correctly
    response_text = get_prompt_response(prompt)
    with open(cur_dir + "/full_response.txt", "w+") as file:
        file.write(response_text)

    text_start = response_text.find("TEXT:")
    images_start = response_text.find("IMAGES:")

    text_list = response_text[text_start:images_start]
    images_list = response_text[images_start:].split('\n')

    images_list = [item for item in images_list if len(item) > 0 and item != "IMAGES:"]

    with open(cur_dir + "/response_text.txt", "w+") as file:
        file.write(text_list)
    with open(cur_dir + "/response_image_prompts.txt", "w+") as file:
        file.write(str(images_list))

    # generate and download images
    for count, image_prompt in enumerate(images_list):
        img_url = get_image_response(image_prompt + ", digital art")
        download_image_from_url(img_url, cur_dir, f'image-{count}')

def get_prompt_response(prompt):
    """Generates a ChatGPT Response"""
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0301",
        messages=[
            {"role":"system", "content":"You are a thoughful storyteller with an admiration for adventure."},
            {"role":"user", "content": prompt}
        ]
    )
    response = completion.choices[0].message.content

    return response

def get_image_response(prompt):
    completion = openai.Image.create(
        prompt=prompt,
        n=1,
        size="1024x1024"
    )
    image_url = completion['data'][0]['url']
    return image_url

def download_image_from_url(url, folder, name):
    img_data = requests.get(url).content
    with open(f'{folder}/{name}.png', 'wb') as handler:
        handler.write(img_data)





if __name__ == "__main__":
    main()