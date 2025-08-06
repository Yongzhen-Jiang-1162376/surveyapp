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

DROP TABLE IF EXISTS `survey_results`;
CREATE TABLE `survey_results` (
  `id` INT AUTO_INCREMENT,
  `session_id` VARCHAR(255) NOT NULL,       -- stores UUID string
  `question_number` INT NOT NULL,           -- 1 to 10
  `selected_plant_id` INT NOT NULL,    -- which plant they chose
  `submission_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- auto logs each click time
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_selected_plant`
    FOREIGN KEY (`selected_plant_id`) REFERENCES `plants`(`id`),
  CONSTRAINT `fk_session_id`
    FOREIGN KEY (`session_id`) REFERENCES `survey_metadata`(`session_id`)
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
alter table survey_results
add (
	`response_time`	float,
	`invasive_plant_id` int,
  `non_invasive_plant_id` int,
  `invasive_plant_selected` bool
);

-- rename question_number to question_seq 
alter table survey_results
change question_number question_seq int;


SET FOREIGN_KEY_CHECKS = 1;
