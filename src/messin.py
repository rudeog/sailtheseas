import random

def distance(x1, y1, x2, y2):
    # Calculate the Euclidean distance between two points (x1, y1) and (x2, y2)
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

def get_random_location(cols,rows):
    return random.randint(0,cols-1), random.randint(0,rows-1)

# returns list of adjacent locations that are non-zero
# exclusive of the location in question
def get_all_adjacent(matrix,x,y):
    rows, cols = len(matrix), len(matrix[0])

    # for col in range(x-1, x+2):
    #     col = cols + col
    #     if col >= cols:
    #         col = cols - col



    xrange = [p for p in range(x-1, x+2) if 0 <= p < cols]
    yrange = [p for p in range(y-1, y+2) if 0 <= p < rows]
    adj=[]
    for row in yrange:
        for col in xrange:
            if matrix[row][col] > 0 and not (row == y and col == x):
                adj.append(matrix[row][col])
    return adj

# get random location not near another filled
MAX_TRIES=400
def get_validated_location(matrix):
    t = MAX_TRIES
    rows, cols = len(matrix), len(matrix[0])
    while t:
        x,y = get_random_location(cols,rows)
        if matrix[y][x]: # don't populate same one twice
            continue
        adj=get_all_adjacent(matrix,x,y)
        if len(adj) == 0:
            return (x,y)
        t=t-1
    raise Exception("failed to get validated location after all these tries!")







def populate_randomly(matrix, num_items):
    rows, cols = len(matrix), len(matrix[0])

    # start in the middle
    x = cols//2
    y = rows//2
    matrix[y][x]=1
    c = num_items-1
    while c:
        x,y = get_validated_location(matrix)
        matrix[y][x]=matrix[y][x]+1
        c=c-1

def disp(i):
    if i:
        return "#"
    return " "
# Example usage:
rows = 12
cols = 12
num_items = 26

random.seed(79)
# Create a 2D list with instances of class X
two_dimensional_list = [[int(0) for i in range(cols)] for j in range(rows)]

# Populate the 2D list with the specified density, scattering 1s as far from each other as possible
populate_randomly(two_dimensional_list, num_items)

# Display the result (printing the values for demonstration)
for row in two_dimensional_list:
    for item in row:
        print(f"{disp(item)}", end=' ')
    print()