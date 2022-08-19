-- MySQL dump 10.13  Distrib 8.0.22, for osx10.16 (x86_64)
--
-- Host: localhost    Database: lobsters_dev
-- ------------------------------------------------------
-- Server version	8.0.22

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `ar_internal_metadata`
--

DROP TABLE IF EXISTS `ar_internal_metadata`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ar_internal_metadata` (
  `key` varchar(255) NOT NULL,
  `value` varchar(255) DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  PRIMARY KEY (`key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `categories`
--

DROP TABLE IF EXISTS `categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `categories` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `category` varchar(255) DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `index_categories_on_category` (`category`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `comments`
--

DROP TABLE IF EXISTS `comments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `comments` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `created_at` datetime NOT NULL,
  `updated_at` datetime DEFAULT NULL,
  `short_id` varchar(10) NOT NULL DEFAULT '',
  `story_id` bigint unsigned NOT NULL,
  `user_id` bigint unsigned NOT NULL,
  `parent_comment_id` bigint unsigned DEFAULT NULL,
  `thread_id` bigint unsigned DEFAULT NULL,
  `comment` mediumtext NOT NULL,
  `score` int NOT NULL DEFAULT '1',
  `flags` int unsigned NOT NULL DEFAULT '0',
  `confidence` decimal(20,19) NOT NULL DEFAULT '0.0000000000000000000',
  `markeddown_comment` mediumtext,
  `is_deleted` tinyint(1) DEFAULT '0',
  `is_moderated` tinyint(1) DEFAULT '0',
  `is_from_email` tinyint(1) DEFAULT '0',
  `hat_id` bigint unsigned DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `short_id` (`short_id`),
  KEY `confidence_idx` (`confidence`),
  KEY `comments_hat_id_fk` (`hat_id`),
  KEY `comments_parent_comment_id_fk` (`parent_comment_id`),
  KEY `index_comments_on_score` (`score`),
  KEY `story_id_short_id` (`story_id`,`short_id`),
  KEY `thread_id` (`thread_id`),
  KEY `index_comments_on_user_id` (`user_id`),
  FULLTEXT KEY `index_comments_on_comment` (`comment`),
  CONSTRAINT `comments_hat_id_fk` FOREIGN KEY (`hat_id`) REFERENCES `hats` (`id`),
  CONSTRAINT `comments_parent_comment_id_fk` FOREIGN KEY (`parent_comment_id`) REFERENCES `comments` (`id`),
  CONSTRAINT `comments_story_id_fk` FOREIGN KEY (`story_id`) REFERENCES `stories` (`id`),
  CONSTRAINT `comments_user_id_fk` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1744 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `domains`
--

DROP TABLE IF EXISTS `domains`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `domains` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `domain` varchar(255) DEFAULT NULL,
  `is_tracker` tinyint(1) NOT NULL DEFAULT '0',
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `banned_at` datetime DEFAULT NULL,
  `banned_by_user_id` int DEFAULT NULL,
  `banned_reason` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=200 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `hat_requests`
--

DROP TABLE IF EXISTS `hat_requests`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `hat_requests` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `user_id` bigint unsigned NOT NULL,
  `hat` varchar(255) NOT NULL,
  `link` varchar(255) NOT NULL,
  `comment` text NOT NULL,
  PRIMARY KEY (`id`),
  KEY `hat_requests_user_id_fk` (`user_id`),
  CONSTRAINT `hat_requests_user_id_fk` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `hats`
--

DROP TABLE IF EXISTS `hats`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `hats` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `user_id` bigint unsigned NOT NULL,
  `granted_by_user_id` bigint unsigned NOT NULL,
  `hat` varchar(255) NOT NULL,
  `link` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `modlog_use` tinyint(1) DEFAULT '0',
  `doffed_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `hats_granted_by_user_id_fk` (`granted_by_user_id`),
  KEY `hats_user_id_fk` (`user_id`),
  CONSTRAINT `hats_granted_by_user_id_fk` FOREIGN KEY (`granted_by_user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `hats_user_id_fk` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `hidden_stories`
--

