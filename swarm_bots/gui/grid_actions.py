from PIL import Image
from swarm_bots.goal.goal_building import GoalBuilding

persistance = 255

def create_grid_from_file(file):
    a = Image.open(file)
    pix = a.load()
    converted_image = ""
    for j in range(a.size[1]):
        for i in range(a.size[0]):
            if pix[i, j] == (0, 0, 0, persistance):
                converted_image += "0"
            elif pix[i, j] == (255, 255, 255, persistance):
                converted_image += "1"
        converted_image += "\n"
    return converted_image


# def calculate_procentage_difference()
