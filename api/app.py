from auth_token import auth_token
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
import torch
from torch import autocast
from diffusers import StableDiffusionPipeline
from io import BytesIO
import base64 
import json
import random
from pydantic import BaseModel
from pathlib import Path

####################################################################################################################################################################################
#                                                                       uvicorn app:appli --reload                                                                                 #
####################################################################################################################################################################################

class AddToPlayerRequest(BaseModel):
    player: str
    img: str

appli = FastAPI()
appli.add_middleware(
    CORSMiddleware, 
    allow_credentials=True, 
    allow_origins=["*"], 
    allow_methods=["*"], 
    allow_headers=["*"]
)
device = "cuda"
model_id = "gsdf/Counterfeit-V2.5"
pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16, use_auth_token=auth_token)
pipe.to(device)

################################################################################################################################################################################
with open('prompt.json', 'r') as prompt_stable:
    list_prompt = json.load(prompt_stable)

with open('models.json', 'r') as models_stable:
    list_models = json.load(models_stable)

with open('count.json', 'r') as counter:
        countable = json.load(counter)

details = "(8k, RAW photo, best quality, cinematic, masterpiece:5, ultra-detailed, beautiful, detailed environment, amazing lighting,  cinematic lighting, high quality, highly detailed, RTX )"
negative = "(mark, text, EasyNegative, paintings, sketches, (worst quality:2), (low quality:2), (normal quality:2), lowres, (monochrome), (grayscale), skin spots, acnes, skin blemishes, age spot, glans,extra fingers,fewer fingers,strange fingers,bad hand,signature, watermark, username, blurry, bad feet,bad leg, duplicate, extra limb, ugly, disgusting, poorly drawn hands, missing limb, floating limbs, disconnected limbs, malformed hands, blurry,mutated hands and fingers, EasyNegative, paintings, sketches, (worst quality:2), (low quality:2), (normal quality:2), lowres, (monochrome), (grayscale), skin spots, acnes, skin blemishes, age spot, glans,extra fingers,fewer fingers,strange fingers,bad hand,bad nails,signature, watermark, username, blurry, bad feet,bad leg)"

################################################################################################################################################################################
@appli.get("/generate/")
def generate(): 
    global prompt
    prompt = generate_prompt()
    random_models = random.randint(0, len(list_models))

    with autocast(device): 
        global pipe
        pipe = StableDiffusionPipeline.from_pretrained(list_models["models"][random_models], torch_dtype=torch.float16, use_auth_token=auth_token)
        pipe.to(device)
        image = pipe(prompt+details, guidance_scale=8.5,num_inference_steps=100,negative_prompt=negative, height=768, width=512).images[0]
        
    """Gestion des images"""
    image.save('../img/image_'+get_count()+'.png')
    increment_count()

    buffer = BytesIO()
    image.save(buffer, format="PNG") 
    imgstr = base64.b64encode(buffer.getvalue()) 

    return Response(content=imgstr, media_type="image/png")


def increment_count():
    global countable
    countable["count"] += 1
    with open('count.json', 'w') as counter:
        json.dump(countable, counter, indent=2)

def get_count():
    with open('count.json', 'r') as counter:
        countable = json.load(counter)
    return str(countable["count"])

def get_count_save():
    return int(get_count())-1

def generate_prompt():
    """ Génére une race aléatoire """
    random_race = random.randint(0, len(list_prompt["race"]))
    prompt_race = list_prompt["race"][random_race]

    """ Génére un sexe aléatoire """
    random_sex = random.randint(0, len(list_prompt["sex"]))
    try:
        prompt_sex = list_prompt["sex"][random_sex]
    except:
        prompt_sex = list_prompt["sex"][1]

    """ Génére une actions aléatoire """
    random_actions = random.randint(0, len(list_prompt["actions"]))
    prompt_actions = list_prompt["actions"][random_actions]

    """ Génére un environments aléatoire """
    random_environments = random.randint(0, len(list_prompt["environments"]))
    prompt_environments = list_prompt["environments"][random_environments]

    return "A "+prompt_sex+" "+prompt_race+" is "+prompt_actions+" in a "+prompt_environments+"."




########################################################################################################################################################################
#                                                                               Gestion des images                                                                     #
########################################################################################################################################################################


@appli.post('/addToPlayer/')
def addToPlayer(request: AddToPlayerRequest):
    image_path = save_image(request.img)  # Fonction à définir pour sauvegarder l'image et renvoyer le chemin
    add_image_to_player(request.player, image_path)
    return {"image_path": image_path}
    
def save_image(img_base64: str) -> str:
    
    # Fonction pour sauvegarder l'image et renvoyer le chemin d'accès
    # Assurez-vous de définir un chemin de stockage approprié
    image_folder = Path("../img/")
    image_path = image_folder / f"image_{get_count_save()}.png"
    
    with open(image_path, "wb") as image_file:
        image_file.write(base64.b64decode(img_base64))
    
    return str(image_path)

def add_image_to_player(player: str, image_path: str):
    # Fonction pour ajouter le chemin d'accès de l'image au joueur
    with open('players.json', 'r+') as fichier_json:
        players = json.load(fichier_json)
        if player not in players["players"]:
            players["players"][player] = []
        if image_path not in players["players"][player]:
            players["players"][player].append(image_path)
        fichier_json.seek(0)
        json.dump(players, fichier_json, indent=4)



###########################################################################################################################################################################
#                                                                               Gestion des joueurs                                                                       #
###########################################################################################################################################################################

@appli.get('/addPlayer/')
def addPlayer(player : str):
    with open('players.json', 'r+') as fichier_json:
        players = json.load(fichier_json)
        if (players["players"][player])==False:
            players["players"][player]=[]
            fichier_json.seek(0)
            json.dump(players, fichier_json, indent=2)
        else:
            print("Player already added")

@appli.get('/getListPersonnages/')
def getListPersonnages(player : str):
    with open('players.json', 'r') as fichier_json:
        players = json.load(fichier_json)   
    return players["players"][players]