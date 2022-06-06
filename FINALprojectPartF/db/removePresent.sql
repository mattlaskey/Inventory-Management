DELIMITER //
CREATE PROCEDURE removePresent(IN pid INT, IN uid INT)
BEGIN

    DECLARE checkUser INT;
    DECLARE checkAdmin BOOLEAN;

    SELECT admin
    INTO checkAdmin
    FROM users
    WHERE userId = uid;
    
    SELECT userId
    INTO checkUser
    FROM presents
    WHERE presentId = pid;
    
    IF(checkUser = uid OR checkAdmin = true) THEN
        DELETE FROM presents
        WHERE presentId = pid;
        
        IF(ROW_COUNT() = 0) THEN
        SIGNAL SQLSTATE '52711'
            SET MESSAGE_TEXT = 'Unable to delete the present.';
        END IF;
    ELSE
        SIGNAL SQLSTATE '52711'
            SET MESSAGE_TEXT = 'Must be an admin or the user associated with this present.';
    END IF;

END //
DELIMITER ;
