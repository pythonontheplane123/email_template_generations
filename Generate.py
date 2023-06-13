#Priority list

#describe your situation widget: done

#Images in the same section have to have different height and width and stuff, print out if h and w arent found: done
#Social media link icons are also being replaced:
#replacing the lorem ipsum dolor and stuff.
# find better templates
#error handling, images not found
#make logic fr the background for corner cases, if there are two then just remove one instead of removing the entire div
#If the size of some images are less than 50 and stuff, dont replace, delete.
# make sure you delete the lib




import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
import os
import random
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from bs4 import BeautifulSoup, Comment
import openai
import subprocess
import json
import unicodedata
from mangum import Mangum
from fastapi.responses import FileResponse

openai.api_key = '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'
os.environ["OPENAI_API_KEY"] = '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'

app = FastAPI()
#handler = Mangum(app)


origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:8080",
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost/",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)



def retrieve_data_format(path):
    with open(path, 'r') as f:
        soup = BeautifulSoup(f, 'lxml')

    blacklist = ['[document]', 'noscript', 'header', 'html', 'meta', 'head', 'input', 'script', 'style']

    tags = [tag for tag in soup.find_all(string=True) if tag.parent.name not in blacklist
            and not isinstance(tag, Comment) and tag.strip()]

    result = "".join(
        f'<{tag.parent.name} class="{ " ".join(tag.parent.get("class", [])) }">{tag.strip()}</{tag.parent.name}>'
        for tag in tags
    )

    return result, soup

def change_text_content(content, theme, context_of_user):
    completion = openai.ChatCompletion.create(
        model="gpt-4",
        temperature=0.5,
        max_tokens=2000,
        messages=[
            { "role": "user", "content":   f"Revise HTML content within tags to match the theme: {theme}. Consider this user story: {context_of_user}. Consider this the html context: {content}" }
        ]
    )
    return completion.choices[0].message.content

def replace_html_content(modified_representation, soup, html_file_path):
    soup_modified = BeautifulSoup(modified_representation, 'lxml')
    tags_modified = soup_modified.find_all()

    blacklist = ['[document]', 'noscript', 'header', 'html', 'meta', 'head', 'input', 'script', 'style']

    original_tags = [tag for tag in soup.find_all(string=True) if tag.parent.name not in blacklist
            and not isinstance(tag, Comment) and tag.strip()]

    if len(original_tags) != len(tags_modified):
        print("Mismatch in number of tags to replace, operation halted.")
        return

    for original_tag, new_tag in zip(original_tags, tags_modified):
        original_tag.replace_with(new_tag.string)

    with open(html_file_path, 'w') as f:
        f.write(str(soup.prettify()))
        f.close()

    print(f"New file saved as {html_file_path}")


#################ALL text before this line############################
####visual starts here
def remove_div_images(html_file_name):

    depth = 1
    # Get the absolute file path
    absolute_html_file_path = os.path.abspath(html_file_name)

    # Setup chrome options
    chrome_options = webdriver.ChromeOptions()

    # Start the WebDriver
    driver_service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=driver_service, options=chrome_options)

    # Open the HTML file in the browser, prepend the path with file://
    driver.get('file://' + absolute_html_file_path)

    # Sleep to allow images to load
    time.sleep(3)

    # First, remove any image if its render size width or height is less than 55px
    all_imgs = driver.find_elements(By.TAG_NAME, 'img')
    for img in all_imgs:
        width = img.size['width']
        height = img.size['height']
        # If either width or height is less than 55, remove the image
        if width < 55 or height < 55:
            driver.execute_script("""
            var element = arguments[0];
            element.parentNode.removeChild(element);
            """, img)

    # Find all the divs in the page
    divs = driver.find_elements(By.TAG_NAME, 'div')

    # Iterate over all divs
    for div in divs:
        # Find all child divs up to specified depth
        xpath_query = './/div' * depth
        child_divs = div.find_elements(By.XPATH, xpath_query)

        # Iterate over all child divs
        for child_div in child_divs:
            # Find all images of the div, including nested ones
            imgs = child_div.find_elements(By.XPATH, './/img')

            # If the div contains more than two images
            if len(imgs) > 2:
                sizes = set((img.size['width'], img.size['height']) for img in imgs)
                # If images do not have identical dimensions, remove the images
                if len(sizes) > 1:
                    for img in imgs:
                        driver.execute_script("""
                        var element = arguments[0];
                        element.parentNode.removeChild(element);
                        """, img)

    # Save the modified HTML to a new file without the file:// prefix
    with open(absolute_html_file_path, 'w') as file:
        file.write(driver.page_source)

    # Quit the browser
    driver.quit()


