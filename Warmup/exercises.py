import sets
import csv
import matplotlib.pyplot as plt
import numpy as np

# Discard everything but plays.

# Could not recognize which are plays directly from looking at contents
#    - Thought that sonnets were only non-plays but no, looking from bottom
#    - Scanning, noticed titles (in CAPS) demarcated plays
#    - Use external sources to find 38 play titles, discard here

# Line by line. "in" or "not in" a play, which lets us know when to copy.
def keep_plays_only():
    in_copy = False

    with open('shakespeare.txt', 'r') as original:
        with open('s_plays_only.txt', 'w') as new:

            while True:
                line = original.readline()

                if not line: 
                    break

                if line.strip() in sets.all_works:
                    
                    if line.strip() in sets.plays_only:
                         in_copy = True
                    else:
                         in_copy = False

                if in_copy:
                     new.write(line)

# keep_plays_only()

# --------------------------------------------------------------------

# After you remove the poetry, how much is left, as a fraction of the original?
#   - Judged by # characters with wc in terminal
def frac_left():
    cleaned = 5080370
    original = 5575101

    print(f"Fraction left: {cleaned/original}")

frac_left()

# --------------------------------------------------------------------

# Create a list of the unique characters in the input file.
def get_unique_chars():

    unique = []

    with open("s_plays_only.txt", "r") as file:

        while True: 
            line = file.readline()

            if not line:
                break

            for i in line:
                if i not in unique:
                    unique.append(i)

    print(f"Unique characters in file: \n\n {unique}")

get_unique_chars()

# --------------------------------------------------------------------

# Approximately how many lines, words and characters did Shakespeare write in all?
#   - Using terminal commands: char (5080370), word (914262), line (188502)

# How many of those are blank lines (or alternatively, how many are non-blank)?

#   - Using grep -cE '^[[:space:]]*$'; 41193 blank
    
# --------------------------------------------------------------------

# How many plays are there in this file?
# Print the titles

def print_play_titles():
    print(f"There are {len(sets.plays_only)} plays in this file.")

    for play in sets.plays_only:
        print(play)

print_play_titles()
print()

# --------------------------------------------------------------------

# compute the number of acts
# compute the total number of scenes
# (ignore miscellany like prologs and epilogs)

# Trouble just using titles! Thought titles were distinct -- except 
# once. KING HENRY THE EIGHTH is a title and a character. :(\

# And thought that what's in contents is a title!
# KING RICHARD THE SECOND --> actually THE LIFE AND DEATH OF KING RICHARD THE SECOND

# Realized that in contents, can have other stuff like INDUCTION in 
# addition to ACTs. Track when under actual ACTs... found common 
# delimiter to be empty lines.

def act_and_scenes():

    count = {}
    master = {}
    # test = []

    with open("s_plays_only.txt", "r") as file:

        while True:
            line = file.readline()

            if not line:
                break

            cleaned = line.strip()

            if cleaned in sets.plays_only and cleaned not in count:

                # test.append(cleaned)
                num_acts = 0
                num_scenes = 0
                scenes = []
                is_act = False

                while True:
                    content_line = file.readline()
                    cl_content = content_line.strip()

                    if len(cl_content) == 0:
                        continue
                    if cl_content == "Dramatis Personæ":
                        scenes.append(num_scenes)

                        count[cleaned] = (num_acts, scenes)
                        break

                    if cl_content[:3] == "ACT":
                        is_act = True
                        num_acts += 1
                        if num_scenes != 0:
                            scenes.append(num_scenes)
                            num_scenes = 0
                    elif not cl_content:
                        is_act = False

                    # sometimes all caps, sometimes not!! 
                    # New approach converts all to lowercase.
                    if cl_content[:5].lower() == "scene" and is_act:
                        num_scenes += 1

    for play in count:

        assert len(count[play][1]) == 5

        print(f"{play} with {count[play][0]} acts with respective "
              f"number of scenes {count[play][1]}. {sum(count[play][1])} total.")
        
        # num acts, num scenes
        master[play] = [count[play][0], sum(count[play][1])]
        
    return master
    # print(len(test))
    # print(test)

