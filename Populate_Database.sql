SET FOREIGN_KEY_CHECKS = 0;


truncate table plants;
truncate table users;


INSERT INTO `users` (id, username, password_hash, email, first_name, last_name, location, description, avatar, role, status) VALUES
(1, 'siteadmin1', 'f8b0c38da5bcf5e7913b51e51a6e7e009c84110f377f0a0f1e178cd99e1bfe2a', 'siteadmin1@example.com', 'John', 'Doe', '{"lat": -45.9, "lon": 170.4}', NULL, 'default.png', 'siteadmin', 'active'),
(2, 'siteadmin2', '96bd7a2f308098c2e52d1cc3c9e5406f914f08fcf989989e35bc80c16063e455', 'siteadmin2@example.com', 'Jane', 'Smith', '{"lat": -45.0, "lon": 168.7}', NULL, 'default.png', 'siteadmin', 'active');


insert into plants (name, description, image, invasiveness, ai_generated, is_variation)
values ('Akebia quinata', 'Akebia quinata Weed', 'Akebia quinata Weed.jpg', 'invasive', 0, 0),
       ('Anaphalioides bellidioides', 'Anaphalioides bellidioides NotWeed', 'Anaphalioides bellidioides NotWeed.jpg', 'non-invasive', 0, 0),
	('Aristea ecklonii', 'Aristea ecklonii Weed', 'Aristea ecklonii Weed.png', 'invasive', 0, 0),
       ('Arthropodium cirrhatum', 'Arthropodium cirrhatum NotWeed', 'Arthropodium cirrhatum NotWeed.jpg', 'non-invasive', 0, 0),
       ('Berberis darwinii', 'Berberis darwinii Weed', 'Berberis darwinii Weed.jpg', 'invasive', 0, 0),
       ('Bomarea multiflora', 'Bomarea multiflora Weed', 'Bomarea multiflora Weed.jpg', 'invasive', 0, 0),
       ('Buddleja davidii', 'Buddleja davidii Weed', 'Buddleja davidii Weed.jpg', 'invasive', 0, 0),
       ('Camellia sasanqua ''Yuletide''', 'Camellia sasanqua ''Yuletide'' NotWeed', 'Camellia sasanqua Yuletide NotWeed.jpg', 'non-invasive', 0, 0),
       ('Cardiospermum grandiflorum', 'Cardiospermum grandiflorum Weed', 'Cardiospermum grandiflorum Weed.jpg', 'invasive', 0, 0),
       ('Catanospermum_australe', 'Catanospermum_australe_Weed', 'Catanospermum_australe_Weed.png', 'invasive', 0, 0),
       ('Cestrum parqui', 'Cestrum parqui Weed', 'Cestrum parqui Weed.png', 'invasive', 0, 0),
       ('Cytisus scoparius', 'Cytisus scoparius Weed', 'Cytisus scoparius Weed.jpg', 'invasive', 0, 0),
       ('Erica cinerea', 'Erica cinerea Weed', 'Erica cinerea Weed.jpg', 'invasive', 0, 0),
       ('Fuchisia boliviana', 'Fuchisia boliviana Weed', 'Fuchisia boliviana Weed.png', 'invasive', 0, 0),
       ('Ipomoea indica', 'Ipomoea indica Weed', 'Ipomoea indica Weed.png', 'invasive', 0, 0),
       ('Iris setosa', 'Iris setosa NotWeed', 'Iris setosa NotWeed.jpg', 'non-invasive', 0, 0),
       ('Kennedia rubicunda', 'Kennedia rubicunda Weed', 'Kennedia rubicunda Weed.png', 'invasive', 0, 0),
       ('Lamium galeobdolon', 'Lamium galeobdolon Weed', 'Lamium galeobdolon Weed.jpg', 'invasive', 0, 0),
       ('Michelia doltsopa', 'Michelia doltsopa NotWeed', 'Michelia doltsopa NotWeed.jpg', 'non-invasive', 0, 0),
       ('Michelia figo', 'Michelia figo NotWeed', 'Michelia figo NotWeed.jpg', 'non-invasive', 0, 0),
       ('Passiflora caerulea', 'Passiflora caerulea Weed', 'Passiflora caerulea Weed.jpg', 'invasive', 0, 0),
       ('Phylica Plumosa', 'Phylica Plumosa NotWeed', 'Phylica Plumosa NotWeed.jpg', 'non-invasive', 0, 0),
       ('Pyrus salicifolia ''Pendula''', 'Pyrus salicifolia ''Pendula'' NotWeed', 'Pyrus salicifolia Pendula NotWeed.jpg', 'non-invasive', 0, 0),
       ('Rosa banksia ''Luteum''', 'Rosa banksia ''Luteum'' NotWeed', 'Rosa banksia Luteum NotWeed.jpg', 'non-invasive', 0, 0),
       ('Sagittaria platyphylla', 'Sagittaria platyphylla Weed', 'Sagittaria platyphylla Weed.png', 'invasive', 0, 0),
       ('Salvia leucantha', 'Salvia leucantha NotWeed', 'Salvia leucantha NotWeed.jpg', 'non-invasive', 0, 0),
       ('Senecio angulatus', 'Senecio angulatus Weed', 'Senecio angulatus Weed.jpg', 'invasive', 0, 0),
       ('Strelitzia-reginae', 'Strelitzia-reginae NotWeed', 'Strelitzia-reginae NotWeed.jpg', 'non-invasive', 0, 0),
       ('Trachelospermum jasminoides', 'Trachelospermum jasminoides NotWeed', 'Trachelospermum jasminoides NotWeed.jpg', 'non-invasive', 0, 0),
       ('Tropaeolum speciosum', 'Tropaeolum speciosum Weed', 'Tropaeolum speciosum Weed.jpg', 'invasive', 0, 0),
       ('Tweedia caerulea', 'Tweedia caerulea NotWeed', 'Tweedia caerulea NotWeed.jpg', 'non-invasive', 0, 0),
       ('Vincetoxicum nigrum', 'Vincetoxicum nigrum Weed', 'Vincetoxicum nigrum Weed.jpg', 'invasive', 0, 0),
       ('Zantedeschia aethiopica', 'Zantedeschia aethiopica Weed', 'Zantedeschia aethiopica Weed.png', 'invasive', 0, 0);


SET FOREIGN_KEY_CHECKS = 1;



/*
SET FOREIGN_KEY_CHECKS = 0;

truncate table survey_metadata;
truncate table survey_results;
truncate table survey_cycle;
truncate table bt_beta_score_by_invasive_type_histogram;
truncate table bt_beta_score_heat_map;
truncate table bt_beta_score_win_percentage;
truncate table win_loss_by_plant;

SET FOREIGN_KEY_CHECKS = 1;
*/