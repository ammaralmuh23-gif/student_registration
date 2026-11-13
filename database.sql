CREATE DATABASE IF NOT EXISTS student_registration CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE student_registration;

-- 1. جدول الطلاب المتقدمين
CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    birth_date DATE NOT NULL,
    address TEXT NOT NULL,
    phone VARCHAR(20) NOT NULL,
    grade VARCHAR(50) NOT NULL,
    status ENUM('pending', 'accepted', 'rejected') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. جدول المديرين
CREATE TABLE IF NOT EXISTS admins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

-- إضافة حساب المدير الافتراضي (admin / admin123)
INSERT IGNORE INTO admins (username, password) VALUES ('admin', 'admin123');