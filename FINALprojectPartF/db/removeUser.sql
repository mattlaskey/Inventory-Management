DELIMITER //
CREATE PROCEDURE removeUser(IN uidToDelete INT,IN currentUid INT)
BEGIN

    DECLARE checkAdmin BOOLEAN;

    SELECT admin
    INTO checkAdmin
    FROM users
    WHERE userId = currentUid;
    
    IF(checkAdmin = true) THEN
        DELETE FROM users
        WHERE userId = uidToDelete;
        
        IF(ROW_COUNT() = 0) THEN
        SIGNAL SQLSTATE '52711'
            SET MESSAGE_TEXT = 'Unable to delete the user.';
        END IF;
    ELSE
        SIGNAL SQLSTATE '52711'
            SET MESSAGE_TEXT = 'Access Denied.';
    END IF;

END //
DELIMITER ;
