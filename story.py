from decouple import config
from gtts import gTTS
from datetime import datetime
from moviepy.editor import *
import openai
import requests
import random
import os
# from playsound import playsound
# from PIL import Image

openai.api_key = config('GPT_KEY')
openai.organization = config("ORG")



def main():
    # cur_dir = "story_assets/" + datetime.now().strftime("%y-%m-%d_%H-%M-%S")
    # story = "Generate a story about a goldendoodle dog who goes to the moon to try and find treats and comes across a moon monster that likes to trick dogs into becoming servants."
    # prompt = generate_prompt(story)
    # generate_audio_visual_assets(cur_dir, prompt)
    # create_movie(cur_dir)    
    
    create_movie("story_assets/23-05-19_18-07-42")
    
    
def create_movie(directory):
    image_files = [file for file in os.listdir(directory) if file.find('image-') > -1]
    clips = []
    script = AudioFileClip(f"{directory}/script.mp3").fx(afx.audio_fadeout, 1)
    offset = random.randint(15,75)
    bg_music_file = f"background_music/music{random.randint(1,11)}.mp3"
    bg_music = AudioFileClip(bg_music_file).subclip(offset, offset + script.duration).fx(afx.volumex, 0.1).fx(afx.audio_fadeout, 1).fx(afx.audio_fadein, 1)
    
    for image_file in image_files:
        clips.append(ImageClip(f"{directory}/{image_file}").set_duration(script.duration / len(image_files)).crossfadein(1.5).crossfadeout(1.5))
    
    final_video = concatenate_videoclips(clips, method='compose')
    final_video.audio = CompositeAudioClip([script, bg_music])
    final_video.write_videofile(f"{directory}/final_video.mp4", fps=24, audio_codec='aac')
    
    
def generate_prompt(first_sentence):
    '''first_sentence should be a complete sentences of set of sentences ended with a period. ie \"Generate a story about a pickle going through a divorce.\"'''
    
    format_specifier = "The output should be formatted as a title to the story, signified with the name \"TITLE\",  followed by two separate lists named \"STORY\" and \"IMAGES\" . \"STORY\" contains the generated story. \"IMAGES\" is list of image descriptions of what is happening in the story. The image descriptions must be in chronological order of the generated story, and each description must have as much detail as possible and inlcude physical characteristics about each character. Also, each image description should have the same context provided in the description itself. The output should be \"TITLE\" followed by all of \"STORY\" followed by all of \"IMAGES\". The lists must not be numbered."
        
    return first_sentence + " " + format_specifier

def generate_audio_visual_assets(directory, prompt):
    
    if not os.path.exists(directory):
        os.mkdir(directory)
        
    with open(directory + "/prompt.txt", "w+") as file:
        file.write(prompt)

    # get response
    response_text = get_prompt_response(prompt)
    with open(directory + "/full_response.txt", "w+") as file:
        file.write(response_text)

    text_start = response_text.find("STORY")
    images_start = response_text.find("IMAGES")

    # format title
    title = response_text[:text_start].strip()
    if title.find("TITLE:") != -1:
        title = title[6:]
    
    # format script and image list
    script = response_text[text_start+6:images_start]
    script = f"This story is called {title}.\n{script}"
    
    images_list = response_text[images_start:].split('\n')
    images_list = [item for item in images_list if len(item) > 12]
    
    # save title
    with open(directory + "/title.txt", "w+") as file:
        file.write(str(title))

    # save full prompt response
    with open(directory + "/script.txt", "w+") as file:
        file.write(script)

    # save image descriptions
    with open(directory + "/response_image_prompts.txt", "w+") as file:
        for image_desc in images_list:
            file.write(str(image_desc + '\n'))

    # generate and download images
    for count, image_prompt in enumerate(images_list):
        img_url = get_image_response(image_prompt + ", digital art")
        download_image_from_url(img_url, directory, f'image-{count}')
    
    # generate and download tts files
    tts = gTTS(script)
    tts.save(directory + '/script.mp3')

def get_prompt_response(prompt):
    """Generates a GPT Response"""
    completion = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0.8,
        max_tokens=1000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    response = completion.choices[0].text.strip()

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