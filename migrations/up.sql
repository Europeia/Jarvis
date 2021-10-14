-- Your SQL goes here

CREATE TABLE `foreign_id_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `type_name` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL,
  PRIMARY KEY (`id`)
);

CREATE TABLE `guild` (
  `id` bigint NOT NULL,
  `welcome_message` text,
  `allow_rejoin` bit(1) DEFAULT b'0',
  `gate_enabled` bit(1) DEFAULT b'0',
  `key_role_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`)
);

CREATE TABLE `keyed_users` (
  `guild_id` bigint NOT NULL,
  `user_id` bigint NOT NULL,
  `foreign_id` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL,
  `foreign_id_type` int DEFAULT NULL,
  PRIMARY KEY (`guild_id`,`user_id`)
)

CREATE TABLE `role` (
  `role_id` bigint NOT NULL,
  `guild_id` bigint NOT NULL,
  `can_join` bit(1) DEFAULT b'0',
  `name` text,
  PRIMARY KEY (`role_id`)
);

CREATE TABLE `role_commander` (
  `role_id` bigint DEFAULT NULL,
  `user_id` bigint DEFAULT NULL
)