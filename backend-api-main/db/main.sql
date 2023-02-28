DROP DATABASE IF EXISTS `bookstore`;
CREATE DATABASE `bookstore`;
USE `bookstore`;

CREATE TABLE `pending_user` (
  `pending_user_id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `name` varchar(128) DEFAULT NULL,
  `email_or_phone_number` varchar(256) NOT NULL,
  `validation_code` int(5) UNSIGNED NOT NULL,
  `code_resend_attempts` int(3) UNSIGNED DEFAULT 0,
  `role` varchar(10) DEFAULT "customer",
  `password_hash` varchar(512),
  `default_lang` varchar(2) DEFAULT "en",
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`pending_user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `user` (
  `user_id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `email` varchar(256) UNIQUE DEFAULT NULL,
  `phone_number` varchar(25) UNIQUE DEFAULT NULL,
  `password_hash` varchar(512),
  `default_lang` varchar(2) DEFAULT "en",
  `default_role` varchar(10) DEFAULT "customer",
  `name` varchar(128) DEFAULT NULL,
  `is_active` bool DEFAULT true,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3120 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `refresh_token` (
  `token` varchar(256) NOT NULL,
  `user_id` int(10) UNSIGNED NOT NULL,
  `is_active` bool DEFAULT true,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`token`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `system_admin` (
  `user_id` int(10) UNSIGNED NOT NULL,
  `is_active` bool DEFAULT true,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `manager` (
  `user_id` int(10) UNSIGNED NOT NULL,
  `is_active` bool DEFAULT true,
  `is_company_owner` bool DEFAULT false,
  `company_id` int(10) UNSIGNED DEFAULT NULL,
  `company_permissions` varchar(512) DEFAULT "",
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE customer (
  'customer_id' int(10) UNSIGNED NOT NULL,
  'active_order_request' bool DEFAULT true,
  'is_active' bool DEFAULT true,
  'created_at' timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  'updated_at' timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (customer_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE order(
  'order_id' int(10) UNSIGNED NOT NULL,
  'customer_id' int(10) UNSIGNED NOT NULL,
  'quantity' int(10) unsigned default null,
  'product_id' int(10) unsigned NOT NULL,
  'created_at' timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  'updated_at' timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (order_id)
) ENGINE=InnoDB AUTO_INCREMENT=7822 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE product(
  'product_id' int(10) UNSIGNED NOT NULL,
  'quantity' int(10) unsigned default null,
  'price' int(10) unsigned default null,
  'book_id' int(10) UNSIGNED NOT NULL,
  'created_at' timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  'updated_at' timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (product_id)
) ENGINE=InnoDB AUTO_INCREMENT=7822 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE book (
  'book_id' int(10) UNSIGNED NOT NULL,
  'book_name' varchar(100) unsigned default null,
  'description' varchar(100) unsigned default null,
  'author' varchar(100) unsigned default null,
  'created_at' timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  'updated_at' timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (book_id)
) ENGINE=InnoDB AUTO_INCREMENT=4233 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;





