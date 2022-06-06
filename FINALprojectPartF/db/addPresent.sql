DELIMITER //
DROP PROCEDURE IF EXISTS addPresent;

CREATE PROCEDURE addPresent (IN uId INT, IN pName VARCHAR(45), IN pDesc VARCHAR(255), IN pPrice DOUBLE(15, 2))
BEGIN
    INSERT INTO presents (presentName, presentDesc, presentPrice, userId) VALUES (pName, pDesc, pPrice, uId);

    IF (ROW_COUNT() = 0) THEN
      SIGNAL SQLSTATE '52711'
        SET MESSAGE_TEXT = 'Unable to create the present.';
    END IF;

    SELECT LAST_INSERT_ID(); 

END //
DELIMITER ;
