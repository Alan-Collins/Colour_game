import pygame, time, random, math, copy
from random import shuffle
from colormath.color_objects import LabColor, XYZColor, sRGBColor
from colormath.color_conversions import convert_color

# Tested with python3.9, pygame-2.0.1, and colormath-3.0.0


#### SET GAME PARAMETERS HERE ######
"""
Controls:
Click to start.
Click a square to select it (indicated by highlight). Click again to swap it with another square.
If you need a hint press the S key to show the solution.
If you want to start again press the R key to reset.
"""

difficulty = 15 # Lower is harder. Sets minimum difference between adjacent colours.
# Range 1 to 100. Impossible: 5; Hard: 10; Medium: 15; Easy: 20 for an 8X8
# Takes longer to find colours for very high or very low (<5) values and for larger grids
# may not work if difficulty much over 20 for grids larger than 6 or so.
# (Couldn't do 40 for a 6x6 in my tests)

wid, hi = 8, 8 # Set size of grid (number of squares wide/high)




#### VISUAL SETTINGS #####

block_width, block_height = 80, 80 # Set square width and height in pixels

block_margin = 5 # Set margin around squares in pixels

highlight = (240, 77, 57) # Set colour of highlight when square is selected





def generate_random_colours(ncolours, gridsize):
    colour_list = [(random.randint(0,100),random.randint(-128,128),random.randint(-128,128))]
    for i in range(1, ncolours):
        acceptable = False
        while not acceptable:
            new_colour = (random.randint(0,100),random.randint(-128,128),random.randint(-128,128))
            distances = []
            for i in colour_list:
                distances.append(math.sqrt(((i[0]-new_colour[0])**2)+((i[1]-new_colour[1])**2)+((i[2]-new_colour[2])**2)))
            if all(x >= 3*gridsize for x in distances):
                acceptable = True
        colour_list.append(new_colour)
    return colour_list


def calc_distances(colours):
    distances = []
    for i in range(len(colours)):
        distances.append([])
        for j in range(len(colours)):
            if i != j:
                a = colours[i]
                b = colours[j]
                distances[i].append(int(math.sqrt(((a[0]-b[0])**2)+((a[1]-b[1])**2)+((a[2]-b[2])**2))))
    return distances
            
def get_col_steps(start, stop, steps):
    asteps = (stop[0] - start[0]) / (steps-1)
    bsteps = (stop[1] - start[1]) / (steps-1)
    csteps = (stop[2] - start[2]) / (steps-1)
    return asteps, bsteps, csteps

def create_col_gradients(top_left, top_right, bottom_left, bottom_right, h_steps, v_steps):
    top_row_rsteps, top_row_gsteps, top_row_bsteps = get_col_steps(top_left, top_right, h_steps)
    top_row = []

    first_col_rsteps, first_col_gsteps, first_col_bsteps = get_col_steps(top_left, bottom_left, v_steps)

    last_col_rsteps, last_col_gsteps, last_col_bsteps = get_col_steps(top_right, bottom_right, v_steps)

    array = []
    
    for i in range(v_steps):
        first_col = (top_left[0] + i*first_col_rsteps, top_left[1] + i*first_col_gsteps, top_left[2] + i*first_col_bsteps)
        last_col = (top_right[0] + i*last_col_rsteps, top_right[1] + i*last_col_gsteps, top_right[2] + i*last_col_bsteps)
        line = []
        for i in range(h_steps):
            line_rsteps, line_gsteps, line_bsteps = get_col_steps(first_col, last_col, h_steps)
            array.append((first_col[0] + i*line_rsteps, first_col[1] + i*line_gsteps, first_col[2] + i*line_bsteps))

    return array

def convert_array_colours(array, source_colour, target_colour):
    for i in range(len(array)):
        new_colour = convert_color(source_colour(array[i][0], array[i][1], array[i][2]), target_colour)#.get_value_tuple()
        r = int(255 * new_colour.clamped_rgb_r)
        g = int(255 * new_colour.clamped_rgb_g)
        b = int(255 * new_colour.clamped_rgb_b)
        new_colour = (r,g,b)
        array[i] = new_colour

    return array
    

def swap_positions(listoflists, coord1, coord2): 
      
    listoflists[coord1[0]][coord1[1]], listoflists[coord2[0]][coord2[1]] = listoflists[coord2[0]][coord2[1]], listoflists[coord1[0]][coord1[1]] 
    return listoflists





gen_colours = generate_random_colours(4, wid)

tl = gen_colours[0]
tr = gen_colours[1]
bl = gen_colours[2]
br = gen_colours[3]
highlight = (240, 77, 57)

colours = create_col_gradients(tl, tr, bl, br, wid, hi)

# Make sure all the colours are sufficiently distinct or else remake the colours

dists = calc_distances(colours)