# act_and_scenes()

# --------------------------------------------------------------------

# compute the approximate number of dramatis personae in each play

# No real structure to when list ends. Heuristic: number of lines 
# between dramatis personae and first line that includes "scene".
# Most plays have multiple characters on same line and blank lines.

def roles_per_play():
    with open("s_plays_only.txt", "r") as file:
        seen = []
        master = {}

        while True:
            line = file.readline()

            if not line:
                break

            line = line.strip()

            if line in sets.plays_only and line not in seen:
                num_actors = 0
                seen.append(line)

                while True:
                    next = file.readline().strip()
                    if next == "Dramatis Personæ":
                        break

                while True:
                    next = file.readline()
                    next = next.strip()
                    num_actors += 1

                    if "scene" in next.lower():
                        break
                
                print(f"Approx # dramatis personae in {line}: {num_actors}")
                master[line] = num_actors

    return master

# roles_per_play()

# --------------------------------------------------------------------

# Count the words

# Line by line, count up and report previous when hit new play.
def count_words():

    with open("s_plays_only.txt", "r") as file:
        
        seen = []
        master = {}

        # t_words = 0
        words = 0
        last_play = ""

        while True:
            line = file.readline()
            c_line = line.strip()

            if not line:
                print(f"# words in {last_play}: {words}")
                master[last_play] = words
                words = 0
                # print(t_words)
                break

            if c_line in sets.plays_only and c_line not in seen:
                
                if words != 0:
                    print(f"# words in {last_play}: {words}")
                    master[last_play] = words
                    words = 0

                last_play = c_line

                seen.append(c_line)

            words += len(c_line.split())
            # t_words += len(c_line.split())
    
    return master

# count_words()

# --------------------------------------------------------------------

# compute the names of all speakers in all plays
# and how many times each name appears

# Note that speaker format is name in all caps and following .
# grep -oE '^[A-Z][A-Z]+[.]$' s_plays_only.txt | sort | uniq -c | sort -nr

# --------------------------------------------------------------------

# Writing to Google Sheets. 4 columns: 

# title
# number of acts
# number of scenes
# number of personae

def construct_export():

    final = act_and_scenes()
    persona = roles_per_play()

    for play in persona:
        final[play].append(persona[play])

    # print(final)
        
    row_list = [["title", "num. acts", "num. scenes", "num. personae"]]

    for play in final:
        row_list.append([play, final[play][0], final[play][1], final[play][2]])

    with open('shakespeare_plays.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(row_list)

# construct_export()
        
# --------------------------------------------------------------------
        
# Plotting
        
def plot_by_word_count():

    words_data = count_words()
    sorted_words_data = sorted(words_data, key = words_data.get)
    
    plays = [play for play in sorted_words_data]
    y_pos = np.arange(len(plays))

    fig, ax = plt.subplots()

    word_count = []
    for play in plays:
        word_count.append(words_data[play])

    ax.barh(y_pos, word_count)
    ax.set_yticks(y_pos, labels = plays)
    plt.subplots_adjust(left=0.3)
    
    plt.show()


# --------------------------------------------------------------------
    
def line_and_chars():

    seen = []
    last_play = ""
    char_count = 0
    line_count = 0
    master = []

    with open("s_plays_only.txt", "r") as file:
        while True:

            line = file.readline()

            if not line:
                master.append((last_play, char_count, line_count))
                break

            c_line = line.strip()

            if c_line in sets.plays_only and c_line not in seen:

                if char_count != 0:
                    master.append((last_play, char_count, line_count))
                    char_count = 0
                    line_count = 0

                seen.append(c_line)
                last_play = c_line
            
            char_count += len(line)
            line_count += 1
    
    return master

def scatter_line_char():

    data = line_and_chars()

    play_name = [item[0] for item in data]
    chars = [item[1] for item in data]
    lines = [item[2] for item in data]

    fig, ax = plt.subplots()
    ax.scatter(chars, lines)

    for i, play in enumerate(play_name):
        ax.annotate(play, (chars[i], lines[i]))

    plt.show()

scatter_line_char()