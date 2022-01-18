-- MySQL dump 10.13  Distrib 5.7.30, for Linux (x86_64)
--
-- Host: localhost    Database: testconf
-- ------------------------------------------------------
-- Server version	5.7.30-0ubuntu0.18.04.1-log

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `ActionLog`
--

DROP TABLE IF EXISTS `ActionLog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ActionLog` (
  `logId` int(11) NOT NULL AUTO_INCREMENT,
  `contactId` int(11) NOT NULL,
  `destContactId` int(11) DEFAULT NULL,
  `trueContactId` int(11) DEFAULT NULL,
  `paperId` int(11) DEFAULT NULL,
  `timestamp` bigint(11) NOT NULL,
  `ipaddr` varbinary(39) DEFAULT NULL,
  `action` varbinary(4096) NOT NULL,
  `data` varbinary(8192) DEFAULT NULL,
  PRIMARY KEY (`logId`)
) ENGINE=InnoDB AUTO_INCREMENT=67 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Capability`
--

DROP TABLE IF EXISTS `Capability`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Capability` (
  `capabilityType` int(11) NOT NULL,
  `contactId` int(11) NOT NULL,
  `paperId` int(11) NOT NULL,
  `timeExpires` bigint(11) NOT NULL,
  `salt` varbinary(255) NOT NULL,
  `data` varbinary(4096) DEFAULT NULL,
  PRIMARY KEY (`salt`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ContactInfo`
--

DROP TABLE IF EXISTS `ContactInfo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ContactInfo` (
  `contactId` int(11) NOT NULL AUTO_INCREMENT,
  `firstName` varbinary(120) NOT NULL DEFAULT '',
  `lastName` varbinary(120) NOT NULL DEFAULT '',
  `unaccentedName` varbinary(240) NOT NULL DEFAULT '',
  `email` varchar(120) NOT NULL,
  `preferredEmail` varchar(120) DEFAULT NULL,
  `affiliation` varbinary(2048) NOT NULL DEFAULT '',
  `phone` varbinary(64) DEFAULT NULL,
  `country` varbinary(256) DEFAULT NULL,
  `password` varbinary(2048) NOT NULL,
  `passwordTime` bigint(11) NOT NULL DEFAULT '0',
  `passwordUseTime` bigint(11) NOT NULL DEFAULT '0',
  `collaborators` varbinary(8192) DEFAULT NULL,
  `creationTime` bigint(11) NOT NULL DEFAULT '0',
  `updateTime` bigint(11) NOT NULL DEFAULT '0',
  `lastLogin` bigint(11) NOT NULL DEFAULT '0',
  `defaultWatch` int(11) NOT NULL DEFAULT '2',
  `roles` tinyint(1) NOT NULL DEFAULT '0',
  `disabled` tinyint(1) NOT NULL DEFAULT '0',
  `contactTags` varbinary(4096) DEFAULT NULL,
  `birthday` int(11) DEFAULT NULL,
  `gender` varbinary(24) DEFAULT NULL,
  `data` varbinary(32767) DEFAULT NULL,
  PRIMARY KEY (`contactId`),
  UNIQUE KEY `email` (`email`),
  KEY `roles` (`roles`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `DeletedContactInfo`
--

DROP TABLE IF EXISTS `DeletedContactInfo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `DeletedContactInfo` (
  `contactId` int(11) NOT NULL,
  `firstName` varbinary(120) NOT NULL,
  `lastName` varbinary(120) NOT NULL,
  `unaccentedName` varbinary(240) NOT NULL,
  `email` varchar(120) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `DocumentLink`
--

DROP TABLE IF EXISTS `DocumentLink`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `DocumentLink` (
  `paperId` int(11) NOT NULL,
  `linkId` int(11) NOT NULL,
  `linkType` int(11) NOT NULL,
  `documentId` int(11) NOT NULL,
  PRIMARY KEY (`paperId`,`linkId`,`linkType`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `FilteredDocument`
--

DROP TABLE IF EXISTS `FilteredDocument`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `FilteredDocument` (
  `inDocId` int(11) NOT NULL,
  `filterType` int(11) NOT NULL,
  `outDocId` int(11) NOT NULL,
  `createdAt` bigint(11) NOT NULL,
  PRIMARY KEY (`inDocId`,`filterType`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Formula`
--

DROP TABLE IF EXISTS `Formula`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Formula` (
  `formulaId` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(200) NOT NULL,
  `expression` varbinary(4096) NOT NULL,
  `createdBy` int(11) NOT NULL DEFAULT '0',
  `timeModified` bigint(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`formulaId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `MailLog`
--

DROP TABLE IF EXISTS `MailLog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `MailLog` (
  `mailId` int(11) NOT NULL AUTO_INCREMENT,
  `recipients` varbinary(200) NOT NULL,
  `q` varbinary(4096) DEFAULT NULL,
  `t` varbinary(200) DEFAULT NULL,
  `paperIds` blob,
  `cc` blob,
  `replyto` blob,
  `subject` blob,
  `emailBody` blob,
  `fromNonChair` tinyint(1) NOT NULL DEFAULT '0',
  `status` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`mailId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Paper`
--

DROP TABLE IF EXISTS `Paper`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Paper` (
  `paperId` int(11) NOT NULL AUTO_INCREMENT,
  `title` varbinary(512) DEFAULT NULL,
  `authorInformation` varbinary(8192) DEFAULT NULL,
  `abstract` varbinary(16384) DEFAULT NULL,
  `collaborators` varbinary(8192) DEFAULT NULL,
  `timeSubmitted` bigint(11) NOT NULL DEFAULT '0',
  `timeWithdrawn` bigint(11) NOT NULL DEFAULT '0',
  `timeFinalSubmitted` bigint(11) NOT NULL DEFAULT '0',
  `timeModified` bigint(11) NOT NULL DEFAULT '0',
  `paperStorageId` int(11) NOT NULL DEFAULT '0',
  `sha1` varbinary(64) NOT NULL DEFAULT '',
  `finalPaperStorageId` int(11) NOT NULL DEFAULT '0',
  `blind` tinyint(1) NOT NULL DEFAULT '1',
  `outcome` tinyint(1) NOT NULL DEFAULT '0',
  `leadContactId` int(11) NOT NULL DEFAULT '0',
  `shepherdContactId` int(11) NOT NULL DEFAULT '0',
  `managerContactId` int(11) NOT NULL DEFAULT '0',
  `capVersion` int(1) NOT NULL DEFAULT '0',
  `size` int(11) NOT NULL DEFAULT '0',
  `mimetype` varbinary(80) NOT NULL DEFAULT '',
  `timestamp` bigint(11) NOT NULL DEFAULT '0',
  `pdfFormatStatus` bigint(11) NOT NULL DEFAULT '0',
  `withdrawReason` varbinary(1024) DEFAULT NULL,
  `paperFormat` tinyint(1) DEFAULT NULL,
  `dataOverflow` longblob,
  PRIMARY KEY (`paperId`),
  KEY `timeSubmitted` (`timeSubmitted`),
  KEY `leadContactId` (`leadContactId`),
  KEY `shepherdContactId` (`shepherdContactId`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `PaperComment`
--

DROP TABLE IF EXISTS `PaperComment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `PaperComment` (
  `paperId` int(11) NOT NULL,
  `commentId` int(11) NOT NULL AUTO_INCREMENT,
  `contactId` int(11) NOT NULL,
  `timeModified` bigint(11) NOT NULL,
  `timeNotified` bigint(11) NOT NULL DEFAULT '0',
  `timeDisplayed` bigint(11) NOT NULL DEFAULT '0',
  `comment` varbinary(32767) DEFAULT NULL,
  `commentType` int(11) NOT NULL DEFAULT '0',
  `replyTo` int(11) NOT NULL,
  `ordinal` int(11) NOT NULL DEFAULT '0',
  `authorOrdinal` int(11) NOT NULL DEFAULT '0',
  `commentTags` varbinary(1024) DEFAULT NULL,
  `commentRound` int(11) NOT NULL DEFAULT '0',
  `commentFormat` tinyint(1) DEFAULT NULL,
  `commentOverflow` longblob,
  PRIMARY KEY (`paperId`,`commentId`),
  UNIQUE KEY `commentId` (`commentId`),
  KEY `contactId` (`contactId`),
  KEY timeModifiedContact (`timeModified`,`contactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `PaperConflict`
--

DROP TABLE IF EXISTS `PaperConflict`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `PaperConflict` (
  `paperId` int(11) NOT NULL,
  `contactId` int(11) NOT NULL,
  `conflictType` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`contactId`,`paperId`),
  KEY `paperId` (`paperId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `PaperOption`
--

DROP TABLE IF EXISTS `PaperOption`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `PaperOption` (
  `paperId` int(11) NOT NULL,
  `optionId` int(11) NOT NULL,
  `value` bigint(11) NOT NULL DEFAULT '0',
  `data` varbinary(32767) DEFAULT NULL,
  `dataOverflow` longblob,
  PRIMARY KEY (`paperId`,`optionId`,`value`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `PaperReview`
--

DROP TABLE IF EXISTS `PaperReview`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `PaperReview` (
  `paperId` int(11) NOT NULL,
  `reviewId` int(11) NOT NULL AUTO_INCREMENT,
  `contactId` int(11) NOT NULL,
  `reviewToken` int(11) NOT NULL DEFAULT '0',
  `reviewType` tinyint(1) NOT NULL DEFAULT '0',
  `reviewRound` int(1) NOT NULL DEFAULT '0',
  `requestedBy` int(11) NOT NULL DEFAULT '0',
  `timeRequested` bigint(11) NOT NULL DEFAULT '0',
  `timeRequestNotified` bigint(11) NOT NULL DEFAULT '0',
  `reviewBlind` tinyint(1) NOT NULL DEFAULT '1',
  `reviewModified` bigint(1) NOT NULL DEFAULT '0',
  `reviewAuthorModified` bigint(1) DEFAULT NULL,
  `reviewSubmitted` bigint(1) DEFAULT NULL,
  `reviewNotified` bigint(1) DEFAULT NULL,
  `reviewAuthorNotified` bigint(11) NOT NULL DEFAULT '0',
  `reviewAuthorSeen` bigint(1) DEFAULT NULL,
  `reviewOrdinal` int(1) NOT NULL DEFAULT '0',
  `reviewViewScore` tinyint(2) NOT NULL DEFAULT '-3',
  `timeDisplayed` bigint(11) NOT NULL DEFAULT '0',
  `timeApprovalRequested` bigint(11) NOT NULL DEFAULT '0',
  `reviewEditVersion` int(1) NOT NULL DEFAULT '0',
  `reviewNeedsSubmit` tinyint(1) NOT NULL DEFAULT '1',
  `reviewWordCount` int(11) DEFAULT NULL,
  `reviewFormat` tinyint(1) DEFAULT NULL,
  `overAllMerit` tinyint(1) NOT NULL DEFAULT '0',
  `reviewerQualification` tinyint(1) NOT NULL DEFAULT '0',
  `novelty` tinyint(1) NOT NULL DEFAULT '0',
  `technicalMerit` tinyint(1) NOT NULL DEFAULT '0',
  `interestToCommunity` tinyint(1) NOT NULL DEFAULT '0',
  `longevity` tinyint(1) NOT NULL DEFAULT '0',
  `grammar` tinyint(1) NOT NULL DEFAULT '0',
  `likelyPresentation` tinyint(1) NOT NULL DEFAULT '0',
  `suitableForShort` tinyint(1) NOT NULL DEFAULT '0',
  `potential` tinyint(4) NOT NULL DEFAULT '0',
  `fixability` tinyint(4) NOT NULL DEFAULT '0',
  `tfields` longblob,
  `sfields` varbinary(2048) DEFAULT NULL,
  `data` varbinary(8192) DEFAULT NULL,
  PRIMARY KEY (`paperId`,`reviewId`),
  UNIQUE KEY `reviewId` (`reviewId`),
  KEY `contactId` (`contactId`),
  KEY `reviewType` (`reviewType`),
  KEY `reviewRound` (`reviewRound`),
  KEY `requestedBy` (`requestedBy`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `PaperReviewPreference`
--

DROP TABLE IF EXISTS `PaperReviewPreference`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `PaperReviewPreference` (
  `paperId` int(11) NOT NULL,
  `contactId` int(11) NOT NULL,
  `preference` int(4) NOT NULL DEFAULT '0',
  `expertise` int(4) DEFAULT NULL,
  PRIMARY KEY (`paperId`,`contactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `PaperReviewRefused`
--

DROP TABLE IF EXISTS `PaperReviewRefused`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `PaperReviewRefused` (
  `paperId` int(11) NOT NULL,
  `email` varchar(120) NOT NULL,
  `firstName` varbinary(120) DEFAULT NULL,
  `lastName` varbinary(120) DEFAULT NULL,
  `affiliation` varbinary(2048) DEFAULT NULL,
  `contactId` int(11) NOT NULL,
  `requestedBy` int(11) NOT NULL,
  `timeRequested` bigint(11) DEFAULT NULL,
  `refusedBy` int(11) DEFAULT NULL,
  `timeRefused` bigint(11) DEFAULT NULL,
  `reviewType` tinyint(1) NOT NULL DEFAULT '0',
  `reviewRound` int(1) DEFAULT NULL,
  `data` varbinary(8192) DEFAULT NULL,
  `reason` varbinary(32767) DEFAULT NULL,
  PRIMARY KEY (`paperId`,`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `PaperStorage`
--

DROP TABLE IF EXISTS `PaperStorage`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `PaperStorage` (
  `paperId` int(11) NOT NULL,
  `paperStorageId` int(11) NOT NULL AUTO_INCREMENT,
  `timestamp` bigint(11) NOT NULL,
  `mimetype` varbinary(80) NOT NULL DEFAULT '',
  `paper` longblob,
  `compression` tinyint(1) NOT NULL DEFAULT '0',
  `sha1` varbinary(64) NOT NULL DEFAULT '',
  `crc32` binary(4) DEFAULT NULL,
  `documentType` int(3) NOT NULL DEFAULT '0',
  `filename` varbinary(255) DEFAULT NULL,
  `infoJson` varbinary(32768) DEFAULT NULL,
  `size` bigint(11) DEFAULT NULL,
  `filterType` int(3) DEFAULT NULL,
  `originalStorageId` int(11) DEFAULT NULL,
  `inactive` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`paperId`,`paperStorageId`),
  UNIQUE KEY `paperStorageId` (`paperStorageId`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `PaperTag`
--

DROP TABLE IF EXISTS `PaperTag`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `PaperTag` (
  `paperId` int(11) NOT NULL,
  `tag` varchar(80) NOT NULL,
  `tagIndex` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`paperId`,`tag`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `PaperTagAnno`
--

DROP TABLE IF EXISTS `PaperTagAnno`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `PaperTagAnno` (
  `tag` varchar(80) NOT NULL,
  `annoId` int(11) NOT NULL,
  `tagIndex` float NOT NULL DEFAULT '0',
  `heading` varbinary(8192) DEFAULT NULL,
  `annoFormat` tinyint(1) DEFAULT NULL,
  `infoJson` varbinary(32768) DEFAULT NULL,
  PRIMARY KEY (`tag`,`annoId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `PaperTopic`
--

DROP TABLE IF EXISTS `PaperTopic`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `PaperTopic` (
  `paperId` int(11) NOT NULL,
  `topicId` int(11) NOT NULL,
  PRIMARY KEY (`paperId`,`topicId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `PaperWatch`
--

DROP TABLE IF EXISTS `PaperWatch`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `PaperWatch` (
  `paperId` int(11) NOT NULL,
  `contactId` int(11) NOT NULL,
  `watch` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`paperId`,`contactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ReviewRating`
--

DROP TABLE IF EXISTS `ReviewRating`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ReviewRating` (
  `paperId` int(11) NOT NULL,
  `reviewId` int(11) NOT NULL,
  `contactId` int(11) NOT NULL,
  `rating` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`paperId`,`reviewId`,`contactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ReviewRequest`
--

DROP TABLE IF EXISTS `ReviewRequest`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ReviewRequest` (
  `paperId` int(11) NOT NULL,
  `email` varchar(120) NOT NULL,
  `firstName` varbinary(120) DEFAULT NULL,
  `lastName` varbinary(120) DEFAULT NULL,
  `affiliation` varbinary(2048) DEFAULT NULL,
  `reason` varbinary(32767) DEFAULT NULL,
  `requestedBy` int(11) NOT NULL,
  `timeRequested` bigint(11) NOT NULL,
  `reviewRound` int(1) DEFAULT NULL,
  PRIMARY KEY (`paperId`,`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Settings`
--

DROP TABLE IF EXISTS `Settings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Settings` (
  `name` varbinary(256) NOT NULL,
  `value` bigint(11) NOT NULL,
  `data` varbinary(32767) DEFAULT NULL,
  PRIMARY KEY (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `TopicArea`
--

DROP TABLE IF EXISTS `TopicArea`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `TopicArea` (
  `topicId` int(11) NOT NULL AUTO_INCREMENT,
  `topicName` varbinary(1024) DEFAULT NULL,
  PRIMARY KEY (`topicId`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `TopicInterest`
--

DROP TABLE IF EXISTS `TopicInterest`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `TopicInterest` (
  `contactId` int(11) NOT NULL,
  `topicId` int(11) NOT NULL,
  `interest` int(1) NOT NULL,
  PRIMARY KEY (`contactId`,`topicId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2020-11-29 12:33:53
