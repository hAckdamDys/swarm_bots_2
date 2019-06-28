from PIL import Image
from difflib import SequenceMatcher

from swarm_bots.goal.goal_building_2d import GoalBuilding2D

persistance = 255

def create_grid_from_file(file):
    a = Image.open(file)
    pix = a.load()
    converted_image = """"""
    converted_image += "\n            "
    for j in range(a.size[1]):
        for i in range(a.size[0]):
            if pix[i, j] != (255, 255, 255, 255):
                converted_image += "1"
            # elif pix[i, j] == (255, 255, 255, persistance):
            else:
                converted_image += "0"
            if a.size[0]-i > 1:
                converted_image += " "
        converted_image += "\n            "
    return GoalBuilding2D(converted_image)



def calculate_procentage_difference(goal_grid, result_grid):
    return str(SequenceMatcher(None, str(goal_grid), str(result_grid)).ratio()*100)+'%'