def find_email_template_template(directory_of_email_template_folder):
    # Get a list of all files in the directory
    files = os.listdir(directory_of_email_template_folder)

    # Randomly select a file
    random_file = random.choice(files)

    # Return the full path of the file
    return os.path.join(directory_of_email_template_folder, random_file)

def find_images(prompt, num_images):
    curl_url = 'curl -H "Authorization: tpYdnkkK4BXFoIgCPy7TZrOFazhAF4iUypjyUWPIxUuMXdO6TJAh7kfi" \"https://api.pexels.com/v1/search?query={}&per_page={}"'.format(prompt, num_images)
    status, data = subprocess.getstatusoutput(curl_url)

    start = data.find('{')
    end = data.rfind('}') + 1
    json_data = data[start:end]

    if not json_data:
        print(f"Warning: No data received for prompt: {prompt}")
        return None

    # Remove control characters
    json_data = ''.join(ch for ch in json_data if unicodedata.category(ch)[0] != "C")

    try:
        parsed_data = json.loads(json_data)
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON: {e}")
        return None

    # Iterate over each photo in the 'photos' list
    all_urls = []
    print(parsed_data['photos'])
    for photo in parsed_data['photos']:
        # Get the URL of the 'original' version of the photo
        url = photo['src']['original']
        all_urls.append(url)
        print(f"appending {url}")

    return random.shuffle(all_urls)

def replace_images_in_html(html_file_path, image_srcs,theme):
    with open(html_file_path, 'r',errors= 'ignore') as file:
        html_content = file.read()

    # Create a regex pattern for .jpg, .png, .jpeg, .gif, .svg image formats
    img_pattern = re.compile(r'src\s*=\s*"(.*?\.(?:jpg|jpeg|png|gif|svg))"')

    all_imgs = re.findall(img_pattern, html_content)

    # Log all found images
    print(f"All Images: {all_imgs}")
    print(all_imgs)
    for i, img in enumerate(all_imgs):
        # Make sure to not go out of bounds of the image_srcs list
        if i < len(image_srcs):
            html_content = html_content.replace(img, image_srcs[i])
        else:
            print(f"No replacement image for {img}. Skipping...")

    # Save the modified HTML to a new file
    path = theme+'.html'
    with open(path, 'w') as file:
        file.write(html_content)



url = find_email_template_template('/Users/macos/PycharmProjects/Botify/Email_template_generation/Templates')
print(url)


@app.get("/")
def read_root():
    return {"answer": "Hello World"}

@app.get("/predict")
def generate_email_templates(theme,user_story):
    email_template_template = find_email_template_template('Templates')
    print(email_template_template)
    theme_of_user = theme
    prompt = theme
    path = prompt+'.html'
    image_srcs = find_images(prompt, 20)
    replace_images_in_html(url, image_srcs,prompt)
    remove_div_images(prompt+'.html')
    html_read = open(path,'r')
    soup = BeautifulSoup(html_read, 'html.parser')
    final = soup.prettify("utf-8")
    return final


    """
    path = prompt+'.html'

    text_representation = retrieve_data_format(path)
    new_representation = change_text_content(text_representation,theme_of_user,user_story)

    print("Initial Text Representation:"+text_representation)

    print('\n')

    replace_html_content(new_representation,path)
    print("Final text representation:"+retreive_data_format(path))#modified website
    html_read = open(path,'r')
    soup = BeautifulSoup(html_read, 'html.parser')
    #final = soup.prettify("utf-8")

"""






