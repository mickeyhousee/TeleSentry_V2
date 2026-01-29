 -- phpMyAdmin SQL Dump
-- version 4.6.6deb5ubuntu0.5
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: 29-Jul-2024 às 18:44
-- Versão do servidor: 10.1.48-MariaDB-0ubuntu0.18.04.1
-- PHP Version: 7.2.24-0ubuntu0.18.04.17

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `search_telegram`
--

-- --------------------------------------------------------

--
-- Structure of the `bot` table
--

CREATE TABLE `bot` (
  `id` int(11) NOT NULL,
  `name` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Structure of the `content` table
--

CREATE TABLE `content` (
  `id_message` int(11) NOT NULL,
  `date_message` varchar(100) DEFAULT NULL,
  `content` text,
  `translated_content` text,
  `file_id` int(11) DEFAULT NULL,
  `id_user` int(11) DEFAULT NULL,
  `id_group` int(11) DEFAULT NULL,
  `id_bot` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Structure of the `files` table
--

CREATE TABLE `files` (
  `file_id` int(11) NOT NULL,
  `file_name` text,
  `file_type` varchar(150) DEFAULT NULL,
  `hash` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Structure of the `group` table
--

CREATE TABLE `group` (
  `group_id` int(11) NOT NULL,
  `group_name` varchar(150) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Structure of the `links` table
--

CREATE TABLE `links` (
  `id_link` int(11) NOT NULL,
  `link` varchar(255) DEFAULT NULL,
  `message_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Structure of the `user` table
--

CREATE TABLE `user` (
  `id_user` int(11) NOT NULL,
  `username` varchar(150) DEFAULT NULL,
  `name` varchar(150) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


--
-- Indexes for dumped tables
--

--
-- Indexes for table `bot`
--
ALTER TABLE `bot`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `name` (`name`);

--
-- Indexes for table `content`
--
ALTER TABLE `content`
  ADD PRIMARY KEY (`id_message`),
  ADD KEY `file_id` (`file_id`),
  ADD KEY `id_user` (`id_user`),
  ADD KEY `id_group` (`id_group`),
  ADD KEY `id_bot` (`id_bot`);

--
-- Indexes for table `files`
--
ALTER TABLE `files`
  ADD PRIMARY KEY (`file_id`);

--
-- Indexes for table `group`
--
ALTER TABLE `group`
  ADD PRIMARY KEY (`group_id`),
  ADD UNIQUE KEY `group_name` (`group_name`);

--
-- Indexes for table `links`
--
ALTER TABLE `links`
  ADD PRIMARY KEY (`id_link`),
  ADD KEY `message_id` (`message_id`);

--
-- Indexes for table `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`id_user`),
  ADD UNIQUE KEY `username` (`username`),
  ADD UNIQUE KEY `name` (`name`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `bot`
--
ALTER TABLE `bot`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT for table `content`
--
ALTER TABLE `content`
  MODIFY `id_message` int(11) NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT for table `files`
--
ALTER TABLE `files`
  MODIFY `file_id` int(11) NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT for table `group`
--
ALTER TABLE `group`
  MODIFY `group_id` int(11) NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT for table `links`
--
ALTER TABLE `links`
  MODIFY `id_link` int(11) NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT for table `user`
--
ALTER TABLE `user`
  MODIFY `id_user` int(11) NOT NULL AUTO_INCREMENT;
--
-- Constraints for dumped tables
--

--
-- Limits for the `content` table
--
ALTER TABLE `content`
  ADD CONSTRAINT `content_ibfk_1` FOREIGN KEY (`file_id`) REFERENCES `files` (`file_id`),
  ADD CONSTRAINT `content_ibfk_2` FOREIGN KEY (`id_user`) REFERENCES `user` (`id_user`),
  ADD CONSTRAINT `content_ibfk_3` FOREIGN KEY (`id_group`) REFERENCES `group` (`group_id`),
  ADD CONSTRAINT `content_ibfk_4` FOREIGN KEY (`id_bot`) REFERENCES `bot` (`id`);

--
-- Limits for the `links` table
--
ALTER TABLE `links`
  ADD CONSTRAINT `links_ibfk_1` FOREIGN KEY (`message_id`) REFERENCES `content` (`id_message`);

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

--------------------------------------------------------

-- Table to store message scores
CREATE TABLE IF NOT EXISTS `message_scores` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `message_id` int(11) NOT NULL,
  `score` int(11) DEFAULT 0,
  `sensitive_terms_count` int(11) DEFAULT 0,
  `suspicious_links_count` int(11) DEFAULT 0,
  `repeated_sharing` tinyint(1) DEFAULT 0,
  `high_risk_user` tinyint(1) DEFAULT 0,
  `calculated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `message_id` (`message_id`),
  KEY `idx_score` (`score`),
  CONSTRAINT `message_scores_ibfk_1` FOREIGN KEY (`message_id`) REFERENCES `content` (`id_message`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--------------------------------------------------------
-- Table to store training feedback for the scoring system
CREATE TABLE IF NOT EXISTS `training_feedback` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `message_id` int(11) NOT NULL,
  `original_score` int(11) NOT NULL,
  `is_correct` tinyint(1) DEFAULT NULL COMMENT '1 = correto, 0 = incorreto, NULL = pendente',
  `feedback_notes` text DEFAULT NULL COMMENT 'Notas adicionais do analista',
  `reviewed_at` timestamp NULL DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `message_id` (`message_id`),
  KEY `idx_is_correct` (`is_correct`),
  KEY `idx_reviewed_at` (`reviewed_at`),
  CONSTRAINT `training_feedback_ibfk_1` FOREIGN KEY (`message_id`) REFERENCES `content` (`id_message`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--------------------------------------------------------