DROP TABLE IF EXISTS `hidden_stories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `hidden_stories` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `user_id` bigint unsigned NOT NULL,
  `story_id` bigint unsigned NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `index_hidden_stories_on_user_id_and_story_id` (`user_id`,`story_id`),
  KEY `hidden_stories_story_id_fk` (`story_id`),
  CONSTRAINT `hidden_stories_story_id_fk` FOREIGN KEY (`story_id`) REFERENCES `stories` (`id`),
  CONSTRAINT `hidden_stories_user_id_fk` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `invitation_requests`
--

DROP TABLE IF EXISTS `invitation_requests`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `invitation_requests` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `code` varchar(255) DEFAULT NULL,
  `is_verified` tinyint(1) DEFAULT '0',
  `email` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `memo` text,
  `ip_address` varchar(255) DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `invitations`
--

DROP TABLE IF EXISTS `invitations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `invitations` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `user_id` bigint unsigned NOT NULL,
  `email` varchar(255) DEFAULT NULL,
  `code` varchar(255) DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `memo` mediumtext,
  `used_at` datetime DEFAULT NULL,
  `new_user_id` bigint unsigned DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `invitations_new_user_id_fk` (`new_user_id`),
  KEY `invitations_user_id_fk` (`user_id`),
  CONSTRAINT `invitations_new_user_id_fk` FOREIGN KEY (`new_user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `invitations_user_id_fk` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `keystores`
--

DROP TABLE IF EXISTS `keystores`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `keystores` (
  `key` varchar(50) NOT NULL DEFAULT '',
  `value` bigint DEFAULT NULL,
  UNIQUE KEY `key` (`key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `messages`
--

DROP TABLE IF EXISTS `messages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `messages` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `created_at` datetime DEFAULT NULL,
  `author_user_id` bigint unsigned NOT NULL,
  `recipient_user_id` bigint unsigned NOT NULL,
  `has_been_read` tinyint(1) DEFAULT '0',
  `subject` varchar(100) DEFAULT NULL,
  `body` mediumtext,
  `short_id` varchar(30) DEFAULT NULL,
  `deleted_by_author` tinyint(1) DEFAULT '0',
  `deleted_by_recipient` tinyint(1) DEFAULT '0',
  `hat_id` bigint unsigned DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `random_hash` (`short_id`),
  KEY `index_messages_on_hat_id` (`hat_id`),
  KEY `messages_recipient_user_id_fk` (`recipient_user_id`),
  CONSTRAINT `messages_hat_id_fk` FOREIGN KEY (`hat_id`) REFERENCES `hats` (`id`),
  CONSTRAINT `messages_recipient_user_id_fk` FOREIGN KEY (`recipient_user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=484 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `mod_notes`
--

DROP TABLE IF EXISTS `mod_notes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `mod_notes` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `moderator_user_id` bigint unsigned NOT NULL,
  `user_id` bigint unsigned NOT NULL,
  `note` text NOT NULL,
  `markeddown_note` text NOT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `index_mod_notes_on_id_and_user_id` (`id`,`user_id`),
  KEY `mod_notes_moderator_user_id_fk` (`moderator_user_id`),
  KEY `mod_notes_user_id_fk` (`user_id`),
  CONSTRAINT `mod_notes_moderator_user_id_fk` FOREIGN KEY (`moderator_user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `mod_notes_user_id_fk` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `moderations`
--

DROP TABLE IF EXISTS `moderations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `moderations` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `moderator_user_id` bigint unsigned DEFAULT NULL,
  `story_id` bigint unsigned DEFAULT NULL,
  `comment_id` bigint unsigned DEFAULT NULL,
  `user_id` bigint unsigned DEFAULT NULL,
  `action` mediumtext,
  `reason` mediumtext,
  `is_from_suggestions` tinyint(1) DEFAULT '0',
  `tag_id` bigint unsigned DEFAULT NULL,
  `domain_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `moderations_comment_id_fk` (`comment_id`),
  KEY `index_moderations_on_created_at` (`created_at`),
  KEY `index_moderations_on_domain_id` (`domain_id`),
  KEY `moderations_moderator_user_id_fk` (`moderator_user_id`),
  KEY `moderations_story_id_fk` (`story_id`),
  KEY `moderations_tag_id_fk` (`tag_id`),
  KEY `index_moderations_on_user_id` (`user_id`),
  CONSTRAINT `moderations_comment_id_fk` FOREIGN KEY (`comment_id`) REFERENCES `comments` (`id`),
  CONSTRAINT `moderations_moderator_user_id_fk` FOREIGN KEY (`moderator_user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `moderations_story_id_fk` FOREIGN KEY (`story_id`) REFERENCES `stories` (`id`),
  CONSTRAINT `moderations_tag_id_fk` FOREIGN KEY (`tag_id`) REFERENCES `tags` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=660 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `read_ribbons`
--

DROP TABLE IF EXISTS `read_ribbons`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `read_ribbons` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `is_following` tinyint(1) DEFAULT '1',
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `user_id` bigint unsigned NOT NULL,
  `story_id` bigint unsigned NOT NULL,
  PRIMARY KEY (`id`),
  KEY `index_read_ribbons_on_story_id` (`story_id`),
  KEY `index_read_ribbons_on_user_id` (`user_id`),
  CONSTRAINT `read_ribbons_story_id_fk` FOREIGN KEY (`story_id`) REFERENCES `stories` (`id`),
  CONSTRAINT `read_ribbons_user_id_fk` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary view structure for view `replying_comments`
--

DROP TABLE IF EXISTS `replying_comments`;
/*!50001 DROP VIEW IF EXISTS `replying_comments`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `replying_comments` AS SELECT 
 1 AS `user_id`,
 1 AS `comment_id`,
 1 AS `story_id`,
 1 AS `parent_comment_id`,
 1 AS `comment_created_at`,
 1 AS `parent_comment_author_id`,
 1 AS `comment_author_id`,
 1 AS `story_author_id`,
 1 AS `is_unread`,
 1 AS `current_vote_vote`,
 1 AS `current_vote_reason`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `saved_stories`
--

DROP TABLE IF EXISTS `saved_stories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `saved_stories` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `user_id` bigint unsigned NOT NULL,
  `story_id` bigint unsigned NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `index_saved_stories_on_user_id_and_story_id` (`user_id`,`story_id`),
  KEY `saved_stories_story_id_fk` (`story_id`),
  CONSTRAINT `saved_stories_story_id_fk` FOREIGN KEY (`story_id`) REFERENCES `stories` (`id`),
  CONSTRAINT `saved_stories_user_id_fk` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `schema_migrations`
--

DROP TABLE IF EXISTS `schema_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `schema_migrations` (
  `version` varchar(255) NOT NULL,
  PRIMARY KEY (`version`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `stories`
--

DROP TABLE IF EXISTS `stories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `stories` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `created_at` datetime DEFAULT NULL,
  `user_id` bigint unsigned NOT NULL,
  `url` varchar(250) DEFAULT '',
  `title` varchar(150) NOT NULL DEFAULT '',
  `description` mediumtext,
  `short_id` varchar(6) NOT NULL DEFAULT '',
  `is_expired` tinyint(1) NOT NULL DEFAULT '0',
  `score` int NOT NULL DEFAULT '1',
  `flags` int unsigned NOT NULL DEFAULT '0',
  `is_moderated` tinyint(1) NOT NULL DEFAULT '0',
  `hotness` decimal(20,10) NOT NULL DEFAULT '0.0000000000',
  `markeddown_description` mediumtext,
  `comments_count` int NOT NULL DEFAULT '0',
  `merged_story_id` bigint unsigned DEFAULT NULL,
  `unavailable_at` datetime DEFAULT NULL,
  `twitter_id` varchar(20) DEFAULT NULL,
  `user_is_author` tinyint(1) DEFAULT '0',
  `user_is_following` tinyint(1) NOT NULL DEFAULT '0',
  `domain_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_short_id` (`short_id`),
  KEY `index_stories_on_created_at` (`created_at`),
  KEY `index_stories_on_domain_id` (`domain_id`),
  KEY `hotness_idx` (`hotness`),
  KEY `index_stories_on_id_and_is_expired` (`id`,`is_expired`),
  KEY `index_stories_on_merged_story_id` (`merged_story_id`),
  KEY `index_stories_on_score` (`score`),
  KEY `index_stories_on_twitter_id` (`twitter_id`),
  KEY `url` (`url`(191)),
  KEY `index_stories_on_user_id` (`user_id`),
  FULLTEXT KEY `index_stories_on_description` (`description`),
  FULLTEXT KEY `index_stories_on_title` (`title`),
  CONSTRAINT `fk_rails_a04bca56b0` FOREIGN KEY (`domain_id`) REFERENCES `domains` (`id`),
  CONSTRAINT `stories_merged_story_id_fk` FOREIGN KEY (`merged_story_id`) REFERENCES `stories` (`id`),
  CONSTRAINT `stories_user_id_fk` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=441 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `story_texts`
--

DROP TABLE IF EXISTS `story_texts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `story_texts` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `body` mediumtext NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  FULLTEXT KEY `index_story_texts_on_body` (`body`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `suggested_taggings`
--

DROP TABLE IF EXISTS `suggested_taggings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `suggested_taggings` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `story_id` bigint unsigned NOT NULL,
  `tag_id` bigint unsigned NOT NULL,
  `user_id` bigint unsigned NOT NULL,
  PRIMARY KEY (`id`),
  KEY `suggested_taggings_story_id_fk` (`story_id`),
  KEY `suggested_taggings_tag_id_fk` (`tag_id`),
  KEY `suggested_taggings_user_id_fk` (`user_id`),
  CONSTRAINT `suggested_taggings_story_id_fk` FOREIGN KEY (`story_id`) REFERENCES `stories` (`id`),
  CONSTRAINT `suggested_taggings_tag_id_fk` FOREIGN KEY (`tag_id`) REFERENCES `tags` (`id`),
  CONSTRAINT `suggested_taggings_user_id_fk` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `suggested_titles`
--

DROP TABLE IF EXISTS `suggested_titles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `suggested_titles` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `story_id` bigint unsigned NOT NULL,
  `user_id` bigint unsigned NOT NULL,
  `title` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '',
  PRIMARY KEY (`id`),
  KEY `suggested_titles_story_id_fk` (`story_id`),
  KEY `suggested_titles_user_id_fk` (`user_id`),
  CONSTRAINT `suggested_titles_story_id_fk` FOREIGN KEY (`story_id`) REFERENCES `stories` (`id`),
  CONSTRAINT `suggested_titles_user_id_fk` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tag_filters`
--

DROP TABLE IF EXISTS `tag_filters`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tag_filters` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `user_id` bigint unsigned NOT NULL,
  `tag_id` bigint unsigned NOT NULL,
  PRIMARY KEY (`id`),
  KEY `tag_filters_tag_id_fk` (`tag_id`),
  KEY `user_tag_idx` (`user_id`,`tag_id`),
  CONSTRAINT `tag_filters_tag_id_fk` FOREIGN KEY (`tag_id`) REFERENCES `tags` (`id`),
  CONSTRAINT `tag_filters_user_id_fk` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `taggings`
--

DROP TABLE IF EXISTS `taggings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `taggings` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `story_id` bigint unsigned NOT NULL,
  `tag_id` bigint unsigned NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `story_id_tag_id` (`story_id`,`tag_id`),
  KEY `taggings_tag_id_fk` (`tag_id`),
  CONSTRAINT `taggings_story_id_fk` FOREIGN KEY (`story_id`) REFERENCES `stories` (`id`),
  CONSTRAINT `taggings_tag_id_fk` FOREIGN KEY (`tag_id`) REFERENCES `tags` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=441 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tags`
--

DROP TABLE IF EXISTS `tags`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tags` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `tag` varchar(25) NOT NULL,
  `description` varchar(100) DEFAULT NULL,
  `privileged` tinyint(1) NOT NULL DEFAULT '0',
  `is_media` tinyint(1) NOT NULL DEFAULT '0',
  `active` tinyint(1) NOT NULL DEFAULT '1',
  `hotness_mod` float DEFAULT '0',
  `permit_by_new_users` tinyint(1) NOT NULL DEFAULT '1',
  `category_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `tag` (`tag`),
  KEY `index_tags_on_category_id` (`category_id`)
) ENGINE=InnoDB AUTO_INCREMENT=157 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `username` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `email` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `password_digest` varchar(75) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `is_admin` tinyint(1) DEFAULT '0',
  `password_reset_token` varchar(75) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `session_token` varchar(75) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '',
  `about` mediumtext CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
  `invited_by_user_id` bigint unsigned DEFAULT NULL,
  `is_moderator` tinyint(1) DEFAULT '0',
  `pushover_mentions` tinyint(1) DEFAULT '0',
  `rss_token` varchar(75) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `mailing_list_token` varchar(75) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `mailing_list_mode` int DEFAULT '0',
  `karma` int NOT NULL DEFAULT '0',
  `banned_at` datetime DEFAULT NULL,
  `banned_by_user_id` bigint unsigned DEFAULT NULL,
  `banned_reason` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `disabled_invite_at` datetime DEFAULT NULL,
  `disabled_invite_by_user_id` bigint unsigned DEFAULT NULL,
  `disabled_invite_reason` varchar(200) DEFAULT NULL,
  `settings` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `session_hash` (`session_token`),
  UNIQUE KEY `index_users_on_email` (`email`),
  UNIQUE KEY `mailing_list_token` (`mailing_list_token`),
  UNIQUE KEY `password_reset_token` (`password_reset_token`),
  UNIQUE KEY `rss_token` (`rss_token`),
  UNIQUE KEY `username` (`username`),
  KEY `users_banned_by_user_id_fk` (`banned_by_user_id`),
  KEY `users_disabled_invite_by_user_id_fk` (`disabled_invite_by_user_id`),
  KEY `users_invited_by_user_id_fk` (`invited_by_user_id`),
  KEY `mailing_list_enabled` (`mailing_list_mode`),
  CONSTRAINT `users_banned_by_user_id_fk` FOREIGN KEY (`banned_by_user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `users_disabled_invite_by_user_id_fk` FOREIGN KEY (`disabled_invite_by_user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `users_invited_by_user_id_fk` FOREIGN KEY (`invited_by_user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=45 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `votes`
--

DROP TABLE IF EXISTS `votes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `votes` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `user_id` bigint unsigned NOT NULL,
  `story_id` bigint unsigned NOT NULL,
  `comment_id` bigint unsigned DEFAULT NULL,
  `vote` tinyint NOT NULL,
  `reason` varchar(1) DEFAULT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `index_votes_on_comment_id` (`comment_id`),
  KEY `votes_story_id_fk` (`story_id`),
  KEY `user_id_comment_id` (`user_id`,`comment_id`),
  KEY `user_id_story_id` (`user_id`,`story_id`),
  CONSTRAINT `votes_comment_id_fk` FOREIGN KEY (`comment_id`) REFERENCES `comments` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `votes_story_id_fk` FOREIGN KEY (`story_id`) REFERENCES `stories` (`id`),
  CONSTRAINT `votes_user_id_fk` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2184 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Final view structure for view `replying_comments`
--

/*!50001 DROP VIEW IF EXISTS `replying_comments`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`lob_dev`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `replying_comments` AS select `read_ribbons`.`user_id` AS `user_id`,`comments`.`id` AS `comment_id`,`read_ribbons`.`story_id` AS `story_id`,`comments`.`parent_comment_id` AS `parent_comment_id`,`comments`.`created_at` AS `comment_created_at`,`parent_comments`.`user_id` AS `parent_comment_author_id`,`comments`.`user_id` AS `comment_author_id`,`stories`.`user_id` AS `story_author_id`,(`read_ribbons`.`updated_at` < `comments`.`created_at`) AS `is_unread`,(select `votes`.`vote` from `votes` where ((`votes`.`user_id` = `read_ribbons`.`user_id`) and (`votes`.`comment_id` = `comments`.`id`))) AS `current_vote_vote`,(select `votes`.`reason` from `votes` where ((`votes`.`user_id` = `read_ribbons`.`user_id`) and (`votes`.`comment_id` = `comments`.`id`))) AS `current_vote_reason` from (((`read_ribbons` join `comments` on((`comments`.`story_id` = `read_ribbons`.`story_id`))) join `stories` on((`stories`.`id` = `comments`.`story_id`))) left join `comments` `parent_comments` on((`parent_comments`.`id` = `comments`.`parent_comment_id`))) where ((`read_ribbons`.`is_following` = 1) and (`comments`.`user_id` <> `read_ribbons`.`user_id`) and (`comments`.`is_deleted` = 0) and (`comments`.`is_moderated` = 0) and ((`parent_comments`.`user_id` = `read_ribbons`.`user_id`) or ((`parent_comments`.`user_id` is null) and (`stories`.`user_id` = `read_ribbons`.`user_id`))) and (`stories`.`score` >= 0) and (`comments`.`score` >= 0) and ((`parent_comments`.`id` is null) or ((`parent_comments`.`score` >= 0) and (`parent_comments`.`is_moderated` = 0) and (`parent_comments`.`is_deleted` = 0))) and exists(select 1 from (`votes` `f` join `comments` `c` on((`f`.`comment_id` = `c`.`id`))) where ((`f`.`vote` < 0) and (`f`.`user_id` = `parent_comments`.`user_id`) and (`c`.`user_id` = `comments`.`user_id`) and (`f`.`story_id` = `comments`.`story_id`))) is false) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2020-12-17  0:22:58
