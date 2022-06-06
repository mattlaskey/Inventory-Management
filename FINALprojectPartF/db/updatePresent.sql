DELIMITER //
DROP PROCEDURE IF EXISTS updatePresent;

CREATE PROCEDURE updatePresent(IN pid INT, IN pName VARCHAR(45), IN pDesc VARCHAR(255), IN pPrice DOUBLE(15, 2), IN uid INT)
BEGIN

    DECLARE checkUser INT;
    DECLARE checkAdmin BOOLEAN;
    
    SELECT userId
    INTO checkUser
    FROM presents
    WHERE presentId = pid;

    SELECT admin
    INTO checkAdmin
    FROM users
    WHERE userId = uid;
    
    IF (checkUser = uid OR checkAdmin = true) THEN
        UPDATE presents
        SET presentName = pName, presentDesc = pDesc, presentPrice = pPrice
        WHERE presentId = pid;
        
        IF(ROW_COUNT() = 0) THEN
        SIGNAL SQLSTATE '52711'
            SET MESSAGE_TEXT = 'Unable to update the present.';
        END IF;
    ELSE
        SIGNAL SQLSTATE '52711'
            SET MESSAGE_TEXT = 'Must be an admin or the user associated with this present.';
    END IF;

END //
DELIMITER ;