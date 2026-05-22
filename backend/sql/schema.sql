-- 股票基金投资论坛数据库初始化脚本（MySQL 8.x）

CREATE TABLE IF NOT EXISTS users (
  id VARCHAR(64) PRIMARY KEY,
  register_method VARCHAR(16) NOT NULL,
  created_at DATETIME NOT NULL,
  updated_at DATETIME NOT NULL
);

CREATE TABLE IF NOT EXISTS user_auth (
  user_id VARCHAR(64) PRIMARY KEY,
  phone VARCHAR(20) UNIQUE,
  phone_verified TINYINT(1) NOT NULL DEFAULT 0,
  email VARCHAR(128) UNIQUE,
  email_verified TINYINT(1) NOT NULL DEFAULT 0,
  wechat_open_id VARCHAR(128) UNIQUE,
  weibo_open_id VARCHAR(128) UNIQUE,
  password_hash VARCHAR(255),
  FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS user_profiles (
  user_id VARCHAR(64) PRIMARY KEY,
  nickname VARCHAR(32) NOT NULL,
  avatar_url VARCHAR(512),
  bio VARCHAR(500),
  experience_tags JSON NOT NULL,
  focus_markets JSON NOT NULL,
  risk_preference VARCHAR(8) NOT NULL DEFAULT 'C3',
  posts_count INT NOT NULL DEFAULT 0,
  featured_posts_count INT NOT NULL DEFAULT 0,
  influence_score INT NOT NULL DEFAULT 0,
  badges JSON NOT NULL,
  FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS user_privacy_settings (
  user_id VARCHAR(64) PRIMARY KEY,
  nickname_visibility VARCHAR(16) NOT NULL DEFAULT 'public',
  avatar_visibility VARCHAR(16) NOT NULL DEFAULT 'public',
  bio_visibility VARCHAR(16) NOT NULL DEFAULT 'public',
  investment_preferences_visibility VARCHAR(16) NOT NULL DEFAULT 'followers',
  achievements_visibility VARCHAR(16) NOT NULL DEFAULT 'public',
  FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS real_name_verifications (
  user_id VARCHAR(64) PRIMARY KEY,
  status VARCHAR(32) NOT NULL DEFAULT 'not_submitted',
  legal_name VARCHAR(32),
  id_number VARCHAR(32),
  face_verified TINYINT(1) NOT NULL DEFAULT 0,
  submitted_at DATETIME,
  reviewed_at DATETIME,
  rejection_reason VARCHAR(255),
  FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS professional_verifications (
  user_id VARCHAR(64) PRIMARY KEY,
  status VARCHAR(32) NOT NULL DEFAULT 'not_submitted',
  reviewed_at DATETIME,
  rejection_reason VARCHAR(255),
  verified_by VARCHAR(64),
  FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS professional_documents (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id VARCHAR(64) NOT NULL,
  doc_type VARCHAR(64) NOT NULL,
  file_name VARCHAR(128) NOT NULL,
  file_url VARCHAR(512) NOT NULL,
  uploaded_at DATETIME NOT NULL,
  FOREIGN KEY (user_id) REFERENCES users(id),
  INDEX idx_prof_doc_user (user_id)
);

CREATE TABLE IF NOT EXISTS suitability_assessments (
  user_id VARCHAR(64) PRIMARY KEY,
  completed TINYINT(1) NOT NULL DEFAULT 0,
  risk_level VARCHAR(8),
  score INT NOT NULL DEFAULT 0,
  answers JSON NOT NULL,
  submitted_at DATETIME,
  FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS forum_boards (
  id VARCHAR(64) PRIMARY KEY,
  slug VARCHAR(64) NOT NULL UNIQUE,
  name VARCHAR(64) NOT NULL,
  description VARCHAR(300) NOT NULL,
  category VARCHAR(32) NOT NULL,
  market VARCHAR(32),
  parent_id VARCHAR(64),
  sort_order INT NOT NULL DEFAULT 0,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  created_at DATETIME NOT NULL,
  updated_at DATETIME NOT NULL,
  INDEX idx_board_category_sort (category, sort_order),
  FOREIGN KEY (parent_id) REFERENCES forum_boards(id)
);

CREATE TABLE IF NOT EXISTS posts (
  id VARCHAR(64) PRIMARY KEY,
  board_id VARCHAR(64) NOT NULL,
  author_id VARCHAR(64) NOT NULL,
  title VARCHAR(120) NOT NULL,
  content TEXT NOT NULL,
  post_type VARCHAR(16) NOT NULL DEFAULT 'normal',
  stock_codes JSON NOT NULL,
  image_urls JSON NOT NULL,
  created_at DATETIME NOT NULL,
  updated_at DATETIME NOT NULL,
  FOREIGN KEY (board_id) REFERENCES forum_boards(id),
  FOREIGN KEY (author_id) REFERENCES users(id),
  INDEX idx_post_board_time (board_id, created_at),
  FULLTEXT INDEX idx_post_fulltext (title, content)
);

CREATE TABLE IF NOT EXISTS comments (
  id VARCHAR(64) PRIMARY KEY,
  post_id VARCHAR(64) NOT NULL,
  author_id VARCHAR(64) NOT NULL,
  content TEXT NOT NULL,
  parent_comment_id VARCHAR(64),
  created_at DATETIME NOT NULL,
  updated_at DATETIME NOT NULL,
  FOREIGN KEY (post_id) REFERENCES posts(id),
  FOREIGN KEY (author_id) REFERENCES users(id),
  FOREIGN KEY (parent_comment_id) REFERENCES comments(id),
  INDEX idx_comment_post_time (post_id, created_at)
);

CREATE TABLE IF NOT EXISTS post_likes (
  post_id VARCHAR(64) NOT NULL,
  user_id VARCHAR(64) NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (post_id, user_id),
  FOREIGN KEY (post_id) REFERENCES posts(id),
  FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS post_favorites (
  post_id VARCHAR(64) NOT NULL,
  user_id VARCHAR(64) NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (post_id, user_id),
  FOREIGN KEY (post_id) REFERENCES posts(id),
  FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS user_follows (
  follower_id VARCHAR(64) NOT NULL,
  followee_id VARCHAR(64) NOT NULL,
  followed_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (follower_id, followee_id),
  FOREIGN KEY (follower_id) REFERENCES users(id),
  FOREIGN KEY (followee_id) REFERENCES users(id),
  INDEX idx_followee (followee_id)
);
