from pydantic import BaseModel
from cat.experimental.form import form, CatForm
from typing import List, Optional
from enum import Enum
from cat.mad_hatter.decorators import tool, hook, plugin
from cat.log import log
import os
import datetime
from enum import Enum
from PIL import Image
import base64
from io import BytesIO

team_cat_dir = "/app/cat/data/coachcat"

class TimeUnit(Enum):
    energyintensive = 'energy intensive'
    energylow = 'energy low'

class InfoTeam(BaseModel):
    team_name: str
    num_player: int
    player_age: int
    player_sex: str
    training_intesity: TimeUnit
    focus_training: List[str] 
    training_duration: str
    

@form
class TeamTrainingForm(CatForm):
    description = "Team Training"
    model_class = InfoTeam
    start_examples = [
        "begin basketball training",
        "start basketball training"
    ]
    stop_examples = [
        "end basketball training",
        "finish basketball training"
    ]
    ask_confirm = True

    def submit(self, form_data):
        team_name = form_data.get('team_name', 'Unknown')
        team_dir = os.path.join(team_cat_dir, team_name)
        if not os.path.exists(team_dir):
            os.makedirs(team_dir)

        team_file = os.path.join(team_dir, f"{team_name}.txt")
        with open(team_file, 'w') as file:
            for key, value in form_data.items():
                file.write(f"{key}: {value}\n")
        return {
            "output": f"Team Training information for {team_name} saved to {team_file} <br><br> Type: <b>@infoteam {team_name}</b> to get team training information<br> Type: <b>@training {team_name}</b> to get basketball training plan<br><br><b>Disclaimer:</b> This software is exclusively intended for use by basketball coach; furthermore, please note that information provided by AI may not be 100% accurate and should be cross-referenced with basketball coach."
        }
    
def read_team_info(p_file_name):
    try:
        with open(p_file_name, 'r') as file:
            content = file.read()
            return content
    except FileNotFoundError:
        return None
        
def save_file_with_team_name(team_name, content, descriptor):
    team_dir = os.path.join(team_cat_dir, team_name)
    try:
        if not os.path.exists(team_dir):
            os.makedirs(team_dir)

        file_path = os.path.join(team_dir, f"{team_name}_{descriptor}.txt")
        with open(file_path, 'w') as file:
            file.write(content)
        return True, file_path  # Indicate success and return the file path
    except Exception as e:
        return False, str(e)  # Indicate failure and return the error message
        

def get_last_updated_time(file_path):
    try:
        # Get the last modified time in seconds since the epoch
        last_modified_time = os.path.getmtime(file_path)
        
        # Convert the time to a datetime object
        last_updated_time = datetime.datetime.fromtimestamp(last_modified_time)
        
        # Format the datetime object as a string
        return last_updated_time.strftime('%Y-%m-%d %H:%M:%S')
    
    except Exception:
        # Return an empty string in case of an exception
        return ''
    

@hook
def agent_fast_reply(fast_reply, cat):
    return_direct = True

    # Get user message from the working memory
    message = cat.working_memory["user_message_json"]["text"]

    if message.startswith('@training'):
        # Extract training's name from the message
        team_name = message[len('@training'):].strip()
        team_dir = os.path.join(team_cat_dir, team_name)

        # Construct filename based on patient's name
        team_file = os.path.join(team_dir, f"{team_name}.txt")

        content = read_team_info(team_file)
        if content is None:
            return {"output": f"Training file not found for {team_name}"}
        team_info = f"<b>Team information:</b> \n {content}"
        cat.send_ws_message(content=f'Creating training... ', msg_type='chat_token')
        llm_training = cat.llm(f"What are the most probable training based on team information: {content}")
        cat.send_ws_message(content=f'Creating team training plan ... ', msg_type='chat_token')
        llm_training_plan = cat.llm(f"Creating a basketball training plan for the duration of training: {llm_training}")
        
        
        save_file_with_team_name(team_name, llm_training + "\n\n<br>\n" + llm_training_plan + "\n\n", 'training_plan')
        
        result = {
            "output": f"{team_info} \n<br><br> {llm_training} \n<br><br> {llm_training_plan}"
        }
        return result
    
    if message.startswith('@infoteam'):
        # Extract patient's name from the message
        team_name = message[len('@infoteam'):].strip()
        team_dir = os.path.join(team_cat_dir, team_name)

        # Construct filename based on patient's name
        team_file = os.path.join(team_dir, f"{team_name}.txt")
        
        content = read_team_info(team_file)
        if content is None:
            return {"output": f"Training file not found for {team_name}"}
        else:
            content_updated_time = get_last_updated_time(team_file)

        team_info = f"<b>Team information:</b> <br><br> {content} <br> <small>Last updated: {content_updated_time}</small>"

        team_training_plan = read_team_info(os.path.join(team_dir, f'{team_name}_training_plan.txt'))
        if team_training_plan is None:
            team_training_plan = "<li>Training plan not found"
        else:
            team_training_plan = f"{team_training_plan} <br> <small>Last updated: {get_last_updated_time(os.path.join(team_dir, f'{team_name}_differantial_training_plan.txt'))}</small>"
        result = {
            "output": f"{team_info}<br><br>{team_training_plan}<br><br>Type: <b>@training {team_name}</b> to get basketball training plan for {team_name}<br><br><b>Disclaimer:</b> This software is exclusively intended for use by basketball coach; furthermore, please note that information provided by AI may not be 100% accurate and should be cross-referenced with basketball coach."
        }
        return result
    
    if message.startswith('@coachcat'):
        # Output to the user the list of the commands of the plugin
        return {
            "output": f"Begin by initiating the basketball training examination process. You can start by typing phrases like <b>begin basketball training</b> or <b>start basketball training.</b><br>You can end the examination process by typing phrases like <b>end basketball training</b> or <b>finish basketball training.</b><br><br>Team Training information for {team_name} saved to {team_file} <br><br> Type: <b>@infoteam {team_name}</b> to get team information<br>Type: <b>@training {team_name}</b> to get basketball training plan<br><br><b>Disclaimer:</b> This software is exclusively intended for use by basketball coach; furthermore, please note that information provided by AI may not be 100% accurate and should be cross-referenced with basketball coach."
        }

    return None