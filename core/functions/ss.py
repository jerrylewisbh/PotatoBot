
from math import pi

# Libraries
import matplotlib.pyplot as plt
import pandas as pd


my_class = """11: Aiming
11: Bow Mastery
11: Perceptive Seeker
10: Tight Grip
10: Accuracy
5: Weapon Mastery
5: Enlightened Warrior
5: Prudent Duelist
4: Light Armor Mastery
3: Power Napping
3: Rare Mutation
3: Hawkeye
2: Armor Mastery"""


classes = [my_class, my_class]


my_skills = dict()

max_value = -1

strings = my_class.splitlines()
# print(strings)
for string in strings[2:]:
    skill_name = string.split(": ")[1]
    skill_value = int(string.split(": ")[0])
    my_skills[skill_name] = [skill_value, 0, 0]


for class_data in classes:
    strings = class_data.splitlines()
    for string in strings:
        skill_name = string.split(": ")[1]
        skill_value = int(string.split(": ")[0])
        if skill_name not in my_skills:
            continue
        my_skills[skill_name][1] += skill_value
        max_value = max(max_value, skill_value)
        my_skills[skill_name][2] += 1


for skill in my_skills:
    my_skills[skill][1] /= my_skills[skill][2]
    my_skills[skill].pop()


# Set data
df = pd.DataFrame(my_skills)


# ------- PART 1: Create background

# number of variable
categories = list(df)[1:]
N = len(categories)

# What will be the angle of each axis in the plot? (we divide the plot / number of variable)
angles = [n / float(N) * 2 * pi for n in range(N)]
angles += angles[:1]

# Initialise the spider plot
ax = plt.subplot(111, polar=True)

# If you want the first axis to be on top:
ax.set_theta_offset(pi / 2)
ax.set_theta_direction(-1)

# Draw one axe per variable + add labels labels yet
plt.xticks(angles[:-1], categories)

# Draw ylabels
ax.set_rlabel_position(0)
plt.yticks(range(max_value), [str(i) for i in range(max_value)], color="grey", size=7)
plt.ylim(0, max_value + 1)


# ------- PART 2: Add plots

# Plot each individual = each line of the data
# I don't do a loop, because plotting more than 3 groups makes the chart unreadable

# Ind1
values = df.loc[0].values.flatten().tolist()

ax.plot(angles, values, linewidth=1, linestyle='solid', label="You")
ax.fill(angles, values, 'b', alpha=0.1)

# Ind2
values = df.loc[1].values.flatten().tolist()
ax.plot(angles, values, linewidth=1, linestyle='solid', label="Castle")
ax.fill(angles, values, 'r', alpha=0.1)

# Add legend
plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
plt.savefig("teste.png")
