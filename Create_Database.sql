-- CREATE SCHEMA IF NOT EXISTS `project693` DEFAULT CHARACTER SET utf8 ;
-- USE `project693` ;

SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(20) NOT NULL,
  `password_hash` varchar(64) NOT NULL,
  `email` varchar(255) NOT NULL,
  `first_name` varchar(50) DEFAULT NULL,
  `last_name` varchar(50) DEFAULT NULL,
  `location` json DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  `avatar` varchar(64) NOT NULL,
  `role` enum('siteadmin') NOT NULL,
  `status` enum('active','inactive') NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username_UK` (`username`),
  UNIQUE KEY `email_UK` (`email`)
);

DROP TABLE IF EXISTS `plants`;
CREATE TABLE `plants` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `description` varchar(255) NOT NULL,
  `image` varchar(64) NOT NULL,
  `invasiveness` enum('invasive', 'non-invasive') NOT NULL DEFAULT 'non-invasive',
  PRIMARY KEY (`id`)
) ;

DROP TABLE IF EXISTS `survey_metadata`;
CREATE TABLE `survey_metadata` (
  `id` INT AUTO_INCREMENT,
  `session_id` VARCHAR(255) NOT NULL,
  `has_garden` BOOLEAN,
  `age` VARCHAR(50),
  `reasoning` VARCHAR(50), 
  `submitted_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY (`session_id`)
);

-- add survey cycle table to support survey cycle
DROP TABLE IF EXISTS `survey_cycle`;
CREATE TABLE `survey_cycle` (
  `id` INT AUTO_INCREMENT,
  `start_time` TIMESTAMP,
  `end_time` TIMESTAMP,
  `survey_participants` INT,
  `total_choices` INT,
  `active` INT default 1,
  PRIMARY KEY (`id`)
);

DROP TABLE IF EXISTS `survey_results`;
CREATE TABLE `survey_results` (
  `id` INT AUTO_INCREMENT,
  `session_id` VARCHAR(255) NOT NULL,       -- stores UUID string
  `question_seq` INT NOT NULL,           -- 1 to 10
  `selected_plant_id` INT NOT NULL,    -- which plant they chose
  `submission_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- auto logs each click time
  `response_time`	float,
	`invasive_plant_id` int,
  `non_invasive_plant_id` int,
  `winner` int,
  `loser` int,
  `invasive_winner` int,
  `invasive_loser` int,
  `active` bool default 1,
  `cycle_id` int,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_selected_plant`
    FOREIGN KEY (`selected_plant_id`) REFERENCES `plants`(`id`),
  CONSTRAINT `fk_session_id`
    FOREIGN KEY (`session_id`) REFERENCES `survey_metadata`(`session_id`),
  CONSTRAINT `fk_cycle_id`
    FOREIGN KEY (`cycle_id`) REFERENCES `survey_cycle`(`id`)
);

SET FOREIGN_KEY_CHECKS = 1;

/* update database tables and structured for stage 2 */
SET FOREIGN_KEY_CHECKS = 0;

-- add fields in plants table
alter table plants
add (
	`ai_generated` bool,
  `is_variation` bool,
  `original_image_id`	int
);

-- add fields in survey results table
-- alter table survey_results
-- add (
-- 	`response_time`	float,
-- 	`invasive_plant_id` int,
--   `non_invasive_plant_id` int
-- );

-- rename question_number to question_seq 
-- alter table survey_results
-- change question_number question_seq int;

-- rename survey result column names to support statistical analysis
-- alter table survey_results
-- add (
--   `winner` int,
--   `loser` int,
--   `invasive_winner` int,
--   `invasive_loser` int
-- )

-- add an active column to servey result table to support survey cycle
-- by default it is true (active)
-- 1: active (current cycle)
-- 0: inactive (history cycle)
-- alter table survey_results
-- add column active bool default 1;     




-- add cycle id column to link to survey cycle table



-- add bradley-terry beta score with win percentage table
DROP TABLE IF EXISTS `bt_beta_score_win_percentage`;
CREATE TABLE `bt_beta_score_win_percentage` (
  `id` INT AUTO_INCREMENT,
  `cycle_id` INT NOT NULL,
  `plant_id` INT NOT NULL,
  `plant_name` VARCHAR(255) NOT NULL,
  `invasiveness` VARCHAR(50) NOT NULL,
  `win_percentage` float not null,
  `bt_beta_score` float not null,
  `bt_beta_socre_weighted` float not null,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_cycle_id_bt_beta_win_percentage`
    FOREIGN KEY (`cycle_id`) REFERENCES `survey_cycle`(`id`)
);

-- add bradley-terry beta score heat map table
DROP TABLE IF EXISTS `bt_beta_score_heat_map`;
CREATE TABLE `bt_beta_score_heat_map` (
  `id` INT AUTO_INCREMENT,
  `cycle_id` INT NOT NULL,
  `plant_a_id` INT NOT NULL,
  `plant_a_name` VARCHAR(255) NOT NULL,
  `plant_b_id` INT NOT NULL,
  `plant_b_name` VARCHAR(255) NOT NULL,
  `plant_a_beats_b` float,
  `plant_a_beats_b_weighted` float,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_cycle_id_bt_beta_heat_map`
    FOREIGN KEY (`cycle_id`) REFERENCES `survey_cycle`(`id`)
);

-- add bradley-terry beta score by invasive type histogram table
DROP TABLE IF EXISTS `bt_beta_score_by_invasive_type_histogram`;
CREATE TABLE `bt_beta_score_by_invasive_type_histogram` (
  `id` INT AUTO_INCREMENT,
  `cycle_id` INT NOT NULL,
  `bin_no` INT NOT NULL,
  `bin_left` float NOT NULL,
  `bin_right` float NOT NULL,
  `invasive_count` int NOT NULL,
  `non_invasive_count` int not null,
  `bin_left_weighted` float NOT NULL,
  `bin_right_weighted` float NOT NULL,
  `invasive_count_weighted` int NOT NULL,
  `non_invasive_count_weighted` int not null,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_cycle_id_bt_beta_histogram`
    FOREIGN KEY (`cycle_id`) REFERENCES `survey_cycle`(`id`)
);

-- add win/loss by plant table
DROP TABLE IF EXISTS `win_loss_by_plant`;
CREATE TABLE `win_loss_by_plant` (
  `id` INT AUTO_INCREMENT,
  `cycle_id` INT NOT NULL,
  `plant_id` INT NOT NULL,
  `plant_name` VARCHAR(255) NOT NULL,
  `invasiveness` VARCHAR(50) NOT NULL,
  `win` INT NOT NULL,
  `loss` INT NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_cycle_id_win_loss`
  FOREIGN KEY (`cycle_id`) REFERENCES `survey_cycle`(`id`)
);

-- add an active column to servey result table to support survey period
-- by default it is true (active)
alter table survey_results
add column active bool default 1;


SET FOREIGN_KEY_CHECKS = 1;
