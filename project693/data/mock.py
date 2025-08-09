import numpy as np
import pandas as pd

from scipy.optimize import minimize
from scipy.special import expit

from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource, LabelSet, Span
from bokeh.io import output_notebook
from bokeh.transform import dodge

import random
from mockdata import invasive_plants, non_invasive_plants

# number of total choices
total_round = 50
# assumed propability of invasive plant choice
invasive_probability = 65


data = pd.DataFrame({
    'winner': [],
    'loser': [],
    'RT': [],
    'invasive_winner': [],
    'invasive_loser': []
})

invasive_map = {}


for n in range(total_round):
    
    invasive_plant = random.choice(invasive_plants)
    non_invasive_plant = random.choice(non_invasive_plants)

    invasive_selection = random.choices([1, 0], weights=[invasive_probability, 100 - invasive_probability])[0]
    
    new_row = pd.DataFrame({
        'winner': [invasive_plant[0] if invasive_selection == 1 else non_invasive_plant[0]],
        'loser': [non_invasive_plant[0] if invasive_selection == 1 else invasive_plant[0]],
        'RT': [1],      # unweighted
        'invasive_winner': [invasive_selection],
        'invasive_loser': [1 - invasive_selection]
    })
    
    data = pd.concat([data, new_row], ignore_index=True)
    
    invasive_map.update({
        invasive_plant[0]: 1
    })
    
    invasive_map.update({
        non_invasive_plant[0]: 0
    })
    

print(data)

image_ids = sorted(set(data['winner']).union(set(data['loser'])))
id_to_idx = {img_id: idx for idx, img_id in enumerate(image_ids)}
idx_to_id = {idx: img_id for img_id, idx in id_to_idx.items()}

print(image_ids)

num_images = len(image_ids)
    
    # plant = random.choice(invasive_plants)
    # data['winner'].append(plant[0])
    # invasive_map.update({
    #     plant[0]: 1
    # })
    
    # plant = random.choice(non_invasive_plants)
    # plant['loser'].append(plant[0])
    # invasive_map.update({
    #     plant[0]: 0
    # })

# print(data['winner'])
# print(data['loser'])
# print(invasive_map)
# print(len(invasive_map))

def weighted_log_likelihood(betas, data):
    ll = 0.0
    for _, row in data.iterrows():
        # mapping image id to index
        i= id_to_idx[row['winner']]
        j = id_to_idx[row['loser']]
        # i, j = int(row['winner']), int(row['loser'])
        beta_i, beta_j = betas[i], betas[j]
        weight = row['RT']
        p = np.exp(beta_i) / (np.exp(beta_i) + np.exp(beta_j))
        ll += weight * np.log(p + 1e-9)
    return -ll

# optimization

betas_init = np.zeros(num_images)

def constraint(betas):
    return betas[-1]

result = minimize(
    fun=weighted_log_likelihood,
    x0=betas_init,
    args=(data,),
    constraints={'type': 'eq', 'fun': constraint},
    method='SLSQP'
)

beta_estimates = result.x

# print("Estimated Attractiveness Scores (β):")
# for i, beta in enumerate(beta_estimates):
#     img_id = idx_to_id[i]
#     print(f"Image {img_id} (Invasive={invasive_map[img_id]}): beta = {beta:.3f}")


# compare invasive vs. non-invasive
invasive_betas = [beta_estimates[id_to_idx[key]] for key, value in invasive_map.items() if value == 1]
non_invasive_betas = [beta_estimates[id_to_idx[key]] for key, value in invasive_map.items() if value == 0]

# print("\nMean beta (invasive):", np.mean(invasive_betas))
# print("\nMean beta (non-invasive):", np.mean(non_invasive_betas))



# Normalization of Betas
beta_min = beta_estimates.min()
beta_max = beta_estimates.max()

# Min-max scale to [0, 1]
beta_scaled_0_1 = (beta_estimates - beta_min) / (beta_max - beta_min)

# rescale to [-1, +1]
beta_normalized = beta_scaled_0_1 * 2 - 1

# print("Normalized Attractiveness Scores (β) [-1, +1]:")
# for i, beta in enumerate(beta_normalized):
#     img_id = idx_to_id[i]
#     print(f"Image {img_id} (Invasive={invasive_map[img_id]}): beta = {beta:.3f}")

# compare normalized invasive vs. non-invasive
normalized_invasive_betas = [beta_normalized[id_to_idx[key]] for key, value in invasive_map.items() if value == 1]
normalized_non_invasive_betas = [beta_normalized[id_to_idx[key]] for key, value in invasive_map.items() if value == 0]

# print("\nMean normalized beta (invasive):", np.mean(normalized_invasive_betas))
# print("\nMean normalized beta (non-invasive):", np.mean(normalized_non_invasive_betas))


# Calculate in percentage
wins = data['winner'].value_counts()
appearances = pd.concat([data['winner'], data['loser']]).value_counts()

win_percentages = (wins / appearances).fillna(0)

all_plants = {p[0]: p[1] for p in (invasive_plants + non_invasive_plants)}

plot_data = {
    'plant': [],
    'win_percentage': [],
    'bradley_terry_beta': [],
    'label_color': []
}


win_percentages_dict = win_percentages.to_dict()

for idx in range(num_images):
    plant_name = all_plants[idx_to_id[idx]]
    win_percentages = win_percentages_dict[idx_to_id[idx]]
    bradley_terry_beta = float(beta_normalized[idx])
    color = 'red' if invasive_map[idx_to_id[idx]] == 1 else 'green'
    
    plot_data['plant'].append(plant_name)
    plot_data['win_percentage'].append(win_percentages)
    plot_data['bradley_terry_beta'].append(bradley_terry_beta)
    plot_data['label_color'].append(color)


output_notebook()
source = ColumnDataSource(data=plot_data)

x_min = min(plot_data['win_percentage'])
x_max = max(plot_data['win_percentage']) + 0.5

p = figure(
    x_range=(x_min, x_max),
    title="Bradley-Terry beta vs. Win %",
    x_axis_label="Win percentage",
    y_axis_label="Bradley-Terry beta",
    height=600,
    sizing_mode="stretch_width"
)

# p.circle("win_percentage", "bradley_terry_beta", size=8, source=source, color="navy", alpha=0.6)

p.scatter("win_percentage", "bradley_terry_beta", size=8, marker="circle", source=source, color="navy", alpha=0.6)

labels = LabelSet(x="win_percentage", y="bradley_terry_beta", text="plant", level="glyph",
                  x_offset=5, y_offset=5, source=source, text_font_size="9pt", text_color="label_color")
p.add_layout(labels)

show(p)

# Histogram of Attractiveness Scores by Each Image
image_names = [all_plants[idx_to_id[idx]] for idx in range(len(beta_normalized))]
scores = beta_normalized

colors = [
    "red" if invasive_map[idx_to_id[idx]] == 1 else "green"
    for idx in range(len(beta_normalized))
]

source = ColumnDataSource(data=dict(
    names=image_names,
    score=scores,
    color=colors
))

p = figure(x_range=image_names, height=600, sizing_mode="stretch_width",
           title="Normalized Attractiveness Score per Plant",
           x_axis_label="Plant Name", y_axis_label="Score [-1, +1]",
           toolbar_location=None, tools="")

p.vbar(x="names", top="score", width=0.6, color="color", source=source)

p.xaxis.major_label_orientation = 0.785

show(p)