# Make sure the lab colourspace difference between adjacent cells is at least the difficulty value, but not more than 2* that value.
while not all([i > difficulty  for j in dists for i in j]) or not all([i < difficulty*2*max([wid,hi])  for j in dists for i in j]):
    gen_colours = generate_random_colours(4, max(wid, hi))

    tl = gen_colours[0]
    tr = gen_colours[1]
    bl = gen_colours[2]
    br = gen_colours[3]

    colours = create_col_gradients(tl, tr, bl, br, wid, hi)

    dists = calc_distances(colours)


colours = convert_array_colours(colours, LabColor, sRGBColor)

col_array =[]

for i in range(0, wid*hi, wid):
    col_array.append(colours[i:i+wid])

shuff_colours = list(colours)


for i in [(wid*hi)-1, (wid*hi)-wid, wid -1, 0]:
    del shuff_colours[i]



shuffle(shuff_colours)

for i in [0, wid-1, (wid*hi)-wid, (wid*hi)-1]:
    shuff_colours.insert(i, colours[i])

shuff_col_array =[]

for i in range(0, wid*hi, wid):
    shuff_col_array.append(shuff_colours[i:i+wid])

orig_shuff_col_array = copy.deepcopy(shuff_col_array)

white = (255,255,255)
black = (0, 0, 0)

pygame.init()




display_width, display_height = (block_width*wid)+(block_margin*(wid+1)), (block_width*hi)+(block_margin*(hi+1))

gameDisplay = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption('Colour_game')
clock = pygame.time.Clock()

esc_game = False
show_finished = True
stored_coord = False
success = False
moves = 0
printed_message = False

while not esc_game:
    if show_finished:
        gameDisplay.fill(white)
        for row in range(len(col_array)):
            for column in range(len(col_array[row])):
                colour = col_array[row][column]
                pygame.draw.rect(gameDisplay, colour,
                                [(block_margin + block_width) * column + block_margin,
                                (block_margin + block_height) * row + block_margin,
                                block_width, block_height])

        pygame.display.update()
    else:
        if not success:
            if not stored_coord:
                gameDisplay.fill(white)
                for row in range(len(shuff_col_array)):
                    for column in range(len(shuff_col_array[row])):
                        colour = shuff_col_array[row][column]
                        pygame.draw.rect(gameDisplay, colour,
                                        [(block_margin + block_width) * column + block_margin,
                                        (block_margin + block_height) * row + block_margin,
                                        block_width, block_height])
            else:
                for row in range(len(shuff_col_array)):
                    for column in range(len(shuff_col_array[row])):
                        if row == coord1[0] and column == coord1[1]:
                            pygame.draw.rect(gameDisplay, highlight,
                                            [(block_margin + block_width) * column,
                                            (block_margin + block_height) * row,
                                            (block_width + (2 * block_margin)), (block_height + (2 * block_margin))])
                        colour = shuff_col_array[row][column]
                        pygame.draw.rect(gameDisplay, colour,
                                        [(block_margin + block_width) * column + block_margin,
                                        (block_margin + block_height) * row + block_margin,
                                        block_width, block_height])
                

            pygame.display.update()

        else:
            if not printed_message:
                print("Good job! It only took you %i moves to finish!" % moves)
                printed_message = True
            
            gameDisplay.fill(black)
            for row in range(len(shuff_col_array)):
                for column in range(len(shuff_col_array[row])):
                    colour = shuff_col_array[row][column]
                    pygame.draw.rect(gameDisplay, colour,
                                    [(block_margin + block_width) * column + block_margin,
                                    (block_margin + block_height) * row + block_margin,
                                    block_width, block_height])
            pygame.display.update()
        
        
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            esc_game = True
        if event.type == pygame.KEYDOWN:
            if event.unicode == 's':
                if show_finished:
                    show_finished = False
                else:
                    show_finished = True
            if event.unicode == 'r':
                moves = 0
                print("Game reset!")
                shuff_col_array = copy.deepcopy(orig_shuff_col_array)
                
        if event.type == pygame.MOUSEBUTTONDOWN:
            if show_finished:
                show_finished = False
            else:
                if event.button == 1:
                    if not stored_coord:
                        stored_coord = True
                        coords = event.pos
                        col = coords[0]//(block_width+block_margin)
                        row = coords[1]//(block_height+block_margin)
##                        print("You clicked the square in row %i, column %i" %(row+1, col+1))
                        coord1 = (row, col)
                    else:
                        if event.pos != coords:
                            coords = event.pos
                            col = coords[0]//(block_width+block_margin)
                            row = coords[1]//(block_height+block_margin)
                            coord2 = (row, col)
                            shuff_col_array = swap_positions(shuff_col_array, coord1, coord2)
                            stored_coord = False
                            success = sorted(col_array) == sorted(shuff_col_array)
                            moves += 1
                        
                if event.button == 3:
                    stored_coord = False
                


    clock.tick(30)

pygame.quit()
