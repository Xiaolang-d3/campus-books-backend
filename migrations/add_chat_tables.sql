-- 创建聊天会话表
CREATE TABLE IF NOT EXISTS `chat_session` (
  `id` bigint NOT NULL,
  `user_id` bigint NOT NULL COMMENT '用户ID',
  `title` varchar(200) DEFAULT '新对话' COMMENT '会话标题',
  `message_count` int DEFAULT 0 COMMENT '消息数量',
  `last_message_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '最后消息时间',
  `addtime` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_last_message_time` (`last_message_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='AI聊天会话表';

-- 创建聊天消息表
CREATE TABLE IF NOT EXISTS `chat_message` (
  `id` bigint NOT NULL,
  `session_id` bigint NOT NULL COMMENT '会话ID',
  `role` varchar(20) NOT NULL COMMENT '角色：user/assistant',
  `content` text NOT NULL COMMENT '消息内容',
  `content_type` varchar(20) DEFAULT 'text' COMMENT '内容类型：text/book_card/book_list',
  `extra_data` text COMMENT '元数据（JSON格式）',
  `addtime` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_session_id` (`session_id`),
  KEY `idx_addtime` (`addtime`),
  CONSTRAINT `fk_chat_message_session` FOREIGN KEY (`session_id`) REFERENCES `chat_session` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='AI聊天消息表';
