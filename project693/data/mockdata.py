import pandas as pd

import random

"""
These are mock data for testing only.
"""


# number of total choices
total_round = 50
# assumed propability of invasive plant choice
invasive_probability = 65


dall_e_2_images_variations = [
    [1, "Akebia quinata", "Akebia quinata Weed.png",
        "Akebia quinata Weed 1.png", "Akebia quinata Weed 2.png"],
    [2, "Aristea ecklonii", "Aristea ecklonii Weed.png",
        "Aristea ecklonii Weed 1.png", "Aristea ecklonii Weed 2.png"],
    [3, "Berberis darwinii", "Berberis darwinii Weed.png",
        "Berberis darwinii Weed 1.png", "Berberis darwinii Weed 2.png"],
    [4, "Bomarea multiflora", "Bomarea multiflora Weed.png",
        "Bomarea multiflora Weed 1.png", "Bomarea multiflora Weed 2.png"],
    [5, "Buddleja davidii", "Buddleja davidii Weed.png",
        "Buddleja davidii Weed 1.png", "Buddleja davidii Weed 2.png"],
    [6, "Cardiospermum grandiflorum", "Cardiospermum grandiflorum Weed.png",
        "Cardiospermum grandiflorum Weed 1.png", "Cardiospermum grandiflorum Weed 2.png"],
    [7, "Catanospermum_australe", "Catanospermum_australe_Weed.png",
        "Catanospermum_australe_Weed 1.png", "Catanospermum_australe_Weed 2.png"],
    [8, "Cestrum parqui", "Cestrum parqui Weed.png",
        "Cestrum parqui Weed 1.png", "Cestrum parqui Weed 2.png"],
    [9, "Cytisus scoparius", "Cytisus scoparius Weed.png",
        "Cytisus scoparius Weed 1.png", "Cytisus scoparius Weed 2.png"],
    [10, "Erica cinerea", "Erica cinerea Weed.png",
        "Erica cinerea Weed 1.png", "Erica cinerea Weed 2.png"],
    [11, "Fuchisia boliviana", "Fuchisia boliviana Weed.png",
        "Fuchisia boliviana Weed 1.png", "Fuchisia boliviana Weed 2.png"],
    [12, "Ipomoea indica", "Ipomoea indica Weed.png",
        "Ipomoea indica Weed 1.png", "Ipomoea indica Weed 2.png"],
    [13, "Kennedia rubicunda", "Kennedia rubicunda Weed.png",
        "Kennedia rubicunda Weed 1.png", "Kennedia rubicunda Weed 2.png"],
    [14, "Lamium galeobdolon", "Lamium galeobdolon Weed.png",
        "Lamium galeobdolon Weed 1.png", "Lamium galeobdolon Weed 2.png"],
    [15, "Passiflora caerulea", "Passiflora caerulea Weed.png",
        "Passiflora caerulea Weed 1.png", "Passiflora caerulea Weed 2.png"],
    [16, "Sagittaria platyphylla", "Sagittaria platyphylla Weed.png",
        "Sagittaria platyphylla Weed 1.png", "Sagittaria platyphylla Weed 2.png"],
    [17, "Senecio angulatus", "Senecio angulatus Weed.png",
        "Senecio angulatus Weed 1.png", "Senecio angulatus Weed 2.png"],
    [18, "Tropaeolum speciosum", "Tropaeolum speciosum Weed.png",
        "Tropaeolum speciosum Weed 1.png", "Tropaeolum speciosum Weed 2.png"],
    [19, "Vincetoxicum nigrum", "Vincetoxicum nigrum Weed.png",
        "Vincetoxicum nigrum Weed 1.png", "Vincetoxicum nigrum Weed 2.png"],
    [20, "Zantedeschia aethiopica", "Zantedeschia aethiopica Weed.png",
        "Zantedeschia aethiopica Weed 1.png", "Zantedeschia aethiopica Weed 2.png"],
]


invasive_plants = [
    (0, "Akebia quinata"),
    (1, "Aluminium Plant"),
    (2, "Aristea ecklonii"),
    (3, "Berberis darwinii"),
    (4, "Bomarea"),
    (5, "Bomarea multiflora"),
    (6, "Buddleja davidii"),
    (7, "Cardiospermum grandiflorum"),
    (8, "Catanospermum australe"),
    (9, "Cestrum parqui"),
    (10, "Clematis Vitalba"),
    (11, "Cytisus scoparius"),
    (12, "English Ivy"),
    (13, "Erica cinerea"),
    (14, "Flame Creeper"),
    (15, "Fuchisia boliviana"),
    (16, "Heather"),
    (17, "Ipomoea indica"),
    (18, "Japanese Honeysuckle"),
    (19, "Kennedia rubicunda"),
    (20, "Lamium galeobdolon"),
    (21, "Mexican Daisy"),
    (22, "Montbretia"),
    (23, "Passiflora caerulea"),
    (24, "Periwinkle"),
    (25, "Pigs Ear"),
    (26, "Russell Lupin"),
    (27, "Sagittaria platyphylla"),
    (28, "Senecio angulatus"),
    (29, "Stinking Iris"),
    (30, "Tradescantia"),
    (31, "Tropaeolum speciosum"),
    (32, "Tutsan"),
    (33, "Vincetoxicum nigrum"),
    (34, "Zantedeschia aethiopica")
]

