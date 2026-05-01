CREATE TABLE USERS (
    User_ID NUMBER PRIMARY KEY,
    Name VARCHAR2(50),
    Email VARCHAR2(50) UNIQUE,
    Phone VARCHAR2(15),
    Password VARCHAR2(50)
);
CREATE TABLE CATEGORY (
    Category_ID NUMBER PRIMARY KEY,
    Category_Name VARCHAR2(50)
);
CREATE TABLE STATUS (
    Status_ID NUMBER PRIMARY KEY,
    Status_Name VARCHAR2(20)
);
CREATE TABLE OFFICER (
    Officer_ID NUMBER PRIMARY KEY,
    Name VARCHAR2(50),
    Department VARCHAR2(50),
    Phone VARCHAR2(15)
);
CREATE TABLE COMPLAINT (
    Complaint_ID NUMBER PRIMARY KEY,
    User_ID NUMBER,
    Category_ID NUMBER,
    Status_ID NUMBER,
    Description VARCHAR2(200),
    Date_Reported DATE,
    Priority VARCHAR2(10),

    FOREIGN KEY (User_ID) REFERENCES USERS(User_ID),
    FOREIGN KEY (Category_ID) REFERENCES CATEGORY(Category_ID),
    FOREIGN KEY (Status_ID) REFERENCES STATUS(Status_ID)
);
CREATE TABLE ADMIN (
    Admin_ID NUMBER PRIMARY KEY,
    Name VARCHAR2(50),
    Email VARCHAR2(50),
    Password VARCHAR2(50)
);
CREATE TABLE ASSIGNMENT (
    Assign_ID NUMBER PRIMARY KEY,
    Complaint_ID NUMBER,
    Officer_ID NUMBER,
    Assign_Date DATE,

    FOREIGN KEY (Complaint_ID) REFERENCES COMPLAINT(Complaint_ID),
    FOREIGN KEY (Officer_ID) REFERENCES OFFICER(Officer_ID)
);
CREATE TABLE FEEDBACK (
    Feedback_ID NUMBER PRIMARY KEY,
    User_ID NUMBER,
    Rating NUMBER,
    Comments VARCHAR2(200),

    FOREIGN KEY (User_ID) REFERENCES USERS(User_ID)
);
INSERT INTO CATEGORY VALUES (1, 'Harassment');
INSERT INTO CATEGORY VALUES (2, 'Unsafe Area');
INSERT INTO CATEGORY VALUES (3, 'Stalking');,
commit;
select * from complaint;
INSERT INTO STATUS VALUES (1, 'Pending');
INSERT INTO STATUS VALUES (2, 'In Progress');
INSERT INTO STATUS VALUES (3, 'Resolved');
commit;
select * from status;
INSERT INTO USERS VALUES (1, 'Anshika', 'a@gmail.com', '9999999991', '123');
INSERT INTO USERS VALUES (2, 'Taashvi', 't@gmail.com', '9999999993', 'taash123');
INSERT INTO USERS VALUES (3, 'Minkal', 'm@gmail.com', '9999999994', 'mink456');
commit;
select * from users;
INSERT INTO OFFICER VALUES (1, 'Inspector Raj', 'Safety', '9999999999');
INSERT INTO OFFICER VALUES (2, 'Officer Neha', 'Security', '8888888888');
INSERT INTO OFFICER VALUES (3, 'Officer Aman', 'Patrol', '7777777777');
commit;
select * from officer;
INSERT INTO COMPLAINT VALUES 
(101, 1, 1, 1, 'Harassment near hostel', SYSDATE, 'High');
INSERT INTO COMPLAINT VALUES 
(102, 2, 2, 1, 'Unsafe street at night', SYSDATE, 'Medium');
INSERT INTO COMPLAINT VALUES 
(103, 3, 3, 1, 'Stalking issue in campus', SYSDATE, 'High');
commit;
select * from complaint;
INSERT INTO ASSIGNMENT VALUES (1, 101, 1, SYSDATE);
INSERT INTO ASSIGNMENT VALUES (2, 102, 2, SYSDATE);
commit;
select * from assignment;
INSERT INTO FEEDBACK VALUES (1, 1, 5, 'Quick response');
INSERT INTO FEEDBACK VALUES (2, 2, 4, 'Good support');
commit;
select * from feedback;
INSERT INTO ADMIN VALUES (1, 'Admin1', 'admin@gmail.com', 'admin123');
commit;
select * from admin;
SELECT u.Name, c.Description, cat.Category_Name, s.Status_Name
FROM COMPLAINT c
JOIN USERS u ON c.User_ID = u.User_ID
JOIN CATEGORY cat ON c.Category_ID = cat.Category_ID
JOIN STATUS s ON c.Status_ID = s.Status_ID;
SELECT COUNT(*) AS Total_Complaints FROM COMPLAINT;
SELECT cat.Category_Name, COUNT(*) AS Total
FROM COMPLAINT c
JOIN CATEGORY cat ON c.Category_ID = cat.Category_ID
GROUP BY cat.Category_Name;
SELECT * FROM COMPLAINT
WHERE Priority = 'High';
SELECT c.Complaint_ID, o.Name AS Officer_Name
FROM ASSIGNMENT a
JOIN COMPLAINT c ON a.Complaint_ID = c.Complaint_ID
JOIN OFFICER o ON a.Officer_ID = o.Officer_ID;
CREATE OR REPLACE PROCEDURE assign_complaint(
    cid NUMBER,
    oid NUMBER
)
IS
BEGIN
    INSERT INTO ASSIGNMENT 
    VALUES (10, cid, oid, SYSDATE);
END;
/
BEGIN
    assign_complaint(103, 3);
END;
/
SELECT * FROM ASSIGNMENT;
CREATE OR REPLACE TRIGGER update_status
AFTER INSERT ON ASSIGNMENT
FOR EACH ROW
BEGIN
    UPDATE COMPLAINT
    SET Status_ID = 2
    WHERE Complaint_ID = :NEW.Complaint_ID;
END;
/
INSERT INTO ASSIGNMENT VALUES (20, 103, 2, SYSDATE);
SELECT Complaint_ID, Status_ID FROM COMPLAINT;
CREATE OR REPLACE FUNCTION total_complaints
RETURN NUMBER
IS
    c NUMBER;
BEGIN
    SELECT COUNT(*) INTO c FROM COMPLAINT;
    RETURN c;
END;
/
SELECT total_complaints FROM dual;

select * from complaint;
SELECT table_name FROM user_tables;
select * from complaint;
ALTER USER system IDENTIFIED BY 1234;
ALTER USER system IDENTIFIED BY 1234 CONTAINER=ALL;