non_invasive_plants = [
    (35, "Bush Lily"),
    (36, "Clematis Henryii"),
    (37, "Creeping Pohuehue"),
    (38, "Daphne"),
    (39, "Hosta Hybrid"),
    (40, "Ice Plant"),
    (41, "Kingfisher Daisy"),
    (42, "Koromiko"),
    (43, "NZ Blueberry"),
    (44, "NZ Iris"),
    (45, "Oxford Blue"),
    (46, "Scarlet Rata"),
    (47, "Star Jasmine"),
    (48, "Sulphurea"),
    (49, "White Clematis")
]

invasive_map = {}

# generate mock data
"""
data = pd.DataFrame({
    'winner': [],
    'loser': [],
    'RT': [],
    'invasive_winner': [],
    'invasive_loser': []
})

for n in range(total_round):

    invasive_plant = random.choice(invasive_plants)
    non_invasive_plant = random.choice(non_invasive_plants)

    invasive_selection = random.choices(
        [1, 0], weights=[invasive_probability, 100 - invasive_probability])[0]

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
"""

survey_data = [
    [39.0, 17.0, 1.0, 0.0, 1.0],
    [35.0, 25.0, 1.0, 0.0, 1.0],
    [42.0, 3.0, 1.0, 0.0, 1.0],
    [42.0, 1.0, 1.0, 0.0, 1.0],
    [24.0, 37.0, 1.0, 1.0, 0.0],
    [6.0, 40.0, 1.0, 1.0, 0.0],
    [6.0, 49.0, 1.0, 1.0, 0.0],
    [45.0, 17.0, 1.0, 0.0, 1.0],
    [4.0, 48.0, 1.0, 1.0, 0.0],
    [36.0, 34.0, 1.0, 0.0, 1.0],
    [30.0, 47.0, 1.0, 1.0, 0.0],
    [45.0, 2.0, 1.0, 0.0, 1.0],
    [34.0, 40.0, 1.0, 1.0, 0.0],
    [19.0, 38.0, 1.0, 1.0, 0.0],
    [21.0, 37.0, 1.0, 1.0, 0.0],
    [10.0, 40.0, 1.0, 1.0, 0.0],
    [43.0, 4.0, 1.0, 0.0, 1.0],
    [28.0, 39.0, 1.0, 1.0, 0.0],
    [37.0, 18.0, 1.0, 0.0, 1.0],
    [47.0, 33.0, 1.0, 0.0, 1.0],
    [0.0, 41.0, 1.0, 1.0, 0.0],
    [6.0, 45.0, 1.0, 1.0, 0.0],
    [29.0, 44.0, 1.0, 1.0, 0.0], 
    [30.0, 40.0, 1.0, 1.0, 0.0], 
    [30.0, 42.0, 1.0, 1.0, 0.0], 
    [26.0, 40.0, 1.0, 1.0, 0.0], 
    [13.0, 47.0, 1.0, 1.0, 0.0], 
    [42.0, 4.0, 1.0, 0.0, 1.0], 
    [39.0, 25.0, 1.0, 0.0, 1.0], 
    [14.0, 44.0, 1.0, 1.0, 0.0], 
    [47.0, 3.0, 1.0, 0.0, 1.0], 
    [19.0, 42.0, 1.0, 1.0, 0.0], 
    [2.0, 47.0, 1.0, 1.0, 0.0], 
    [21.0, 44.0, 1.0, 1.0, 0.0], 
    [48.0, 33.0, 1.0, 0.0, 1.0], 
    [41.0, 13.0, 1.0, 0.0, 1.0], 
    [8.0, 35.0, 1.0, 1.0, 0.0], 
    [43.0, 5.0, 1.0, 0.0, 1.0], 
    [7.0, 37.0, 1.0, 1.0, 0.0], 
    [11.0, 43.0, 1.0, 1.0, 0.0], 
    [42.0, 25.0, 1.0, 0.0, 1.0], 
    [27.0, 42.0, 1.0, 1.0, 0.0], 
    [16.0, 46.0, 1.0, 1.0, 0.0], 
    [49.0, 24.0, 1.0, 0.0, 1.0], 
    [37.0, 23.0, 1.0, 0.0, 1.0], 
    [43.0, 5.0, 1.0, 0.0, 1.0], 
    [32.0, 36.0, 1.0, 1.0, 0.0], 
    [8.0, 39.0, 1.0, 1.0, 0.0], 
    [45.0, 6.0, 1.0, 0.0, 1.0], 
    [4.0, 41.0, 1.0, 1.0, 0.0]
]

data = pd.DataFrame(survey_data, columns=['winner', 'loser', 'RT', 'invasive_winner', 'invasive_loser'])

for index, row in data.iterrows():
    winner = int(row['winner'])
    loser = int(row['loser'])
    invasive_map.update({
        winner: 1 if winner <= 34 else 0
    })
    invasive_map.update({
        loser: 1 if loser <= 34 else 0
    })
